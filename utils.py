def calculate_settlement(transactions):
    settlement_amount = 0.0
    for txn in transactions:
        amount = float(txn["amount"])
        if txn["type"] == "PURCHASE":
            settlement_amount += amount
        elif txn["type"] == "REFUND":
            settlement_amount -= amount
    return settlement_amount
