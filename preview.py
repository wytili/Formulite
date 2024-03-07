from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QAction)
from qfluentwidgets import FluentIcon, PlainTextEdit, DropDownPushButton, RoundMenu, \
                        HeaderCardWidget, PrimaryPushButton, Theme
from qframelesswindow.webengine import FramelessWebEngineView
from PyQt5.QtGui import QFont
class PreviewInterface(QWidget):
    def __init__(self, theme):
        super().__init__()
        self.setObjectName("Preview-Interface")
        layout = QVBoxLayout()
        self.inputCard = InputCard2()
        self.outputCard = OutputCard2(theme)
        layout.addWidget(self.inputCard)
        layout.addWidget(self.outputCard)
        self.setLayout(layout)

class InputCard2(HeaderCardWidget):
    def __init__(self):
        super().__init__()
        self.setTitle("Input")
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        contentLayout = QVBoxLayout()
        self.editBox = PlainTextEdit()
        self.editBox.setFont(font)
        self.previewButton = PrimaryPushButton(FluentIcon.SEARCH, 'Preview')
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.previewButton, 0, Qt.AlignCenter)
        self.previewButton.setFixedWidth(150)
        contentLayout.addWidget(self.editBox)
        contentLayout.addLayout(buttonLayout)
        self.viewLayout.addLayout(contentLayout)


class OutputCard2(HeaderCardWidget):
    def __init__(self, theme):
        super().__init__()
        self.setTitle("Output")
        self.theme = theme
        contentLayout = QVBoxLayout()

        # WebEngine
        self.webView = FramelessWebEngineView(self)
        self.webView.setFixedHeight(230)
        contentLayout.addWidget(self.webView)
        self.viewLayout.addLayout(contentLayout)

        # init latex
        # self.updateLatex("$f(x) = \\int_{0}^{x} e^{-t^2} dt$")
        self.updateLatex("""
        $$f(x) = \\begin{cases} x^2 & \\text{if } x \\geq 0 \\\\-x & \\text{if } x < 0 \\end{cases}$$
        $$f(x) = \\int_{0}^{x} e^{-t^2} dt$$
        """)

        buttonsLayout = QHBoxLayout()
        # buttons
        button1 = DropDownPushButton(FluentIcon.CODE, 'Copy Code')
        menu1 = RoundMenu()
        menu1.addAction(QAction('LaTex', self))
        menu1.addAction(QAction('HTML', self))
        button1.setMenu(menu1)
        buttonsLayout.addWidget(button1)

        button2 = DropDownPushButton(FluentIcon.IMAGE_EXPORT, 'Copy Image')
        menu2 = RoundMenu()
        menu2.addAction(QAction('PNG', self))
        menu2.addAction(QAction('JPG', self))
        menu2.addAction(QAction('SVG', self))
        button2.setMenu(menu2)
        buttonsLayout.addWidget(button2)

        button3 = DropDownPushButton(FluentIcon.DOCUMENT, 'Copy Word')
        menu3 = RoundMenu()
        menu3.addAction(QAction('Word', self))
        menu3.addAction(QAction('MathML', self))
        button3.setMenu(menu3)
        buttonsLayout.addWidget(button3)

        contentLayout.addLayout(buttonsLayout)

        self.viewLayout.addLayout(contentLayout)

    def updateLatex(self, latex_code):
        mathjax_url = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
        if self.theme == Theme.DARK:
            background_color = "rgb(39, 39, 39)"
            text_color = "white"
        else:
            background_color = "white"
            text_color = "black"

        html_content = f"""
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="{mathjax_url}"></script>
            <script>
            MathJax = {{
                tex: {{
                    inlineMath: [ ['$','$'], ["\\(","\\)"] ],
                    displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
                    processEscapes: true,
                    processEnvironments: true,
                }},
                chtml: {{
                    displayAlign: "center",
                }},
                options: {{
                    enableMenu: True
                }},
            }};
            </script>
            <style>
                body {{
                    font-size: 25px; 
                    background-color: {background_color}; 
                     color: {text_color}; 
                }}
            </style>
        </head>
        <body>
            <p>{latex_code}</p>
        </body>
        </html>
        """
        self.webView.setHtml(html_content)
