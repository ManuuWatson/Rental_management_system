def generate_report(report_type):
    if report_type == "overview":
        with open(USER_FILE, "r") as file:
            users = json.load(file)
        return users
    elif report_type == "transactions":
        with open(TRANSACTION_FILE, "r") as file:
            transactions = json.load(file)
        return transactions
