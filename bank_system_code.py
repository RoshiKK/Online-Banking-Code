import datetime
from abc import ABC,abstractmethod

class Account(ABC):
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance
        self.transaction_history = []

    @abstractmethod
    def deposit(self):
        pass

    @abstractmethod
    def withdraw(self):
        pass

    def balance_enquiry(self):
        return self.balance
    #method for record transaction history
    def add_transaction(self, transaction_type, amount):
        transaction = {
            "timestamp": datetime.datetime.now(),# transaction date and time
            "type": transaction_type,
            "amount": amount
        }
        self.transaction_history.append(transaction)
    #method for getting transaction history
    def get_transaction_history(self):
        return self.transaction_history

    #loading transaction history from file
    def load_transaction_history_from_file(self, lines):
        transaction_history_started = False
        acc_match = False
        for line in lines:
            if line.startswith("Account Number:") and not (self.account_number == line.strip().split(": ")[1]):
                acc_match = False # Transaction history is not of req:d account
            elif line.startswith("Account Number:") and (self.account_number == line.strip().split(": ")[1]):
                acc_match = True #transaction history is of req:d account
            if line.startswith("Transaction History:"):
                transaction_history_started = True
            elif acc_match and transaction_history_started and line.strip() != "":
                transaction_parts = line.strip().split(" - ")
                if len(transaction_parts) >= 2:
                    timestamp = datetime.datetime.strptime(transaction_parts[0], "%Y-%m-%d %H:%M:%S")
                    transaction_type, amount = transaction_parts[1].split(": ")
                    amount = float(amount)
                    self.add_transaction(transaction_type, amount)


class CheckingAccount(Account):
    def __init__(self, account_number, balance=0, credit_limit=0, overdraft_fee=0):
        super().__init__(account_number, balance)
        self.credit_limit = credit_limit
        self.overdraft_fee = overdraft_fee

    def deposit(self, amount):
        self.balance += amount  # adding deposit amount in balance
        self.add_transaction("Deposit", amount)
        print("Deposit successful!")
        print(f"Updated balance: {self.balance_enquiry()}")

    def withdraw(self, amount):
        if self.balance + self.credit_limit >= amount:  # checking is withdrawl amount less than account balance plus credit limit
            if self.balance >= amount:  # Checking is amount to be withdraw greater than balance
                self.balance -= amount  # subtracting withdraw amount from account balance
                self.add_transaction("Withdrawal", -amount)  # Saving transaction history
            else:  # if balance is less than amount to be withdraw than customer can withdraw from credit limit
                overdraft_amount = amount - self.balance
                self.balance = 0
                self.balance -= overdraft_amount  # subtracting credit limit amount which was withdraw from account balance
                self.balance -= self.overdraft_fee  # subtracting credit_limit fees from account balance
                self.add_transaction("Withdrawal (Overdraft)", -amount)  # saving transaction history
            print("Withdrawal successful!")
            print(f"Updated balance: {self.balance_enquiry()}")
        else:  # if withdraw amount is greater than balance plus credit limit
            raise ValueError("Insufficient balance with credit limit.")

    def __str__(self):
        return f"Checking Account #{self.account_number}"


class SavingAccount(Account):
    def __init__(self, account_number, balance, interest_rate=10):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate

    def deposit(self, amount):
        self.balance += amount #adding deposit amount in balance
        self.add_transaction("Deposit", amount)
        print("Deposit successful!")
        print(f"Updated balance: {self.balance_enquiry()}")

    def withdraw(self, amount):
        if self.balance >= amount:# Checking is amount to be withdraw greater than balance
            self.balance -= amount #subracting withdrawl amount from balance
            self.add_transaction("Withdrawal", -amount)# Saving transaction history
            print("Withdrawal successful!")
            print(f"Updated balance: {self.balance_enquiry()}")
        else:#if amount to be withdraw is less than balance
            raise ValueError("Insufficient balance.")

    # calculating how much interest you would be given  in one month in your account balance
    def calculate_monthly_interest(self):
        monthly_interest = self.balance * (self.interest_rate / 100) / 12
        return monthly_interest

    # Adding above calculated interest in account balance
    def credit_interest(self):
        monthly_interest = self.calculate_monthly_interest()
        self.balance += monthly_interest
        self.add_transaction("Interest Credit", monthly_interest)
        return self.balance

    def __str__(self):
        return f"Savings Account #{self.account_number}"


