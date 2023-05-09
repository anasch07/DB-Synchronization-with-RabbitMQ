# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from rabbitmq import RabbitMQConnection
from consts import COLUMNS, HIDDEN_COLS, SPECIAL_COLS, BRANCH_OFFICES, AUTO_SYNC
from models import Product
from ProductTableWidget import ProductTableWidget
from sqlalchemy.orm import Session
from ClickableImageWidget import ClickableImageWidget
from AddProdScreen import AddProdScreen
from helpers.conversion import int2, float2
from helpers.sync_actions import handleSyncAction


class Ui_MainWindow(object):
    def __init__(self, QMainWindow: QtWidgets.QMainWindow, connection: RabbitMQConnection, session: Session) -> None:
        self.connection = connection
        self.session = session
        
        self.setupUi(QMainWindow)
        self.loadDbRows()
        # __init__
    

    def handleSyncButtonClick(self, auto=False):
        confirmed = {}
        errorDetected = False
        try:
            self.connection.connect()
            for office in BRANCH_OFFICES:
                self.connection.consumer.declareDurableQueue(office)
                confirmed[office] = 0

                while True:
                    method, _, body = self.connection.consumer.readQueue(office, auto_ack=False)
                    if method is None or body is None:
                        break
                    
                    try: handleSyncAction(body, office, self.session)
                    except Exception as error:
                        print("Error2:", error)
                        print(body)
                        errorDetected = True
                        self.connection.consumer.sendNack(method.delivery_tag)

                        if not auto:
                            errorDiag = QtWidgets.QMessageBox()
                            errorDiag.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                            errorDiag.setText(f"Unable to save product in db.\nSource: {office}.\nData: {body}")
                            errorDiag.setWindowTitle("Error!")
                            errorDiag.exec_()
                        else:
                            print(f"[!] Unable to save product in db.\nSource: {office}.\nData: {body}")
                        break

                    confirmed[office] += 1
                    self.connection.consumer.sendAck(method.delivery_tag)
            
            if not errorDetected:
                total = 0
                msg = "Synced {0} changes.\nDetails:"
                for key, value in confirmed.items():
                    total += value
                    msg += f"\n    {key}: {value} changes."
                msg = msg.format(total)

                if not auto:
                    infoDiag = QtWidgets.QMessageBox()
                    infoDiag.setIcon(QtWidgets.QMessageBox.Icon.Information)
                    infoDiag.setText(msg)
                    infoDiag.setWindowTitle("Success!")
                    infoDiag.exec_()
                else:
                    print(f"[+] {msg}")
        except Exception as e:
            total = 0
            msg = "Synced {0} changes.\nDetails:"
            for key, value in confirmed.items():
                total += value
                msg += f"\n    {key}: {value} changes."
            msg = msg.format(total)

            print("Error1:", e)

            if not auto:
                errorDiag = QtWidgets.QMessageBox()
                errorDiag.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                errorDiag.setText(f"Unable to get data.\n{msg}")
                errorDiag.setWindowTitle("Error!")
                errorDiag.exec_()
            else:
                print(f"[!] Unable to get data.\n{msg}")
        finally:
            self.connection.disconnect()
            self.reloadTableRows()
        # handleSyncButtonClick


    def genTableList(self, product: Product):
        prod = product.toList()
        row = prod[:len(COLUMNS)]

        row.extend(prod[len(COLUMNS):])
        return row


    def reloadTableRows(self):
        self.tableView.removeAllRows()
        self.loadDbRows()
        # reloadTableRows


    def loadDbRows(self):
        products = self.session.query(Product).all()
        for product in products:
            row = self.genTableList(product)
            self.tableView.addItem(row)
        # loadDbRows


    def onCellChangeEventHandler(self, row, col):
        id = int(self.tableView.item(row, HIDDEN_COLS.index('id') + len(COLUMNS) + len(SPECIAL_COLS)).text())
        prod = self.session.query(Product).filter(Product.id == id).first()
        if prod is None:
            return
        
        if prod.source != self.connection.clientId:
            self.tableView.setItem(row,COLUMNS.index('Cost'), QtWidgets.QTableWidgetItem(str(prod.cost)))
            self.tableView.setItem(row,COLUMNS.index('Qty'), QtWidgets.QTableWidgetItem(str(prod.qty)))
            self.tableView.setItem(row,COLUMNS.index('Tax'), QtWidgets.QTableWidgetItem(str(prod.tax)))
            self.tableView.setItem(row,COLUMNS.index('Amt'), QtWidgets.QTableWidgetItem(str(prod.amt)))
            self.tableView.setItem(row,COLUMNS.index('Total'), QtWidgets.QTableWidgetItem(str(prod.total)))
            self.tableView.setItem(row,COLUMNS.index('Source'), QtWidgets.QTableWidgetItem(str(prod.source)))
            self.tableView.setItem(row,COLUMNS.index('Product'), QtWidgets.QTableWidgetItem(str(prod.product)))
            self.tableView.setItem(row,COLUMNS.index('Date'), QtWidgets.QTableWidgetItem(str(prod.date)))
            self.tableView.setItem(row,COLUMNS.index('Region'), QtWidgets.QTableWidgetItem(str(prod.region)))
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
        self.tableView.setItem(row,COLUMNS.index('Source'), QtWidgets.QTableWidgetItem(str(prod.source)))

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
        # self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.onCellChangeEventHandler = self.onCellChangeEventHandler

        for idx in range(len(COLUMNS)+len(SPECIAL_COLS), len(COLUMNS)+len(SPECIAL_COLS)+len(HIDDEN_COLS)):
            self.tableView.setColumnHidden(idx, True)
        
        tableHeaders = self.tableView.horizontalHeader()
        for idx in range(len(COLUMNS)):
            tableHeaders.setSectionResizeMode(idx, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.tableView.setObjectName("tableView")

        self.syncButton = QtWidgets.QPushButton(self.centralwidget)
        self.syncButton.setGeometry(QtCore.QRect(950, 20, 100, 30))
        self.syncButton.clicked.connect(lambda _: self.handleSyncButtonClick())
        self.syncButton.setObjectName("syncButton")

        self.autoSyncTimer = QtCore.QTimer()
        self.autoSyncTimer.timeout.connect(lambda : self.handleSyncButtonClick(True))
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
        product.source = self.connection.clientId
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
    