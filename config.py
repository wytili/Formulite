from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (QConfig, ConfigSerializer, OptionsConfigItem, OptionsValidator, qconfig,
                            ConfigItem, BoolValidator, EnumSerializer)


class Language(Enum):
    ENGLISH = QLocale(QLocale.English)
    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    AUTO = QLocale()

class API(Enum):
    SIMPLETEX = "SimpleTex"
    TENCENTCLOUD = "TencentCloud"
    ALIYUN = "Aliyun"

class LanguageSerializer(ConfigSerializer):
    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):

    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())

    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)

    apiService = OptionsConfigItem(
        "API", "Service", API.ALIYUN, OptionsValidator(API), EnumSerializer(API), restart=True)

    apiId = ConfigItem(
        "API", "ID", "")

    apiKey = ConfigItem(
        "API", "Key", "")


URL = "https://github.com/wytili/Formulite"
EMAIL = "wyt_0416@sjtu.edu.cn"
YEAR = 2024
AUTHOR = "wytili"
VERSION = "1.0"

cfg = Config()
qconfig.load('resource/config.json', cfg)