class LoanAccount(Account):
    def __init__(self, account_number, principal_amount, interest_rate=10, loan_duration=12):
        super().__init__(account_number)
        self.principal_amount = principal_amount # the amount of the loan provided by the banker to the cutomer
        self.interest_rate = interest_rate
        self.loan_duration = loan_duration
        self.monthly_payment = self.calculate_monthly_payment()


    def deposit(self, amount):
        print('Sorry! you are not allowed to deposit in Loan account.')

    def withdraw(self, amount):
        print('Sorry! You are not allowed to withdraw from Loan account')

    #calculating montly payment of loan that customer will pay
    def calculate_monthly_payment(self):
        monthly_interest_rate = self.interest_rate / 100 / 12
        num_payments = self.loan_duration
        annuity_factor = (monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments) / (
                (1 + monthly_interest_rate) ** num_payments)# calculating how much money will be paid out in the future at specific points of time under an annuity agreement
        monthly_payment = self.principal_amount * annuity_factor
        return monthly_payment

    #method for paying loan installment
    def pay_installment(self):
        interest_payment = self.balance * (self.interest_rate / 100) / 12
        principal_payment = self.monthly_payment - interest_payment
        self.balance -= principal_payment
        self.add_transaction("Loan Installment", -principal_payment)
        return principal_payment

    def get_remaining_balance(self):
        return self.balance

    def __str__(self):
        return f"Loan Account #{self.account_number}"


