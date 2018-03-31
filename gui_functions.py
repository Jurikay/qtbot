from init import val
from PyQt5.QtCore import QThreadPool, QTimer, QObject, QRunnable, pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import QDialog, QWidget, QMainWindow, QListWidgetItem, QScrollBar, QTableWidgetItem, QStyleFactory, QHeaderView, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QColor, QPalette, QIcon, QStandardItem, QPixmap, QFont, QFontDatabase, QCursor
from PyQt5.uic import loadUi
from colors import *
from charts import build_chart2, welcome_page

from binance.websockets import BinanceSocketManager


def initial_values(self):
    self.limit_total_btc.setText(str(val["accHoldings"]["BTC"]["free"]) + " BTC")
    self.limit_total_coin.setText(str(val["accHoldings"][val["coin"]]["free"]) + " " + val["coin"])

    self.limit_buy_label.setText("<span style='font-weight: bold;'>Buy " + val["coin"] + "</span>")
    self.limit_sell_label.setText("<span style='font-weight: bold;'>Sell " + val["coin"] + "</span>")

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
    bids_header.setSectionResizeMode(1, QHeaderView.Fixed)
    bids_header.setSectionResizeMode(2, QHeaderView.Fixed)

    asks_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
    asks_header.setSectionResizeMode(1, QHeaderView.Fixed)
    asks_header.setSectionResizeMode(2, QHeaderView.Fixed)





def build_holdings(self, *args):
    self.holdings_table.setRowCount(0)
    for holding in val["accHoldings"]:

        try:
            name = val["coins"][holding + "BTC"]["baseAssetName"]
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
                self.holdings_table.setItem(0, 3, QTableWidgetItem(total_formatted))
                self.holdings_table.setItem(0, 4, QTableWidgetItem(free))
                self.holdings_table.setItem(0, 5, QTableWidgetItem(locked))
                self.holdings_table.setItem(0, 6, QTableWidgetItem(total_formatted))

                self.holdings_table.item(0, 6).setFont(bold_font)
                self.holdings_table.item(0, 6).setForeground(QColor(color_lightgrey))

                self.btn_sell = QPushButton('Trade' + " BTC")
                self.btn_sell.setEnabled(False)
                self.btn_sell.setStyleSheet("color: #666;")
                self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                self.holdings_table.setCellWidget(0,7,self.btn_sell)



            elif float(total) * float(val["coins"][holding + "BTC"]["close"]) >= 0.001:
                icon = QIcon("images/ico/" + str(holding) + ".svg")

                icon_item = QTableWidgetItem()
                icon_item.setIcon(icon)

                total_btc = total * float(val["coins"][holding + "BTC"]["close"])
                total_btc_formatted = '{number:.{digits}f}'.format(number=total_btc, digits=8)


                self.holdings_table.insertRow(1)
                self.holdings_table.setItem(1, 0, icon_item)

                self.holdings_table.setItem(1, 1, QTableWidgetItem(holding))
                self.holdings_table.setItem(1, 2, QTableWidgetItem(name))
                self.holdings_table.setItem(1, 3, QTableWidgetItem(total_formatted))
                self.holdings_table.setItem(1, 4, QTableWidgetItem(free))
                self.holdings_table.setItem(1, 5, QTableWidgetItem(locked))
                self.holdings_table.setItem(1, 6, QTableWidgetItem(total_btc_formatted))

                self.holdings_table.item(1, 6).setFont(bold_font)
                self.holdings_table.item(1, 6).setForeground(QColor(color_lightgrey))

                self.btn_sell = QPushButton('Trade ' + str(holding))
                self.btn_sell.clicked.connect(self.gotoTradeButtonClicked)
                self.holdings_table.setCellWidget(1,7,self.btn_sell)

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

        try:
            if holding != "BTC" and total * float(val["tickers"][holding+"BTC"]["lastPrice"]) > 0.001:

                coin_total = total * float(val["tickers"][holding+"BTC"]["lastPrice"])
                total_btc_val += coin_total


            elif holding == "BTC":
                total_btc_val += total
        except KeyError:
            # print("error")
            # HIER!
            pass
    total_formatted = '{number:.{digits}f}'.format(number=float(total_btc_val), digits=8) + " BTC"

    return total_formatted


def calc_wavg():
    coin = val["coin"]
    current_free = val["accHoldings"][coin]["free"]
    current_locked = val["accHoldings"][coin]["locked"]
    current_total = float(current_free) + float(current_locked)

    remaining = current_total
    total_cost = 0.0
    wAvg = 0.0
    sumTraded = 0.0
    print("calculating wAvg for " + str(coin))
    print("currently holding " + str(remaining))
    try:
        for i, order in enumerate(val["history"]):
            print(str(order))
            if order["side"] == "BUY":
                sumTraded += float(order["executedQty"])
                remaining -= float(order["executedQty"])
                total_cost += float(order["price"]) * float(order["executedQty"])

                wAvg = total_cost/(sumTraded)

                print(str(i))
                print("sum traded: " + str(sumTraded))
                print("remainign: " + str(remaining))
                print("exec qty: " + str(order["executedQty"]))
                # print(str(i) + ". buy: " + str(total_cost) + " remaining: " + str(remaining) + " wAvg; " + str(wAvg))
            elif order["side"] == "SELL":
                print(str(i))
                if wAvg != 0:
                    sumTraded -= float(order["executedQty"])
                    print(str(i) + ". Sell: " + str(total_cost) + " remaining: " + str(remaining) + " wAvg; " + str(wAvg))
                    remaining += float(order["executedQty"])
                    total_cost -= float(order["executedQty"]) * wAvg


            if coin != "BTC":
                if remaining <= float(val["coins"][coin+"BTC"]["minTrade"]):


                    if current_total > 0:
                        print("ENOUGH! " + str(total_cost / (current_total-remaining)))
                        final = ('{number:,.{digits}f}'.format(number=total_cost / (current_total-remaining), digits=8))
                        return str(final)
                    else:
                        return ""
    except KeyError:
        pass
