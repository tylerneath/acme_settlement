# main.py
from http.client import HTTP_PORT
from fastapi import FastAPI, HTTPException, logger
from exceptions import InvalidMerchantIDException
from models import HealthCheck, SettlementRequest, TransactionsRequest
from payments_client.acme_client import fetch_transactions
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

app = FastAPI()


PURCHASE = "PURCHASE"
REFUND = "REFUND"


@app.get("/")
def read_root():
    return {"message": "ACME Settlement Service running..."}


@app.get(
    "/health",
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.post("/settlement")
def get_settlement(request: SettlementRequest):
    """
        Returns the settlement amount for a given merchant and date.
        Params:
        - date: string 
        - merchant_id: string

        Returns:
        - merchant_id: string 
        - settlement_amount: int
        - date: string

        Raises:
        - HTTPException: 
            - 404 if no transactions are found for the specified merchant and date.
            - 502 if there is an error during processing or while fetching transactions.
    """
    try:
        # Retrieve merchant id and date from reqeust 
        merchant_id = request.merchant_id
        date = request.transactions_date

        # Fetch transactions for the given merchant and date
        transactions = fetch_transactions(merchant_id, date)
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found.")

        # Calculate the settlement amount
        settlement_amount = calculate_settlement(transactions)
        return {
            "merchant_id": merchant_id,
            "date": date,
            "settlement_amount": settlement_amount,
        }
    
    except InvalidMerchantIDException as e:
        raise HTTPException(
            status_code=404,
            detail=f"Merchant not found: {str(merchant_id)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to process settlement. Please retry. {str(e)}"
        )


@app.post("/transactions")
def get_transactions(request: TransactionsRequest):
    try:
        # Extract merchant_id and date from request body
        merchant_id = request.merchant_id
        date = request.transactions_date

        # Fetch transactions
        transactions = fetch_transactions(merchant_id, date)

        if not transactions:
            raise HTTPException(
                status_code=404, detail=f"No transactions found for the date {date}."
            )
        return transactions
    
    except InvalidMerchantIDException as e:
        raise HTTPException(
            status_code=404,
            detail=f"Merchant not found: {str(merchant_id)}"
        )

    except RetryError as e:
        original_exception = e.last_attempt.exception()
        raise HTTPException(
            status_code=502,
            detail=f"Failed to retrieve transactions after multiple attempts: {str(original_exception)}",
        )


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def calculate_settlement(transactions):
    settlement_amount = 0.0
    for txn in transactions:
        amount = float(txn["amount"])
        if txn["type"] == PURCHASE:
            settlement_amount += amount
        elif txn["type"] == REFUND:
            settlement_amount -= amount
    return settlement_amount