class Customer:
    def __init__(self, username, password, first_name, last_name, address):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.accounts = []
    #creating customer account
    def create_account(self, account_type, account_number, **kwargs):
        account = {
            "Checking": CheckingAccount,
            "Savings": SavingAccount,
            "Loan": LoanAccount
        }.get(account_type, None)

        if account: #checking is customer input valid account type or not
            new_account = account(account_number, **kwargs)
            self.accounts.append(new_account)
            print("Account created successfully!")
        else:# customer input invalid account type
            raise ValueError("Invalid account type.")

    def __str__(self):
        return f"Customer: {self.first_name} {self.last_name}"

    #searching and getting account by account number
    def get_account_by_number(self, account_number):
        for account in self.accounts:
            if account.account_number == account_number:
                return account
        return None #if account number not exit

    #printing customer detail
    def view_customer_details(self):
        print(f"\n--- Customer Details ---")
        print(f"Username: {self.username}")
        print(f"Name: {self.first_name} {self.last_name}")
        print(f"Address: {self.address}")
        # printing customer's accounts details
        print(f"\n--- Account Details ---")
        for account in self.accounts:
            print(f"Account Type: {type(account).__name__}")
            print(f"Account Number: {account.account_number}")
            print(f"Balance: {account.balance_enquiry()}")
            #printing customer's transacton history
            print("Transaction History:")
            transaction_history = account.get_transaction_history()
            for transaction in transaction_history:
                timestamp = transaction['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                transaction_type = transaction['type']
                amount = transaction['amount']
                print(f"{timestamp} - {transaction_type}: {amount}")
            print()

class BankingSystem:
    def __init__(self):
        self.customers = []

    def get_customer_by_username(self, username):
        for customer in self.customers:
            if customer.username == username:
                return customer
        return None

    # method for loading all customers detail from a single file
    @staticmethod
    def load_customers_from_file(filename):
        customers = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    customer_data = line.strip().split(",")
                    username, password, first_name, last_name, address = customer_data
                    customer = Customer(username, password, first_name, last_name, address)
                    customers.append(customer)
        except FileNotFoundError: #if file not exit
            pass
        return customers
    # method saving all customer details in a single file
    @staticmethod
    def save_customers_to_file(customers, filename):
        try:
            with open(filename, 'w') as file:
                for customer in customers:
                    customer_data = [
                        customer.username,
                        customer.password,
                        customer.first_name,
                        customer.last_name,
                        customer.address
                    ]
                    line = ",".join(customer_data) + "\n"
                    file.write(line)
        except IOError:
            pass
    # saving each customer account details and transaction history in separate file
    @staticmethod
    def save_account_details_to_file(customers, directory):
        try:
            for customer in customers:
                filename = f"{customer.username}.txt"  # Unique file based on username
                with open(filename, 'w') as file:
                    file.write(f"Customer: {customer.first_name} {customer.last_name}\n")
                    for account in customer.accounts:
                        file.write(f"Account Type: {type(account).__name__}\n")
                        file.write(f"Account Number: {account.account_number}\n")
                        file.write(f"Balance: {account.balance_enquiry()}\n")
                        file.write("Transaction History:\n")
                        transaction_history = account.get_transaction_history()
                        for transaction in transaction_history:
                            timestamp = transaction['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                            transaction_type = transaction['type']
                            amount = transaction['amount']
                            file.write(f"{timestamp} - {transaction_type}: {amount}\n")
                        file.write("\n")
        except IOError:
            pass

    #loading each customer's account details and transaction history from file
    @staticmethod
    def load_account_details_from_file(customer):
        filename = f"{customer.username}.txt"  # Unique file based on username
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            account_details = {}
            current_account = None

            for line in lines:
                if line.startswith("Account Type:"):
                    account_type = line.strip().split(": ")[1]
                    account_details["account_type"] = account_type
                elif line.startswith("Account Number:"):
                    account_details["account_number"] = line.strip().split(": ")[1]
                elif line.startswith("Balance:"):
                    account_details["balance"] = float(line.strip().split(": ")[1])
                elif line.startswith("Transaction History:"):
                    if current_account:
                        customer.accounts.append(current_account)

                    account_type = account_details.get("account_type")
                    account_number = account_details.get("account_number")
                    balance = account_details.get("balance")

                    if account_type == "CheckingAccount":
                        current_account = CheckingAccount(account_number, balance)
                    elif account_type == "SavingAccount":
                        current_account = SavingAccount(account_number, balance)
                    elif account_type == "LoanAccount":
                        current_account = LoanAccount(account_number, balance, 0)  # Set initial balance to 0
                    else:
                        raise ValueError("Invalid account type.")

                    #calling load_transaction_history method from account class
                    current_account.load_transaction_history_from_file(lines)

            # Add the last account if it exists
            if current_account:
                customer.accounts.append(current_account)

        except IOError:
            pass

    # viewing cutomers detail
    def view_customer_details(self, username):
        customer = self.get_customer_by_username(username)
        if customer:#checking is customer exit or not
            customer.view_customer_details()
        else:#if customer not exit
            print("Customer not found.")
    #register customer
    def register_customer(self):
        print("\n--- Register Customer ---")
        username = input("Enter username: ")
        password = input("Enter password: ")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        address = input("Enter address: ")

        customer = Customer(username, password, first_name, last_name, address)
        print("Customer registered successfully!")
        self.customers.append(customer)

class BankingSystemCLI:
    def __init__(self, banking_system):
        self.banking_system = banking_system

    def run(self):
        print("***************Welcome to The NED Bank**************!")

        while True:
            print("\n--- Menu ---")
            print("1. Admin Login")
            print("2. Customer Login")
            print("3. Quit")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.admin_login()
            elif choice == "2":
                self.customer_login()
            elif choice == "3":
                print('\nThank You For Using Our Bank\nHave a Nice Day!')
                break
            else:
                print("Invalid choice. Try again.")

    def customer_login(self):
        print("\n--- Customer Login ---")
        username = input("Enter your username (or 'q' to go back): ")
        if username == "q":
            return

        password = input("Enter your password: ")

        customer = self.banking_system.get_customer_by_username(username)
        if customer and customer.username == username and customer.password == password:#checking is customer input correct credentials
            # Load the account details for the logged-in customer
            self.banking_system.load_account_details_from_file(customer)
            print(f"Welcome, {customer.first_name} {customer.last_name}!")

            while True:
                print("\n--- Menu ---")
                print("1. Create an account")
                print("2. Deposit")
                print("3. Withdraw")
                print("4. Balance Enquiry")
                print("5. View Customer Details")
                print("6. Logout")

                choice = input("Enter your choice: ")
                if choice == "1":
                    self.create_account(customer)
                elif choice == "2":
                    self.deposit(customer)
                elif choice == "3":
                    self.withdraw(customer)
                elif choice == "4":
                    self.balance_enquiry(customer)
                elif choice == "5":
                    self.view_customer_details(customer)
                elif choice == "6":
                    # Save account details to separate files in the "customer_files" directory
                    banking_system.save_account_details_to_file(banking_system.customers, "customer_files")
                    break
                else:
                    print("Invalid choice. Try again.")

        else: # if credentials are wrong
            print("Invalid username or password. Try again.")

    # taking input for creating new account
    def create_account(self, customer):
        print("\n--- Create Account ---")
        account_type = input("Enter the account type (Checking/Savings/Loan): ")
        account_number = input("Enter the account number: ")
        if account_type in ["Checking", "Savings", "Loan"]: # checking is account type valid
            kwargs = {}

            if account_type == "Checking": # taking input for creating checking account
                balance = float(input("Enter the initial balance: "))
                credit_limit = float(input("Enter the credit limit: "))
                overdraft_fee = float(input("Enter the overdraft fee: "))
                kwargs = {"balance": balance, "credit_limit": credit_limit, "overdraft_fee": overdraft_fee}

            elif account_type == "Savings":# taking input for creating saving account
                balance = float(input("Enter the initial balance: "))
                interest_rate = float(input("Enter the interest rate: "))
                kwargs = {"balance": balance, "interest_rate": interest_rate}

            elif account_type == "Loan":# taking input for creating loan account
                principal_amount = float(input("Enter the principal amount: "))
                interest_rate = float(input("Enter the interest rate: "))
                loan_duration = int(input("Enter the loan duration (in months): "))
                kwargs = {"principal_amount": principal_amount, "interest_rate": interest_rate, "loan_duration": loan_duration}

            # calling create account method from customer class
            customer.create_account(account_type, account_number, **kwargs)

        else:
            print("Invalid account type.")


    # taking input for deposit amount and calling deposit method from class account
    def deposit(self, customer):
        print("\n--- Deposit ---")
        account_number = input("Enter the account number: ")

        account = customer.get_account_by_number(account_number)
        if account:
            amount = float(input("Enter the deposit amount: "))
            account.deposit(amount)
        else:
            print("Account not found.")

    # taking input for withdraw amount and calling withdraw method from class account
    def withdraw(self, customer):
        print("\n--- Withdraw ---")
        account_number = input("Enter the account number: ")

        account = customer.get_account_by_number(account_number)
        if account:
            amount = float(input("Enter the withdrawal amount: "))

            try:
                account.withdraw(amount)
            except ValueError as e:
                print(str(e))
        else:
            print("Account not found.")

    # taking input for account number to check balance and calling balance enquiry method from class account
    def balance_enquiry(self, customer):
        print("\n--- Balance Enquiry ---")
        account_number = input("Enter the account number: ")

        account = customer.get_account_by_number(account_number)
        if account:
            balance = account.balance_enquiry()
            print(f"Account Balance: {balance}")
        else:
            print("Account not found.")

    # calling view_customer_details method from class Bank system
    def view_customer_details(self, customer):
        self.banking_system.view_customer_details(customer.username)

    def admin_login(self):
        print("\n--- Admin Login ---")
        username = input("Enter your username (or 'q' to go back): ")
        if username == "q":
            return

        password = input("Enter your password: ")

        # Perform admin authentication (e.g., check against admin credentials)
        if username == "neduet" and password == "cisd": # checking is admin credentials are correct or not
            print("Admin login successful!")

            while True:
                print("\n--- Admin Menu ---")
                print("1. Register Customer")
                print("2. View Customer Details")
                print("3. Quit")

                choice = input("Enter your choice: ")
                if choice == "1":
                    self.register_customer()
                elif choice == "2":
                    username = input("Enter the customer username: ")
                    customer = self.banking_system.get_customer_by_username(username)
                    if customer:
                        self.banking_system.load_account_details_from_file(customer)
                    self.banking_system.view_customer_details(username)
                elif choice == "3":
                    break
                else:
                    print("Invalid choice. Try again.")

        else:
            print("Invalid admin credentials. Try again.")
    #calling registe_customer method from customer class
    def register_customer(self):
        self.banking_system.register_customer()




# Create an instance of the BankingSystem
banking_system = BankingSystem()

# Load customers from a file
customers = banking_system.load_customers_from_file("customers.txt")
banking_system.customers = customers

# Register a customer
# banking_system.register_customer()

# Create an instance of the BankingSystemCLI
cli = BankingSystemCLI(banking_system)

# Run the CLI
cli.run()

# Save customers to a file
banking_system.save_customers_to_file(banking_system.customers, "customers.txt")
# Save account details to a file


