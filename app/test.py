# import os.path
# import time
from MAIN import *
from app.initApi import *

holdings = (getHoldings(client))
print(type(val["tickers"]["BNBBTC"]))

# print(holdings["BTC"]["free"])
# print(val["decimals"])
# #percentage_ammount(totoal_btc, price, percentage):
# # time.sleep(2)
# # print(percentage_ammount(holdings["BTC"]["free"], 0.0013781, 50, val["assetDecimals"]))
# #
# # print(val["coins"]["BNBBTC"])
#
# print(int(val["buttonPercentage"][0]))
#
# print(val["coins"])
#
# print("##########")

# print(client.get_all_tickers())
# print(client.get_products())

# print(val["coins"])
get_tether(client)

orders = (client.get_all_orders(symbol="BNBBTC"))

orderList = list()

# for i, val in enumerate(val["coins"]):
#     orders = (client.get_all_orders(symbol=val))
#
#     try:
#         if len(orders) > 1:
#             orderList.insert(0, orders)
#             print("insert " + str(val))
#     except IndexError:
#         print("fail")
#
#
# with open("trades.txt", "w") as f:
#             f.write(str(orderList))


# print(getOrders(client, "DASHBTC"))

# depth = (client.get_order_book(symbol='BNBBTC'))
# asks = list()
# bids = list()
# for i in enumerate(depth["asks"]):
#     print(str(i[1][0]) + " " + str(i[1][1]))
#     line = [str(i[1][0]), str(i[1][1])]
#     asks.append(line)
#
# for i in enumerate(depth["bids"]):
#     print(str(i[1][0]) + " " + str(i[1][1]))
#     line = [str(i[1][0]), str(i[1][1])]
#     bids.append(line)
#
# mydct = {"asks": asks, "bids": bids}
#
# print(mydct)


price = '{number:.{digits}f}'.format(number=val["coins"]["BNBBTC"]["minQty"], digits=8)

# print(client.get_ticker(symbol="BNBBTC"))
#
# time.sleep(5)
#
# print(val["ticker"]["BNBBTC"])
# print(type(val["tickers"]["BNBBTC"]))
#
# # while True:
# #     # print(val["tickers"]["BNBBTC"]["quoteVolume"])
# #     time.sleep(1)
# #     print((val["tickers"]["BNBBTC"]))
#
# print(val["coins"]["BNBBTC"])
# print(val["coin"])
#
# print(val["accHoldings"][val["coin"]]["free"])


my_list = ["item1", 1337, ["list1", "list2"]]

for i,_ in enumerate(my_list):
    print("i:")
    print(str(i))
    print("")
    print("i 0, i1:")
    print(str(i[0]))
    print(str(i[1]))
