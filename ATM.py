import pandas as pd


class BankAccount:
    def __init__(self, account_holder, card_number, pin, balance=0):
        self.data = pd.Series({
            "Account Holder": account_holder,
            "Card Number": card_number,
            "PIN": pin,
            "Balance": balance
        })

    def check_pin(self, pin):
        return self.data["PIN"] == pin

    def deposit(self, amount):
        if amount > 0:
            self.data["Balance"] += amount
            print(f"\n₹{amount} deposited successfully.")
        else:
            print("\nInvalid deposit amount.")

    def withdraw(self, amount):
        if amount <= 0:
            print("\nInvalid withdrawal amount.")
        elif amount > self.data["Balance"]:
            print("\nInsufficient balance.")
        else:
            self.data["Balance"] -= amount
            print(f"\n₹{amount} withdrawn successfully.")

    def check_balance(self):
        print(f"\nAvailable Balance: ₹{self.data['Balance']}")

    def display_details(self):
        print("\n--- Account Details ---")
        print(f"Account Holder : {self.data['Account Holder']}")
        print(f"Card Number    : {self.data['Card Number']}")
        print(f"Balance        : ₹{self.data['Balance']}")
        print("------------------------")


class ATM:
    def __init__(self):
        self.accounts = {}
        self.current_user = None

    def add_account(self, account):
        card_number = account.data["Card Number"]
        self.accounts[card_number] = account

    def login(self):
        card_number = input("\nEnter Card Number: ")
        pin = input("Enter PIN: ")

        account = self.accounts.get(card_number)

        if account and account.check_pin(pin):
            self.current_user = account
            print("\nLogin Successful!")
            return True

        print("\nInvalid Card Number or PIN.")
        return False

    def logout(self):
        self.current_user = None
        print("\nLogged Out Successfully.")

    def menu(self):
        while True:
            print("\n===== ATM MENU =====")
            print("1. Check Balance")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Account Details")
            print("5. Logout")

            choice = input("\nEnter Choice: ")

            if choice == "1":
                self.current_user.check_balance()

            elif choice == "2":
                amount = float(input("Enter Amount to Deposit: "))
                self.current_user.deposit(amount)

            elif choice == "3":
                amount = float(input("Enter Amount to Withdraw: "))
                self.current_user.withdraw(amount)

            elif choice == "4":
                self.current_user.display_details()

            elif choice == "5":
                self.logout()
                break

            else:
                print("\nInvalid Choice.")


def main():
    atm = ATM()

    account1 = BankAccount(
        account_holder="Santosh Kumar",
        card_number="123456789012",
        pin="1234",
        balance=10000
    )

    account2 = BankAccount(
        account_holder="Ramy",
        card_number="987654321098",
        pin="5678",
        balance=5000
    )

    atm.add_account(account1)
    atm.add_account(account2)

    print("===== ATM SYSTEM =====")

    if atm.login():
        atm.menu()


if __name__ == "__main__":
    main()
