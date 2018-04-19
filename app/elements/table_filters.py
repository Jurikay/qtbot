# from app.workers import Worker
# import PyQt5.QtWidgets as QtWidgets
# import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
# import app
# from app.init import val


class TableFilters:
    def __init__(self, mw):
        self.mw = mw

        self.mw.tabsBotLeft.setCornerWidget(self.mw.coin_index_filter, corner=QtCore.Qt.TopRightCorner)
        self.mw.hide_pairs.stateChanged.connect(self.init_filter)

        self.mw.coinindex_filter.returnPressed.connect(self.filter_return)

        self.mw.coinindex_filter.textChanged.connect(self.init_filter)
        self.mw.tabsBotLeft.currentChanged.connect(self.init_filter)
        self.mw.cancel_all.clicked.connect(self.mw.open_orders.cancel_all_orders)

    def init_filter(self):
        print("init filter")
        text = self.mw.coinindex_filter.text()
        state = self.mw.hide_pairs.checkState()

        # print("text: " + str(text) + " state: " + str(state))

        self.filter_table(text, state)

        # reset filter
        if state == 0 and text == "":
            print("UNHIDE ALL")
            for i in range(self.mw.holdings_table.rowCount()):
                self.mw.holdings_table.setRowHidden(i, False)
            for i in range(self.mw.open_orders.rowCount()):
                self.mw.open_orders.setRowHidden(i, False)
            for i in range(self.mw.coin_index.rowCount()):
                self.mw.coin_index.setRowHidden(i, False)
                self.mw.coin_index.update()
                print("unhide: " + str(i))


    def filter_table(self, text, state):
        print("filter table")
        # print("filter table state: " + str(state))
        # tabIndex = self.mw.tabsBotLeft.currentIndex()
        # if tabIndex == 0:
        self.mw.coin_index.filter_coin_index(text, state)
        # elif tabIndex == 1:
        self.mw.open_orders.filter_open_orders(text, state)
        # elif tabIndex == 3:
        self.mw.holdings_table.filter_holdings(text, state)


        if text != "" or state == 2:
            self.mw.holdings_table.setSortingEnabled(False)
            self.mw.open_orders.setSortingEnabled(False)
            self.mw.coin_index.setSortingEnabled(False)
        else:
            self.mw.holdings_table.setSortingEnabled(True)
            self.mw.open_orders.setSortingEnabled(True)
            self.mw.coin_index.setSortingEnabled(True)

        # state = self.mw.hide_pairs.checkState()
        # if state == 2:
        #     self.toggle_other_pairs(state)





    def filter_return(self):

        """Iterate through the currently active table and switch
           the active pair to the topmost non-hidden coin."""

        tabIndex = self.mw.tabsBotLeft.currentIndex()
        if tabIndex == 0:
            self.coin_index_goto()
        elif tabIndex == 1:
            self.open_orders_goto()
        elif tabIndex == 2:
            self.history_goto()
        elif tabIndex == 3:
            self.holdings_goto()


    def coin_index_goto(self):
        for row in range(self.mw.coin_index.rowCount()):
            top_coin = self.mw.coin_index.item(row, 1).text()

            if self.mw.coin_index.isRowHidden(row) or top_coin == "BTC":
                continue
            else:
                coinIndex = self.mw.coin_selector.findText(top_coin)
                self.mw.coin_selector.setCurrentIndex(coinIndex)
                self.mw.gui_manager.change_pair()
                return


    def open_orders_goto(self):
        for row in range(self.mw.open_orders.rowCount()):
            top_coin = self.mw.open_orders.item(row, 2).text().replace("BTC", "")
            if self.mw.coin_index.isRowHidden(row) or top_coin == "BTC":
                continue
            else:
                coinIndex = self.mw.coin_selector.findText(top_coin)
                self.mw.coin_selector.setCurrentIndex(coinIndex)
                self.mw.gui_manager.change_pair()
                return


    def history_goto(self):
        for row in range(self.mw.history_table.rowCount()):
            top_coin = self.mw.history_table.item(row, 2).text().replace("BTC", "")
            if self.mw.history_table.isRowHidden(row) or top_coin == "BTC":
                continue
            else:
                coinIndex = self.mw.coin_selector.findText(top_coin)
                self.mw.coin_selector.setCurrentIndex(coinIndex)
                self.mw.gui_manager.change_pair()
                return


    def holdings_goto(self):
        for row in range(self.mw.holdings_table.rowCount()):
            top_coin = self.mw.holdings_table.item(row, 1).text()

            if self.mw.holdings_table.isRowHidden(row) or top_coin == "BTC":
                continue
            else:
                coinIndex = self.mw.coin_selector.findText(top_coin)
                self.mw.coin_selector.setCurrentIndex(coinIndex)
                self.mw.gui_manager.change_pair()
                return



        # elif tabIndex == 1:
        #     self.mw.open_orders.filter_open_orders(text, state)
        # elif tabIndex == 3:
        #     self.mw.holdings_table.filter_holdings(text, state)



    # def filter_confirmed(self):
    #     """Switch to the topmost coin of the coin index that is not hidden."""
    #     # check if input is empty
    #     if self.mw.coinindex_filter.text() != "":
    #         # self.coin_index.setSortingEnabled(False)
    #         # test = self.coin_index.
    #         # print(str(test))

    #         # iterate through all rows
    #         for i in (range(self.mw.coin_index.rowCount())):
    #             # skip the row if hidden
    #             if self.mw.coin_index.isRowHidden(i):
    #                 continue
    #             else:
    #                 # return the first nonhidden row (might be inefficient)
    #                 coin = self.mw.coin_index.item(i, 1).text()
    #                 # switch to that coin
    #                 # print(str(coin) + "   " + str(val["pair"]))

    #                 if coin != val["pair"].replace("BTC", ""):
    #                     coinIndex = self.mw.coin_selector.findText(coin)
    #                     self.mw.coin_selector.setCurrentIndex(coinIndex)
    #                     self.mw.gui_manager.change_pair()
    #                     # self.coin_index.setSortingEnabled(True)
    #                     return

    #                 elif coin == val["pair"].replace("BTC", ""):
    #                     # self.coin_index.setSortingEnabled(True)
    #                     return
