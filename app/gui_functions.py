# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Collection of functions that concern the gui."""


from PyQt5.QtCore import QSize, Qt, QVariant
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import QHeaderView, QPushButton, QTableWidgetItem

from app.charts import build_chart2
from app.colors import colors
from app.init import val
from app.table_items import CoinDelegate


def initial_values(self):
    """Set various values needed for further tasks."""
    self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
    self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

    self.limit_buy_label.setText("<span style='font-weight: bold; font-size: 12px;'>Buy " + val["coin"] + "</span>")
    self.limit_sell_label.setText("<span style='font-weight: bold; font-size: 12px;'>Sell " + val["coin"] + "</span>")

    # self.limit_coin_label_buy.setText("<span style='font-weight: bold; color: white;'>" + val["coin"] + "</span>")
    # self.limit_coin_label_sell.setText("<span style='font-weight: bold; color: white;'>" + val["coin"] + "</span>")

    # self.limit_buy_input.setText("kernoschmaus")
    self.limit_buy_input.setDecimals(val["decimals"])
    self.limit_buy_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

    self.limit_sell_input.setDecimals(val["decimals"])
    self.limit_sell_input.setSingleStep(float(val["coins"][val["pair"]]["tickSize"]))

    self.limit_buy_amount.setDecimals(val["assetDecimals"])
    self.limit_buy_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

    self.limit_sell_amount.setDecimals(val["assetDecimals"])
    self.limit_sell_amount.setSingleStep(float(val["coins"][val["pair"]]["minTrade"]))

    self.buy_asset.setText(val["coin"])
    self.sell_asset.setText(val["coin"])

    self.chart.setHtml(build_chart2(val["pair"], val["defaultTimeframe"]))
    self.chart.show()

    bids_header = self.bids_table.horizontalHeader()
    asks_header = self.asks_table.horizontalHeader()
    bids_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    bids_header.setSectionResizeMode(1, QHeaderView.Stretch)
    bids_header.setSectionResizeMode(2, QHeaderView.Stretch)

    asks_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    asks_header.setSectionResizeMode(1, QHeaderView.Stretch)
    asks_header.setSectionResizeMode(2, QHeaderView.Stretch)

    trades_header = self.tradeTable.horizontalHeader()
    trades_header.setSectionResizeMode(0, QHeaderView.Stretch)
    trades_header.setSectionResizeMode(1, QHeaderView.Stretch)


def filter_coinindex(self, text):
    """Hide every row in coin index that does not contain the user input."""
    self.coin_index.setSortingEnabled(False)
    row_count = self.coin_index.rowCount()

    if text != "":
        for i in range(row_count):

            if text.upper() not in str(self.coin_index.item(i, 1).text()):
                print("hide row: " + str(i))
                self.coin_index.hideRow(i)
            else:
                print("show")
                self.coin_index.showRow(i)
    else:
        print("show all row count: " + str(row_count))
        for j in range(row_count):
            self.coin_index.showRow(j)
        self.coin_index.setSortingEnabled(True)

    # print("procc")


def filter_confirmed(self):
    """Switch to the topmost coin of the coin index that is not hidden."""
    # check if input is empty
    if self.coinindex_filter.text() != "":
        # self.coin_index.setSortingEnabled(False)
        # test = self.coin_index.
        # print(str(test))

        # iterate through all rows
        for i in (range(self.coin_index.rowCount())):
            # skip the row if hidden
            if self.coin_index.isRowHidden(i):
                continue
            else:
                # return the first nonhidden row (might be inefficient)
                coin = self.coin_index.item(i, 1).text()
                # switch to that coin
                print(str(coin) + "   " + str(val["pair"]))

                if coin != val["pair"].replace("BTC", ""):
                    coinIndex = self.coin_selector.findText(coin)
                    self.coin_selector.setCurrentIndex(coinIndex)
                    self.change_pair()
                    # self.coin_index.setSortingEnabled(True)
                    return

                elif coin == val["pair"].replace("BTC", ""):
                    # self.coin_index.setSortingEnabled(True)
                    return


