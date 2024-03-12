from PyQt5.QtCore import Qt, QByteArray, QBuffer, QTimer
from PyQt5.QtWidgets import (QWidget, QStackedWidget, QHBoxLayout, QApplication,
                             QVBoxLayout, QFileDialog)
from qfluentwidgets import FluentIcon, SegmentedToggleToolWidget, PlainTextEdit, ImageLabel, \
    BodyLabel, HeaderCardWidget, SimpleCardWidget, PushButton, PrimaryPushButton, InfoBar
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage, QFont, QKeySequence

from config import cfg
from ocr_services import OCRClient
from settings import decrypt_text


class RecognitionInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Recognition-Interface")
        layout = QVBoxLayout()
        self.input = InputCard1()
        self.input.setFocus()
        self.output = OutputCard1()
        layout.addWidget(self.input)
        layout.addWidget(self.output)
        self.setLayout(layout)
        QTimer.singleShot(0, self.input.uploadInterface.setFocus)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            self.pasteImageFromClipboard()
        else:
            super().keyPressEvent(event)

    def pasteImageFromClipboard(self):
        clipboard = QApplication.clipboard()
        mimeData = clipboard.mimeData()
        if mimeData.hasImage():
            image = QImage(mimeData.imageData())
            if not image.isNull():
                self.input.uploadInterface.setImage(image)


class InputCard1(HeaderCardWidget):

    def __init__(self):
        super().__init__()
        self.setTitle(self.tr("Input"))
        self.pivot = SegmentedToggleToolWidget(self)
        self.stackedWidget = QStackedWidget(self)

        self.uploadInterface = UploadBox()
        self.uploadInterface.setFocus()
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
        self.clearButton = PushButton(FluentIcon.DELETE, self.tr("Clear"))
        self.recognizeButton = PrimaryPushButton(FluentIcon.VIEW, self.tr("Recognize"))
        self.clearButton.setFixedWidth(150)
        self.recognizeButton.setFixedWidth(150)

        self.clearButton.clicked.connect(self.clearCurrentWidget)
        self.recognizeButton.clicked.connect(self.recognizeContent)

        buttonsLayout_action = QHBoxLayout()
        buttonsLayout_action.addWidget(self.clearButton)
        buttonsLayout_action.addWidget(self.recognizeButton)

        contentLayout.addLayout(buttonsLayout_action)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentIndex(0)
        initialWidget = self.stackedWidget.currentWidget()
        self.pivot.setCurrentItem(initialWidget.objectName())

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

    def clearCurrentWidget(self):
        currentIndex = self.stackedWidget.currentIndex()
        if currentIndex == 0:  # UploadBox
            self.uploadInterface.clearContent()
        elif currentIndex == 1:  # HandwritingBoard
            self.handwritingInterface.clearContent()

    def recognizeContent(self):
        self.parent().output.textEdit.clear()
        currentWidget = self.stackedWidget.currentWidget()
        image_bytes = None
        # at upload interface
        if isinstance(currentWidget, UploadBox):
            image_bytes = currentWidget.getImageAsBytes()
        # at handwriting interface
        elif isinstance(currentWidget, HandwritingBoard):
            image_bytes = currentWidget.getDrawingAsBytes()

        if image_bytes:
            service = f"{cfg.apiService.value}"
            access_key_id = cfg.apiId.value
            access_key_secret = decrypt_text(cfg.apiKey.value)
            if not access_key_id or not access_key_secret:
                InfoBar.warning(
                    title=self.tr("API Info Required"),
                    content=self.tr("Please fill in valid API ID and Key in the settings."),
                    parent=self.parent()
                ).show()
                return

            try:
                ocr_client = OCRClient(service, id=access_key_id,
                                       key=access_key_secret)
                recognition_result = ocr_client.recognizeText(image_bytes)
                if recognition_result['status']:
                    self.parent().output.displayRecognitionResult(recognition_result)
                else:
                    InfoBar.error(
                        title=self.tr("Recognition Failed"),
                        content=self.tr("Please check the Network and API settings."),
                        parent=self.parent()
                    ).show()
            except ValueError as e:
                InfoBar.error(
                    title='Error',
                    content=str(e),
                    parent=self.parent()
                ).show()
        else:
            InfoBar.warning(
                title=self.tr("Empty"),
                content=self.tr("No content to recognize."),
                parent=self.parent()
            ).show()


