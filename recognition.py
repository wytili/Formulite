from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QStackedWidget, QHBoxLayout,
                             QVBoxLayout, QFileDialog, QMessageBox)
from qfluentwidgets import FluentIcon, SegmentedToggleToolWidget, PlainTextEdit, ImageLabel, \
    BodyLabel, HeaderCardWidget, SimpleCardWidget, PushButton, PrimaryPushButton
from PyQt5.QtGui import QPainter, QPen, QPixmap

class RecognitionInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Recognition-Interface")
        layout = QVBoxLayout()
        self.input = InputCard1()
        self.output = OutputCard1()
        layout.addWidget(self.input)
        layout.addWidget(self.output)
        self.setLayout(layout)


class InputCard1(HeaderCardWidget):

    def __init__(self):
        super().__init__()
        self.setTitle("Input")

        self.pivot = SegmentedToggleToolWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.uploadInterface = UploadBox()
        self.uploadInterface.setFixedHeight(200)
        self.handwritingInterface = HandwritingBoard()

        contentLayout = QVBoxLayout()
        buttonsLayout = QHBoxLayout()

        self.addSubInterface(self.uploadInterface, 'Upload File', FluentIcon.PHOTO)
        self.addSubInterface(self.handwritingInterface, 'Writing Pad', FluentIcon.PENCIL_INK)

        buttonsLayout.addWidget(self.pivot, 0, Qt.AlignCenter)
        contentLayout.addLayout(buttonsLayout)
        contentLayout.addWidget(self.stackedWidget)

        self.viewLayout.addLayout(contentLayout)
        self.clearButton = PushButton(FluentIcon.DELETE, 'Clear')
        self.recognizeButton = PrimaryPushButton(FluentIcon.SEARCH, 'Recognize')
        self.clearButton.setFixedWidth(150)
        self.recognizeButton.setFixedWidth(150)
        buttonsLayout_action = QHBoxLayout()
        buttonsLayout_action.addWidget(self.clearButton)
        buttonsLayout_action.addWidget(self.recognizeButton)

        contentLayout.addLayout(buttonsLayout_action)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

    def addSubInterface(self, widget: QWidget, objectName, icon):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
            icon=icon
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

class UploadBox(SimpleCardWidget):
    def __init__(self, parent=None):
        super(UploadBox, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.initUI()

    def initUI(self):
        self.textLabel = BodyLabel("Click to Upload / Drag & Drop \n an Image Here", self)
        self.textLabel.setAlignment(Qt.AlignCenter)

        self.imageLabel = ImageLabel(parent=self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.textLabel)
        layout.addWidget(self.imageLabel, 0, Qt.AlignCenter)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        pixmap = QPixmap()
        if mimeData.hasImage():
            pixmap = QPixmap(mimeData.imageData())
        elif mimeData.hasUrls():
            for url in mimeData.urls():
                file_path = url.toLocalFile()
                pixmap = QPixmap(file_path)
                break
        if not pixmap.isNull():
            self.switchToImageLabel(pixmap)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
            if fileName:
                pixmap = QPixmap(fileName)
                self.switchToImageLabel(pixmap)

    def paintEvent(self, event):
        super().paintEvent(event)

    @staticmethod
    def scaleToSize(pixmap, targetWidth, targetHeight):
        if pixmap.isNull():
            return QPixmap()

        scaledPixmap = pixmap.scaled(targetWidth, targetHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return scaledPixmap

    def switchToImageLabel(self, pixmap):
        if pixmap.isNull():
            QMessageBox.warning(self, "Image Load Error", "Could not load the image.")
            return

        scaledPixmap = self.scaleToSize(pixmap, 520, 180)

        self.imageLabel.setPixmap(scaledPixmap)
        self.textLabel.setVisible(False)
        self.imageLabel.setVisible(True)


class HandwritingBoard(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.path = []
        self.last_point = None
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.path.append([self.last_point])

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.last_point is not None:
            new_point = event.pos()
            self.path[-1].append(new_point)
            self.last_point = new_point
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_point = None

    def paintEvent(self, event):
        super().paintEvent(event)  # call the paintEvent of SimpleCardWidget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # draw path
        painter.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for segment in self.path:
            if len(segment) > 1:
                for i in range(len(segment) - 1):
                    painter.drawLine(segment[i], segment[i + 1])

class OutputCard1(HeaderCardWidget):
    def __init__(self):
        super().__init__()
        self.setTitle('Output')

        contentLayout = QVBoxLayout()
        textEdit = PlainTextEdit()
        textEdit.setReadOnly(True)
        contentLayout.addWidget(textEdit)

        self.copyButton = PushButton(FluentIcon.COPY, 'Copy')
        self.copyButton.setFixedWidth(150)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.copyButton, 0, Qt.AlignCenter)

        contentLayout.addLayout(buttonLayout)

        self.viewLayout.addLayout(contentLayout)
