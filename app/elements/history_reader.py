import pandas as pd
from datetime import date, datetime
from app.helpers import resource_path, check_file_exists, date_to_milliseconds
import dateparser
import pytz

# Entrypoint
def exec_df():
    print("lul")
    df = parse_history_file("TradeHistory.xlsx")
    print("df", df)
    iterate_df_rows(df)


# class parser:
def parse_history_file(filename="TradeHistory.xlsx"):
    """Read a xlsx file and return it's data as a pandas dataframe."""
    history_file_path = resource_path(filename)

    xls = pd.ExcelFile(history_file_path)
    return xls.parse("sheet1")
    # print("returning df", df)
    # return df

def iterate_df_rows(df):
    traded_pairs = set()
    trade_list = list()

    for _, row in df.iterrows():

        trade = parse_excel_row(row)
        trade_list.append(trade)
        traded_pairs.add(str(row["Market"]))

    print("traded paris:", traded_pairs)
    print("TRADE LIST:", trade_list)
    return traded_pairs

def trade_to_excel(trade):
    """Format a historical trade to fint into Binance generated trade history
    spreadsheet."""
    # TODO: Implement
    pass

def parse_excel_row(row) -> dict():
    """Receives a row from a Binance TradeHistory xlsx file. Returns a dictionary
    containing the trade information."""

    unix_date = date_to_milliseconds(row["Date(UTC)"])

    isBuyer = True

    if row["Type"] == "SELL":
        isBuyer = False

    trade = {"time": unix_date, "isBuyer": isBuyer, "symbol": row["Market"], "price": row["Price"], "executedQty": row["Amount"],
             "qty": row["Amount"], "quoteQty": row["Total"], "commission": row["Fee"], "commissionAsset": row["Fee Coin"],
             "id": 0000, "orderId": 0000, "isMaker": True, "isBestMatch": True}

    return trade