def build_coinindex(self):
    self.coin_index.setRowCount(0)
    print("setze delegate")
    self.coin_index.setItemDelegate(CoinDelegate(self))

    for pair in val["tickers"]:
        if "USDT" not in pair:
            coin = str(val["tickers"][pair]["symbol"]).replace("BTC", "")
            # print(str(holding))

            icon = QIcon("images/ico/" + coin + ".svg")

            icon_item = QTableWidgetItem()
            icon_item.setIcon(icon)

            # price_change = float(val["tickers"][pair]["priceChangePercent"])
            # if price_change > 0:
            #     operator = "+"
            # else:
            #     operator = ""

            last_price = QTableWidgetItem()
            last_price.setData(Qt.EditRole, QVariant(val["tickers"][pair]["lastPrice"]))

            price_change = QTableWidgetItem()
            price_change_value = float(val["tickers"][pair]["priceChangePercent"])
            price_change.setData(Qt.EditRole, QVariant(price_change_value))

            btc_volume = QTableWidgetItem()
            btc_volume.setData(Qt.EditRole, QVariant(round(float(val["tickers"][pair]["quoteVolume"]), 2)))

            # price_change.setData(Qt.DisplayRole, QVariant(str(val["tickers"][pair]["priceChangePercent"]) + "%"))

            self.coin_index.insertRow(0)
            self.coin_index.setItem(0, 0, icon_item)
            self.coin_index.setItem(0, 1, QTableWidgetItem(coin))
            self.coin_index.setItem(0, 2, last_price)
            self.coin_index.setItem(0, 3, QTableWidgetItem(price_change))
            self.coin_index.setItem(0, 4, QTableWidgetItem(btc_volume))

            if price_change_value < 0:
                self.coin_index.item(0, 3).setForeground(QColor(colors.color_pink))
            else:
                self.coin_index.item(0, 3).setForeground(QColor(colors.color_green))

            self.btn_trade = QPushButton("Trade " + coin)
            self.btn_trade.clicked.connect(self.gotoTradeButtonClicked)
            self.coin_index.setCellWidget(0, 5, self.btn_trade)

    self.coin_index.model().sort(5, Qt.AscendingOrder)
    self.coin_index.setIconSize(QSize(25, 25))

    self.coin_index.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.coin_index.setColumnWidth(2, 120)
    self.coin_index.model().sort(4, Qt.DescendingOrder)


def build_holdings(self, *args):
    self.holdings_table.setRowCount(0)
    for holding in val["accHoldings"]:

        try:
            # if holding != "BTC" and holding != "BNC":
            if holding + "BTC" in val["coins"]:
                name = val["coins"][holding + "BTC"]["baseAssetName"]
            elif holding == "BTC":
                name = "Bitcoin"
        except KeyError:
            name = "Bitcoin"
        free = val["accHoldings"][holding]["free"]
        locked = val["accHoldings"][holding]["locked"]
        total = float(free) + float(locked)
        total_formatted = '{number:.{digits}f}'.format(number=total, digits=8)

        bold_font = QFont()
        bold_font.setBold(True)

        try:
            if holding == "BTC":
                icon = QIcon("images/ico/" + str(holding) + ".svg")

                icon_item = QTableWidgetItem()
                icon_item.setIcon(icon)
                self.holdings_table.insertRow(0)
                self.holdings_table.setItem(0, 0, icon_item)

                self.holdings_table.setItem(0, 1, QTableWidgetItem(holding))
                self.holdings_table.setItem(0, 2, QTableWidgetItem(name))
                self.holdings_table.setItem(0, 3, QTableWidgetItem("{0:.8f}".format(float(total))))
                self.holdings_table.setItem(0, 4, QTableWidgetItem("{0:g}".format(float(free))))
                self.holdings_table.setItem(0, 5, QTableWidgetItem("{0:g}".format(float(locked))))
                self.holdings_table.setItem(0, 6, QTableWidgetItem(total_formatted))

                self.holdings_table.item(0, 6).setFont(bold_font)
                self.holdings_table.item(0, 6).setForeground(QColor(colors.color_lightgrey))

                self.btn_sell = QPushButton('Trade' + " BTC")
                self.btn_sell.setEnabled(False)
                self.btn_sell.setStyleSheet("color: #666;")
                self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                self.holdings_table.setCellWidget(0, 7, self.btn_sell)

            elif holding + "BTC" in val["coins"]:
                if float(total) * float(val["coins"][holding + "BTC"]["close"]) >= 0.001:
                    icon = QIcon("images/ico/" + str(holding) + ".svg")

                    icon_item = QTableWidgetItem()
                    icon_item.setIcon(icon)

                    total_btc = total * float(val["coins"][holding + "BTC"]["close"])
                    total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)

                    self.holdings_table.insertRow(1)
                    self.holdings_table.setItem(1, 0, icon_item)

                    self.holdings_table.setItem(1, 1, QTableWidgetItem(holding))
                    self.holdings_table.setItem(1, 2, QTableWidgetItem(name))
                    self.holdings_table.setItem(1, 3, QTableWidgetItem("{0:.8f}".format(float(total))))
                    self.holdings_table.setItem(1, 4, QTableWidgetItem("{0:g}".format(float(free))))
                    self.holdings_table.setItem(1, 5, QTableWidgetItem("{0:g}".format(float(locked))))
                    self.holdings_table.setItem(1, 6, QTableWidgetItem(total_btc_formatted))

                    self.holdings_table.item(1, 6).setFont(bold_font)
                    self.holdings_table.item(1, 6).setForeground(QColor(colors.color_lightgrey))

                    self.btn_sell = QPushButton('Trade ' + str(holding))
                    self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                    self.holdings_table.setCellWidget(1, 7, self.btn_sell)

        except KeyError:
            pass

        header = self.holdings_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.holdings_table.setIconSize(QSize(25, 25))


