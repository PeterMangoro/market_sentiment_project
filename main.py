from database.create_db import create_database
from database.insert_stocks import insert_stock_data

def main():
    # Create the database and tables
    create_database()
    # Insert stock data into the database
    # insert_stock_data()

if __name__ == "__main__":
    main()