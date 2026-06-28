class Category:
    def __init__(self, name):
        self.name = name
        self.ledger = []

    def deposit(self, amount, description=""):
        self.ledger.append({"amount": amount, "description": description})

    def withdraw(self, amount, description=""):
        if self.check_funds(amount):
            self.ledger.append({"amount": -amount, "description": description})
            return True
        return False

    def get_balance(self):
        return sum(item["amount"] for item in self.ledger)

    def transfer(self, amount, category):
        if self.check_funds(amount):
            self.withdraw(amount, f"Transfer to {category.name}")
            category.deposit(amount, f"Transfer from {self.name}")
            return True
        return False

    def check_funds(self, amount):
        return amount <= self.get_balance()

    def __str__(self):
        title = f"{self.name}".center(30, "*")
        items = ""
        for item in self.ledger:
            desc = f"{item['description'][:23]:<23}"
            amt = f"{item['amount']:>7.2f}"
            items += f"{desc}{amt}\n"
        total = f"Total: {self.get_balance():.2f}"
        return f"{title}\n{items}{total}"


def create_spend_chart(categories):
    # Calculate withdrawals per category and total withdrawals
    withdrawals = []
    for category in categories:
        spent = sum(-item["amount"] for item in category.ledger if item["amount"] < 0)
        withdrawals.append(spent)
    
    total_spent = sum(withdrawals)
    
    # Calculate percentages rounded down to the nearest 10
    percentages = []
    for spent in withdrawals:
        if total_spent > 0:
            percentages.append(int((spent / total_spent) * 100 // 10) * 10)
        else:
            percentages.append(0)

    # Build the chart string line by line
    chart = "Percentage spent by category\n"
    for i in range(100, -1, -1,):
        chart += f"{i:>3}| "
        for percent in percentages:
            if percent >= i:
                chart += "o  "
            else:
                chart += "   "
        chart += "\n"

    # Add the horizontal line separator
    chart += "    " + "-" * (len(categories) * 3 + 1) + "\n"

    # Find the longest category name to handle vertical alignment
    max_len = max(len(category.name) for category in categories)
    names = [category.name.ljust(max_len) for category in categories]

    # Write category names vertically below the bars
    for i in range(max_len):
        chart += "     "
        for name in names:
            chart += f"{name[i]}  "
        if i < max_len - 1:
            chart += "\n"

    return chart
