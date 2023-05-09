from PyQt5 import QtCore, QtGui, QtWidgets


class ProductTableWidget(QtWidgets.QTableWidget):
    def __init__(self, *args, **kwargs):
        super(ProductTableWidget, self).__init__(*args, **kwargs)
        self.cellChangedFilter = False
        self.onCellChangeEventHandler = None
        self.cellChanged.connect(self.cellChangedEvent)


    def cellChangedEvent(self, x, y):
        if self.cellChangedFilter:
            return
        if self.onCellChangeEventHandler: self.onCellChangeEventHandler(x, y)


    def removeAllRows(self):
        self.setRowCount(0)
        # removeAllRows


    def setItem(self, *args, **kwargs):
        self.cellChangedFilter = True
        super().setItem(*args, **kwargs)
        self.cellChangedFilter = False


    def addItem(self, item:list):
        rowCount = self.rowCount()
        self.setRowCount(rowCount+1)
        for idx, field in enumerate(item):
            self.cellChangedFilter = True
            if isinstance(field, str):
                self.setItem(rowCount, idx, QtWidgets.QTableWidgetItem(field))
            else:
                self.setCellWidget(rowCount, idx, field)
                self.horizontalHeader().setSectionResizeMode(idx, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.cellChangedFilter = False
        # addItem
