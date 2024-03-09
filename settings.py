from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon, QColor, QDesktopServices
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QHBoxLayout, QLabel, QButtonGroup, QPushButton
from qfluentwidgets import (ScrollArea, SettingCardGroup, OptionsSettingCard, SwitchSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, RadioButton, setTheme, setThemeColor, isDarkTheme,
                            LineEdit, PasswordLineEdit, ExpandGroupSettingCard, OptionsConfigItem,
                             Theme, ExpandLayout, ColorDialog, qconfig,
                            ColorConfigItem, FluentIconBase)
from qfluentwidgets import FluentIcon as FIF

from config import cfg, API, EMAIL, URL, AUTHOR, VERSION, YEAR


class SettingInterface(ScrollArea):

    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # Personalization group
        self.personalizationGroup = SettingCardGroup("Personalization", self.scrollWidget)

        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "Application theme",
            "Change the appearance of your application",
            texts=['Light', 'Dark', 'Use system setting'],
            parent=self.personalizationGroup
        )

        self.themeColorCard = ColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            parent=self.personalizationGroup
        )

        self.languageCard = OptionsSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            "Language",
            "Set your preferred language for UI",
            texts=['English', '简体中文', 'Use system setting'],
            parent=self.personalizationGroup
        )

        # Main Panel group
        self.mainPanelGroup = SettingCardGroup("Main Panel", self.scrollWidget)

        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            "Minimize to tray after closing",
            "Formulite will continue to run in the background",
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        # Configuration group
        self.configurationGroup = SettingCardGroup("Configuration", self.scrollWidget)
        self.apiConfigCard = APIConfigSettingCard(
            cfg.apiService,
            FIF.ROBOT,
            "API service",
            "Configure the API service for LaTeX recognition",
            parent=self.configurationGroup
        )

        # About group
        self.aboutGroup = SettingCardGroup("About", self.scrollWidget)
        self.helpCard = HyperlinkCard(
            URL,
            "Open help page",
            FIF.HELP,
            "Help",
            "Discover new features and learn useful tips about Formulite",
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            "Provide feedback",
            FIF.FEEDBACK,
            "Provide feedback",
            "Help us improve Formulite by providing feedback",
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            "Check update",
            FIF.INFO,
            "About",
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):

        # add cards to group
        self.personalizationGroup.addSettingCard(self.themeCard)
        self.personalizationGroup.addSettingCard(self.themeColorCard)
        self.personalizationGroup.addSettingCard(self.languageCard)
        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)
        self.configurationGroup.addSettingCard(self.apiConfigCard)
        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(20)
        self.expandLayout.setContentsMargins(60, 0, 60, 0)
        self.expandLayout.addWidget(self.personalizationGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)
        self.expandLayout.addWidget(self.configurationGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __onThemeChanged(self, theme: Theme):
        setTheme(theme)
        self.__setQss()

    def __setQss(self):
        self.scrollWidget.setObjectName('scrollWidget')
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{theme}/demo.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(self.__onThemeChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)
    #     self.languageCard.optionChanged.connect(self.onLanguageChanged)
        self.minimizeToTrayCard.checkedChanged.connect(self.minimizeToTrayChanged)
        self.feedbackCard.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(f"mailto:{EMAIL}?subject=Formulite%20Feedback&body=Here%20is%20my%20feedback%20about"
                 "%20Formulite: ")))
        self.aboutCard.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(URL)))

class APIConfigSettingCard(ExpandGroupSettingCard):
    def __init__(self, configItem: OptionsConfigItem, icon: Union[str, QIcon], title: str, content=None, parent=None):
        super().__init__(icon, title, content, parent=parent)
        self.configItem = configItem
        self.configName = configItem.name

        self.choiceLabel = QLabel(self)

        self.radioWidget = QWidget(self.view)
        self.radioLayout = QVBoxLayout(self.radioWidget)
        self.apiButton1 = RadioButton(self.tr('SimpleTex'), self.radioWidget)
        self.apiButton2 = RadioButton(self.tr('TencentCloud'), self.radioWidget)
        self.apiButton3 = RadioButton(self.tr('AliYun'), self.radioWidget)
        self.buttonGroup = QButtonGroup(self)

        self.apiInfoWidget = QWidget(self.view)
        self.apiInfoLayout = QHBoxLayout(self.apiInfoWidget)

        self.apiIdLabel = QLabel('API Id :', self.apiInfoWidget)
        self.apiKeyLabel = QLabel('API Key :', self.apiInfoWidget)
        self.apiIdInput = LineEdit(self.apiInfoWidget)
        self.apiKeyInput = PasswordLineEdit(self.apiInfoWidget)
        self.apiIdInput.setPlaceholderText("API Id")
        self.apiKeyInput.setPlaceholderText("API Key")

        self.__initWidget(self.configItem)

    def __initWidget(self, configItem: OptionsConfigItem):
        self.__initLayout()

        self.apiButton1.setChecked(True)
        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())
        self.choiceLabel.adjustSize()

        self.apiIdInput.setText(cfg.apiId.value)
        self.apiKeyInput.setText(cfg.apiKey.value)

        # Connect signals
        self.setValue(cfg.get(self.configItem))
        self.configItem.valueChanged.connect(self.setValue)
        self.apiIdInput.textChanged.connect(self.__onApiIdTextChanged)
        self.apiKeyInput.textChanged.connect(self.__onApiKeyTextChanged)
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __initLayout(self):
        self.addWidget(self.choiceLabel)

        # Setup radio button layout
        self.radioLayout.setSpacing(15)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 15, 0, 15)
        self.buttonGroup.addButton(self.apiButton1)
        self.buttonGroup.addButton(self.apiButton2)
        self.buttonGroup.addButton(self.apiButton3)
        self.radioLayout.addWidget(self.apiButton1)
        self.radioLayout.addWidget(self.apiButton2)
        self.radioLayout.addWidget(self.apiButton3)
        self.apiButton1.setProperty(self.configName, API.SIMPLETEX)
        self.apiButton2.setProperty(self.configName, API.TENCENTCLOUD)
        self.apiButton3.setProperty(self.configName, API.ALIYUN)
        self.radioLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        # Setup custom color layout
        self.apiInfoLayout.setContentsMargins(20, 15, 20, 15)
        self.apiInfoLayout.addWidget(self.apiIdLabel, 0)
        self.apiInfoLayout.addWidget(self.apiIdInput, 0)
        self.apiInfoLayout.addWidget(self.apiKeyLabel, 0)
        self.apiInfoLayout.addWidget(self.apiKeyInput, 0)
        self.apiInfoLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        # Add widgets to the main view layout
        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.addGroupWidget(self.radioWidget)
        self.addGroupWidget(self.apiInfoWidget)

    def __onButtonClicked(self, button: RadioButton):
        if button.text() == self.choiceLabel.text():
            return

        value = button.property(self.configName)
        cfg.set(self.configItem, value)
        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()

    def __onApiIdTextChanged(self, text: str):
        cfg.set(cfg.apiId, text)

    def __onApiKeyTextChanged(self, text: str):
        cfg.set(cfg.apiKey, text)

    def setValue(self, value):
        """ select button according to the value """
        cfg.set(self.configItem, value)
        for button in self.buttonGroup.buttons():
            isChecked = button.property(self.configName) == value
            button.setChecked(isChecked)

            if isChecked:
                self.choiceLabel.setText(button.text())
                self.choiceLabel.adjustSize()


