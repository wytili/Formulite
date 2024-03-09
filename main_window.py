import sys
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStackedWidget, QHBoxLayout, QLabel, QWidget, QVBoxLayout

from qfluentwidgets import (NavigationItemPosition, isDarkTheme, setTheme, Theme, NavigationToolButton, NavigationPanel,
                            qconfig)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from config import cfg
from recognition import RecognitionInterface
from preview import PreviewInterface
from settings import SettingInterface


class Widget(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        self.setObjectName(text.replace(' ', '-'))


class NavigationBar(QWidget):
    """ Navigation widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.menuButton = NavigationToolButton(FIF.MENU, self)
        self.navigationPanel = NavigationPanel(parent, True)
        self.titleLabel = QLabel(self)

        self.navigationPanel.move(0, 31)
        self.hBoxLayout.setContentsMargins(5, 5, 5, 5)
        self.hBoxLayout.addWidget(self.menuButton)
        self.hBoxLayout.addWidget(self.titleLabel)

        self.menuButton.clicked.connect(self.showNavigationPanel)
        self.navigationPanel.setExpandWidth(260)
        self.navigationPanel.setMenuButtonVisible(True)
        self.navigationPanel.hide()

        # enable acrylic effect
        self.navigationPanel.setAcrylicEnabled(True)

        self.window().installEventFilter(self)

    def setTitle(self, title: str):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def showNavigationPanel(self):
        self.navigationPanel.show()
        self.navigationPanel.raise_()
        self.navigationPanel.expand()

    def addItem(self, routeKey, icon, text: str, onClick, selectable=True, position=NavigationItemPosition.TOP):
        def wrapper():
            shouldSetTitle = onClick()
            if shouldSetTitle is not False:
                self.setTitle(text)

        self.navigationPanel.addItem(
            routeKey, icon, text, wrapper, selectable, position)

    def addSeparator(self, position=NavigationItemPosition.TOP):
        self.navigationPanel.addSeparator(position)

    def setCurrentItem(self, routeKey: str):
        self.navigationPanel.setCurrentItem(routeKey)
        self.setTitle(self.navigationPanel.widget(routeKey).text())

    def eventFilter(self, obj, e: QEvent):
        if obj is self.window():
            if e.type() == QEvent.Resize:
                self.navigationPanel.setFixedHeight(e.size().height() - 31)

        return super().eventFilter(obj, e)


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        self.vBoxLayout = QVBoxLayout(self)
        self.navigationInterface = NavigationBar(self)
        self.stackWidget = QStackedWidget(self)

        cfg.themeChanged.connect(self.onThemeChanged)

        # create sub interface
        self.recognitionInterface = RecognitionInterface()
        self.previewInterface = PreviewInterface()
        self.historyInterface = Widget('To be finished...', self)
        self.settingInterface = SettingInterface()

        self.stackWidget.addWidget(self.recognitionInterface)
        self.stackWidget.addWidget(self.previewInterface)
        self.stackWidget.addWidget(self.historyInterface)
        self.stackWidget.addWidget(self.settingInterface)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.vBoxLayout.addWidget(self.navigationInterface)
        self.vBoxLayout.addWidget(self.stackWidget)
        self.vBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.recognitionInterface, FIF.FIT_PAGE, 'Formula Recognition')
        self.addSubInterface(self.previewInterface, FIF.COMMAND_PROMPT, 'Formula Preview')
        self.addSubInterface(self.historyInterface, FIF.HISTORY, 'History')
        # add item to bottom
        self.navigationInterface.addItem(
            routeKey='switch-theme',
            icon=FIF.CONSTRACT,
            text='Switch Theme',
            onClick=self.switchTheme,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)
        initialWidget = self.stackWidget.currentWidget()
        self.navigationInterface.setCurrentItem(initialWidget.objectName())

    def addSubInterface(self, w: QWidget, icon, text, position=NavigationItemPosition.TOP):
        self.stackWidget.addWidget(w)
        self.navigationInterface.addItem(
            routeKey=w.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(w),
            position=position
        )

    def initWindow(self):
        self.resize(600, 800)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle('Formulite')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.setQss()

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def switchTheme(self):
        newTheme = Theme.LIGHT if isDarkTheme() else Theme.DARK
        qconfig.set(qconfig.themeMode, newTheme)
        return False

    def onThemeChanged(self, theme: Theme):
        setTheme(theme)
        self.setQss()

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
