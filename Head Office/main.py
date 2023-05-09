from MainWindow import Ui_MainWindow
from PyQt5 import QtWidgets
from rabbitmq import RabbitMQConnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"{sys.argv[0]} [Identifier]")
        exit()
    
    engine = create_engine(f'sqlite:///{sys.argv[1]}.db')
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    
    app = QtWidgets.QApplication(sys.argv)
    conn = RabbitMQConnection(sys.argv[1])

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow, conn, session)
    MainWindow.show()
    
    sys.exit(app.exec_())