def calc_total_btc():
    total_btc_val = 0
    for holding in val["accHoldings"]:
        free = val["accHoldings"][holding]["free"]
        locked = val["accHoldings"][holding]["locked"]
        total = float(free) + float(locked)

        if holding + "BTC" in val["coins"]:
            if holding != "BTC" and total * float(val["tickers"][holding + "BTC"]["lastPrice"]) > 0.001:

                coin_total = total * float(val["tickers"][holding + "BTC"]["lastPrice"])
                total_btc_val += coin_total

        elif holding == "BTC":
            total_btc_val += total

    total_formatted = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8) + " BTC"
    # print("total: " + total_formatted)
    return total_formatted


def calc_wavg():
    coin = val["coin"]
    current_free = val["accHoldings"][coin]["free"]
    current_locked = val["accHoldings"][coin]["locked"]
    current_total = float(current_free) + float(current_locked)

    remaining = current_total
    total_cost = 0.0
    wavg = 0.0
    sum_traded = 0.0
    print("calculating wavg for " + str(coin))
    print("currently holding " + str(remaining))
    try:
        for i, order in enumerate(val["history"]):
            print(str(order))
            if order["side"] == "BUY":
                sum_traded += float(order["executedQty"])
                remaining -= float(order["executedQty"])
                total_cost += float(order["price"]) * float(order["executedQty"])

                wavg = total_cost / sum_traded

                print(str(i))
                print("sum traded: " + str(sum_traded))
                print("remainign: " + str(remaining))
                print("exec qty: " + str(order["executedQty"]))
                # print(str(i) + ". buy: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))
            elif order["side"] == "SELL":
                print(str(i))
                if wavg != 0:
                    sum_traded -= float(order["executedQty"])
                    print(str(i) + ". Sell: " + str(total_cost) + " remaining: " + str(remaining) + " wavg; " + str(wavg))
                    remaining += float(order["executedQty"])
                    total_cost -= float(order["executedQty"]) * wavg

            if coin != "BTC":
                if remaining <= float(val["coins"][coin + "BTC"]["minTrade"]):

                    if current_total > 0:
                        print("ENOUGH! " + str(total_cost / (current_total - remaining)))
                        final = ('{number:,.{digits}f}'.format(number=total_cost / (current_total - remaining), digits=8))
                        return str(final)

                    return ""
    except KeyError:
        return ""


def update_holding_prices(self):

    """Update the total value of every coin in the holdings table."""

    bold_font = QFont()
    bold_font.setBold(True)

    for i in range(self.holdings_table.rowCount()):

        current_total = self.holdings_table.item(i, 6).text()

        coin = self.holdings_table.item(i, 1).text()
        total = float(self.holdings_table.item(i, 3).text())

        if coin != "BTC":
            current_price = float(val["tickers"][coin + "BTC"]["lastPrice"])
        elif coin == "BTC":
            current_price = 1

        total_value = total * current_price
        total_formatted = '{number:.{digits}f}'.format(number=float(total_value), digits=8)

        if current_total != total_formatted:
            self.holdings_table.item(i, 6).setText(total_formatted)
            self.holdings_table.item(i, 6).setFont(bold_font)
            self.holdings_table.item(i, 6).setForeground(QColor(colors.color_lightgrey))


def update_coin_index_prices(self):
    for i in range(self.coin_index.rowCount()):
        coin = self.coin_index.item(i, 1).text()
        price = self.coin_index.item(i, 2).text()
        price_change = self.coin_index.item(i, 3).text()
        btc_volume = self.coin_index.item(i, 4).text()


        new_price = QTableWidgetItem()
        new_price_change = QTableWidgetItem()
        new_btc_volume = QTableWidgetItem()

        new_price_value = "{0:.8f}".format(float(val["tickers"][coin + "BTC"]["lastPrice"]))
        new_price_change_value = float(val["tickers"][coin + "BTC"]["priceChangePercent"])
        new_btc_volume_value = float(val["tickers"][coin + "BTC"]["quoteVolume"])

        new_price.setData(Qt.EditRole, QVariant(new_price_value))
        new_price_change.setData(Qt.EditRole, QVariant(new_price_change_value))
        new_btc_volume.setData(Qt.EditRole, QVariant(new_btc_volume_value))


        if price != new_price_value:
            self.coin_index.setItem(i, 2, new_price)

        if float(price_change) != new_price_change_value:

            self.coin_index.setItem(i, 3, new_price_change)

        if float(btc_volume) != new_btc_volume_value:

            self.coin_index.setItem(i, 4, new_btc_volume)