class UploadBox(SimpleCardWidget):
    def __init__(self, parent=None):
        super(UploadBox, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.currentImage = None
        self.initUI()

    def initUI(self):
        self.textLabel = BodyLabel(self.tr("Click to Upload / Drag & Drop / Paste (Ctrl + V)  an Image Here"), self)
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
        if mimeData.hasImage():
            self.currentImage = mimeData.imageData()
        elif mimeData.hasUrls():
            url = mimeData.urls()[0].toLocalFile()
            self.currentImage = QImage(url)
        if self.currentImage and not self.currentImage.isNull():
            self.switchToImageLabel(QPixmap.fromImage(self.currentImage))
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            fileName, _ = QFileDialog.getOpenFileName(self, self.tr("Open Image"), "", self.tr("Image Files (*.png "
                                                                                               "*.jpg *.bmp)"))
            if fileName:
                # load image from path
                image = QImage(fileName)
                self.currentImage = image
                pixmap = QPixmap.fromImage(image)
                self.switchToImageLabel(pixmap)

    def setImage(self, image):
        if isinstance(image, QImage) and not image.isNull():
            self.currentImage = image
            pixmap = QPixmap.fromImage(image)
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
            InfoBar.warning(
                title=self.tr("Image Load Error"),
                content=self.tr("Could not load the image."),
                parent=self.parent()
            ).show()
            return

        scaledPixmap = self.scaleToSize(pixmap, 510, 180)

        self.imageLabel.setPixmap(scaledPixmap)
        self.textLabel.setVisible(False)
        self.imageLabel.setVisible(True)

    def clearContent(self):
        self.imageLabel.clear()
        self.currentImage = None
        self.textLabel.setVisible(True)
        self.imageLabel.setVisible(False)

    def getImageAsBytes(self):
        # transform current image to QByteArray
        if self.currentImage is None or self.currentImage.isNull():
            return None  # invalid image

        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QBuffer.WriteOnly)
        self.currentImage.save(buffer, 'PNG')
        return byte_array.data()


class HandwritingBoard(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.path = []
        self.last_point = None
        self.setMouseTracking(True)
        self.total_drawn_length = 0  # total length of drawn path

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.path.append([self.last_point])

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.last_point is not None:
            new_point = event.pos()
            self.path[-1].append(new_point)
            self.total_drawn_length += (new_point - self.last_point).manhattanLength()
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

    def draw(self, painter):
        painter.setPen(QPen(Qt.black, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for segment in self.path:
            for i in range(1, len(segment)):
                painter.drawLine(segment[i - 1], segment[i])

    def getDrawingAsBytes(self):
        if not self.path or self.total_drawn_length < 10:
            return None

        image = QImage(self.size(), QImage.Format_ARGB32)
        image.fill(Qt.white)

        painter = QPainter(image)
        self.draw(painter)
        painter.end()

        buffer = QBuffer()
        buffer.open(QBuffer.WriteOnly)
        image.save(buffer, "PNG")

        return bytes(buffer.data())

    def clearContent(self):
        self.path = []
        self.total_drawn_length = 0
        self.update()


class OutputCard1(HeaderCardWidget):
    def __init__(self):
        super().__init__()
        self.setTitle(self.tr("Output"))

        contentLayout = QVBoxLayout()
        self.textEdit = PlainTextEdit()
        self.textEdit.setReadOnly(True)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(15)
        self.textEdit.setFont(font)
        contentLayout.addWidget(self.textEdit)

        self.copyButton = PushButton(FluentIcon.COPY, self.tr("Copy"))
        self.copyButton.setFixedWidth(150)
        self.copyButton.clicked.connect(self.copyResult)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.copyButton, 0, Qt.AlignCenter)

        contentLayout.addLayout(buttonLayout)

        self.viewLayout.addLayout(contentLayout)

    def displayRecognitionResult(self, recognition_result):
        results = recognition_result.get('results', [])
        detected_texts = []  # store all detected texts

        for result in results:
            if isinstance(result, dict):  # check if the result is a dict
                text = result.get('DetectedText', '')
                detected_texts.append(text)
            elif isinstance(result, str):  # check if the result is a string
                detected_texts.append(result)

        result_text = "\n".join(detected_texts)

        self.textEdit.setPlainText(result_text)

    def copyResult(self):
        text = self.textEdit.toPlainText()
        if text.strip():  # check if there is any text
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            InfoBar.success(
                title=self.tr("Copied"),
                content=self.tr("Text copied to clipboard."),
                parent=self.parent()
            ).show()
        else:
            InfoBar.warning(
                title=self.tr("No Text"),
                content=self.tr("There is no text to copy."),
                parent=self.parent()
            ).show()
