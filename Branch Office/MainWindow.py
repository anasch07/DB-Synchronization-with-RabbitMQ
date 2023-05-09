# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from rabbitmq import RabbitMQConnection
from consts import COLUMNS, HIDDEN_COLS, SPECIAL_COLS, AUTO_SYNC
from models import Product
from ProductTableWidget import ProductTableWidget
from sqlalchemy.orm import Session
from ClickableImageWidget import ClickableImageWidget
from AddProdScreen import AddProdScreen
from helpers.conversion import int2, float2
from helpers.sync_actions import genActionMessage
from sqlalchemy import or_


class Ui_MainWindow(object):
    def __init__(self, QMainWindow: QtWidgets.QMainWindow, connection: RabbitMQConnection, session: Session) -> None:
        self.connection = connection
        self.session = session
        
        self.setupUi(QMainWindow)
        self.loadDbRows()
        # __init__
    

    def genTableList(self, product: Product):
        prod = product.toList()
        row = prod[:len(COLUMNS)]

        delBtn = ClickableImageWidget("./images/del.png", lambda event: product.softDelete(self.session) or self.reloadTableRows())
        row.append(delBtn)

        row.extend(prod[len(COLUMNS):])
        return row


    def reloadTableRows(self):
        self.tableView.removeAllRows()
        self.loadDbRows()
        # reloadTableRows


    def loadDbRows(self):
        products = self.session.query(Product).filter(Product.toDelete == False).all()
        for product in products:
            row = self.genTableList(product)
            self.tableView.addItem(row)
        # loadDbRows
    

    def onSyncButtonClicked(self, auto=False):
        confirmed = 0
        total = 0
        try:
            self.connection.connect()
            self.connection.publisher.declareDurableQueue(self.connection.clientId)
            unsyncProducts = self.session.query(Product).filter(or_(Product.created == True,Product.edited == True,Product.toDelete == True)).all()
            total = len(unsyncProducts)
            for product in unsyncProducts:
                message = genActionMessage(product)
                if self.connection.publisher.sendMessage(message, self.connection.clientId):
                    product.setSynced(self.session)
                    confirmed += 1
                else:
                    raise "Sync failed"
            
            if not auto:
                infoDiag = QtWidgets.QMessageBox()
                infoDiag.setIcon(QtWidgets.QMessageBox.Icon.Information)
                infoDiag.setText(f"Synced {confirmed} rows.")
                infoDiag.setWindowTitle("Success!")
                infoDiag.exec_()
            else:
                print(f"[+] Auto-Synced {confirmed} rows.")
        except Exception as e:
            print("Error1: ", e)
            if not auto:
                errorDiag = QtWidgets.QMessageBox()
                errorDiag.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                errorDiag.setText(f"Unable to confirm sync. {confirmed} confirmed out of {total}")
                errorDiag.setWindowTitle("Error!")
                errorDiag.exec_()
            else:
                print(f"Unable to confirm sync. {confirmed} confirmed out of {total}")
        finally:
            self.connection.disconnect()


    def onCellChangeEventHandler(self, row, col):
        id = int(self.tableView.item(row, HIDDEN_COLS.index('id') + len(COLUMNS) + len(SPECIAL_COLS)).text())
        prod = self.session.query(Product).filter(Product.id == id).first()
        if prod is None:
            return
        
        qty = int2(self.tableView.item(row,COLUMNS.index('Qty')).text())
        cost = float2(self.tableView.item(row,COLUMNS.index('Cost')).text())
        tax = float2(self.tableView.item(row,COLUMNS.index('Tax')).text())
        amt = qty*cost
        total = amt + tax

        prod.setProduct(self.tableView.item(row,COLUMNS.index('Product')).text())
        prod.setDate(self.tableView.item(row,COLUMNS.index('Date')).text())
        prod.setRegion(self.tableView.item(row,COLUMNS.index('Region')).text())
        prod.setQty(qty)
        prod.setCost(cost)
        prod.setAmt(qty*cost)
        prod.setTax(tax)
        prod.setTotal(total)

        self.tableView.setItem(row,COLUMNS.index('Cost'), QtWidgets.QTableWidgetItem(str(cost)))
        self.tableView.setItem(row,COLUMNS.index('Qty'), QtWidgets.QTableWidgetItem(str(qty)))
        self.tableView.setItem(row,COLUMNS.index('Tax'), QtWidgets.QTableWidgetItem(str(tax)))
        self.tableView.setItem(row,COLUMNS.index('Amt'), QtWidgets.QTableWidgetItem(str(amt)))
        self.tableView.setItem(row,COLUMNS.index('Total'), QtWidgets.QTableWidgetItem(str(total)))

        self.session.add(prod)
        self.session.commit()
        # onCellChangeEventHandler
    

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 553)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tableView = ProductTableWidget(0, len(COLUMNS)+len(HIDDEN_COLS)+len(SPECIAL_COLS), self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(10, 70, 1100-2*10, 431))
        self.tableView.setHorizontalHeaderLabels(COLUMNS+['']*len(SPECIAL_COLS))
        self.tableView.onCellChangeEventHandler = self.onCellChangeEventHandler

        for idx in range(len(COLUMNS)+len(SPECIAL_COLS), len(COLUMNS)+len(SPECIAL_COLS)+len(HIDDEN_COLS)):
            self.tableView.setColumnHidden(idx, True)
        
        tableHeaders = self.tableView.horizontalHeader()
        for idx in range(len(COLUMNS)):
            tableHeaders.setSectionResizeMode(idx, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.tableView.setObjectName("tableView")

        self.syncButton = QtWidgets.QPushButton(self.centralwidget)
        self.syncButton.setGeometry(QtCore.QRect(950, 20, 100, 30))
        self.syncButton.clicked.connect(lambda _: self.onSyncButtonClicked())
        self.syncButton.setObjectName("syncButton")

        self.autoSyncTimer = QtCore.QTimer()
        self.autoSyncTimer.timeout.connect(lambda : self.onSyncButtonClicked(True))
        self.autoSyncTimer.start(AUTO_SYNC)

        self.addButton = ClickableImageWidget("./images/add.png", self.showAddProdDialog, self.centralwidget)
        self.addButton.setGeometry(QtCore.QRect(910, 20, 30, 30))

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 658, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # setupUi


    def showAddProdDialog(self, event):
        AddProductDialog = QtWidgets.QDialog()
        screen = AddProdScreen(AddProductDialog)
        screen.onAddPress = self.insertNewProduct
        AddProductDialog.exec()
        # showAddProdDialog


    def insertNewProduct(self, product: Product):
        self.session.add(product)
        self.session.commit()
        row = self.genTableList(product)
        self.tableView.addItem(row)
        # insertNewProduct


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", self.connection.clientId))
        self.syncButton.setText(_translate("MainWindow", "Sync Data"))
        # retranslateUi
    