import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential, wait_fixed

from exceptions import InvalidMerchantIDException

BASE_URL = "https://api-engine-dev.clerq.io/tech_assessment"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    reraise=True,
    retry=retry_if_exception_type((requests.HTTPError,)),  # Retry only for HTTPError
)
def fetch_transactions(merchant_id: str, date: str):
    """
        Fetch transactions for a given merchant within the given date range. The range accounts for all
        times within the 24hr period of a day. It retrices for up to 3 times in the case of an HTTP error that is
        1) not a exception concenrning an invalid merchant id 2) empty lists of transactions.

        Returns:
        - List[dict]: A list of transaction dictionaries if successful, or an empty list
        if no transactions are found.

        Raises:
        - InvalidMerchantIDException: If the merchant ID is invalid.
        - RuntimeE
    """
    url = f"{BASE_URL}/transactions/"
    start_of_day = f"{date}T00:00:00Z"
    end_of_day = f"{date}T23:59:59Z"
    params = {
        "merchant": merchant_id,
        "created_at__gte": start_of_day,
        "created_at__lt": end_of_day,
    }
    try:
        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 400:
            error_detail = response.json().get("merchant", [])
            if error_detail:
                # Raise InvalidMerchantIDException, this will NOT trigger a retry
                raise InvalidMerchantIDException(f"Invalid merchant ID: {merchant_id}")

        if response.status_code == 404:
            return []  # No transactions found, return an empty list

        response.raise_for_status()
        return response.json().get("results", [])

    except requests.HTTPError as e:
        raise RuntimeError(f"Failed to fetch transactions: {str(e)}")
