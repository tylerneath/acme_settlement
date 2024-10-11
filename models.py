# models.py
from pydantic import BaseModel, Field
from datetime import date


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"


class SettlementRequest(BaseModel):
    merchant_id: str = Field(..., description="The unique identifier of the merchant")
    transactions_date: date = Field(
        ...,
        description="The date for which to retrieve transactions, in YYYY-MM-DD format",
    )


class TransactionsRequest(SettlementRequest):
    pass
