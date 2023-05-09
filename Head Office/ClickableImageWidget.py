from PyQt5 import QtWidgets, QtCore, QtGui


class ClickableImageWidget(QtWidgets.QLabel):
    def __init__(self, path, onClickEvent, *args, **kwargs):
        super(ClickableImageWidget, self).__init__(*args, **kwargs)
        with open(path, 'rb') as f:
            bytes = f.read()
        img = QtGui.QImage()
        img.loadFromData(bytes)

        self.setPixmap(QtGui.QPixmap(img))
        self.mouseReleaseEvent = onClickEvent
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