class ColorSettingCard(ExpandGroupSettingCard):

    colorChanged = pyqtSignal(QColor)

    def __init__(self, configItem: ColorConfigItem, icon: Union[str, QIcon, FluentIconBase], title: str,
                 content=None, parent=None, enableAlpha=False):

        super().__init__(icon, title, content, parent=parent)
        self.enableAlpha = enableAlpha
        self.configItem = configItem
        self.defaultColor = QColor("#0078d4")
        self.customColor = QColor(qconfig.get(configItem))

        self.choiceLabel = QLabel(self)

        self.radioWidget = QWidget(self.view)
        self.radioLayout = QVBoxLayout(self.radioWidget)
        self.defaultRadioButton = RadioButton(
            self.tr('Default color'), self.radioWidget)
        self.customRadioButton = RadioButton(
            self.tr('Custom color'), self.radioWidget)
        self.buttonGroup = QButtonGroup(self)

        self.customColorWidget = QWidget(self.view)
        self.customColorLayout = QHBoxLayout(self.customColorWidget)
        self.customLabel = QLabel(
            self.tr('Custom color'), self.customColorWidget)
        self.chooseColorButton = QPushButton(
            self.tr('Choose color'), self.customColorWidget)

        self.__initWidget()

    def __initWidget(self):
        self.__initLayout()

        if self.defaultColor != self.customColor:
            self.customRadioButton.setChecked(True)
            self.chooseColorButton.setEnabled(True)
        else:
            self.defaultRadioButton.setChecked(True)
            self.chooseColorButton.setEnabled(False)

        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())
        self.choiceLabel.adjustSize()

        self.chooseColorButton.setObjectName('chooseColorButton')

        self.buttonGroup.buttonClicked.connect(self.__onRadioButtonClicked)
        self.chooseColorButton.clicked.connect(self.__showColorDialog)

    def __initLayout(self):
        self.addWidget(self.choiceLabel)

        self.radioLayout.setSpacing(19)
        self.radioLayout.setAlignment(Qt.AlignTop)
        self.radioLayout.setContentsMargins(48, 18, 0, 18)
        self.buttonGroup.addButton(self.customRadioButton)
        self.buttonGroup.addButton(self.defaultRadioButton)
        self.radioLayout.addWidget(self.customRadioButton)
        self.radioLayout.addWidget(self.defaultRadioButton)
        self.radioLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.customColorLayout.setContentsMargins(48, 18, 44, 18)
        self.customColorLayout.addWidget(self.customLabel, 0, Qt.AlignLeft)
        self.customColorLayout.addWidget(self.chooseColorButton, 0, Qt.AlignRight)
        self.customColorLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.viewLayout.setSpacing(0)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.addGroupWidget(self.radioWidget)
        self.addGroupWidget(self.customColorWidget)

    def __onRadioButtonClicked(self, button: RadioButton):
        """ radio button clicked slot """
        if button.text() == self.choiceLabel.text():
            return

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()

        if button is self.defaultRadioButton:
            self.chooseColorButton.setDisabled(True)
            qconfig.set(self.configItem, self.defaultColor)
            if self.defaultColor != self.customColor:
                self.colorChanged.emit(self.defaultColor)
        else:
            self.chooseColorButton.setDisabled(False)
            qconfig.set(self.configItem, self.customColor)
            if self.defaultColor != self.customColor:
                self.colorChanged.emit(self.customColor)

    def __showColorDialog(self):
        """ show color dialog """
        w = ColorDialog(
            qconfig.get(self.configItem), self.tr('Choose color'), self.window(), self.enableAlpha)
        w.colorChanged.connect(self.__onCustomColorChanged)
        w.exec()

    def __onCustomColorChanged(self, color):
        """ custom color changed slot """
        qconfig.set(self.configItem, color)
        self.customColor = QColor(color)
        self.colorChanged.emit(color)



