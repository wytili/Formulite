from io import BytesIO
import latex2mathml.converter

import matplotlib.pyplot as plt
import matplotlib
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QAction, QApplication
from qfluentwidgets import (FluentIcon, PlainTextEdit, DropDownPushButton, RoundMenu, HeaderCardWidget,
                            isDarkTheme, InfoBar)
from qframelesswindow.webengine import FramelessWebEngineView
from PyQt5.QtGui import QFont, QImage, QPixmap

from config import cfg
matplotlib.rcParams["mathtext.fontset"] = "cm"


class PreviewInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Preview-Interface")
        layout = QVBoxLayout()
        self.inputCard = InputCard2()
        self.outputCard = OutputCard2()
        layout.addWidget(self.inputCard)
        layout.addWidget(self.outputCard)
        self.setLayout(layout)
        cfg.themeChanged.connect(self.updateTheme)

    def updateTheme(self):
        self.outputCard.updateLatex(self.outputCard.current_latex)

class InputCard2(HeaderCardWidget):
    def __init__(self):
        super().__init__()
        self.setTitle("Input")
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(15)
        contentLayout = QVBoxLayout()
        self.editBox = PlainTextEdit()
        self.editBox.setFont(font)

        self.editBox.textChanged.connect(self.updateLatexRender)

        contentLayout.addWidget(self.editBox)
        self.viewLayout.addLayout(contentLayout)

    def updateLatexRender(self):
        user_input = self.editBox.toPlainText().strip()
        formatted_input = "$$" + user_input + "$$"
        self.parent().outputCard.updateLatex(formatted_input)


class OutputCard2(HeaderCardWidget):
    def __init__(self):
        super().__init__()
        self.current_latex = None
        self.current_html = None
        self.setTitle("Output")
        contentLayout = QVBoxLayout()

        # WebEngine
        self.webView = FramelessWebEngineView(self)
        self.webView.setFixedHeight(230)
        contentLayout.addWidget(self.webView)
        self.viewLayout.addLayout(contentLayout)

        # init latex
        self.updateLatex("")

        buttonsLayout = QHBoxLayout()
        # buttons
        button1 = DropDownPushButton(FluentIcon.CODE, 'Copy Code')
        menu1 = RoundMenu()
        # copy latex
        latexAction = QAction('LaTex', self)
        latexAction.triggered.connect(self.copyLatex)
        menu1.addAction(latexAction)
        # copy html
        htmlAction = QAction('HTML', self)
        htmlAction.triggered.connect(self.copyHtml)
        menu1.addAction(htmlAction)

        button1.setMenu(menu1)
        buttonsLayout.addWidget(button1)

        button2 = DropDownPushButton(FluentIcon.IMAGE_EXPORT, 'Copy Image')
        menu2 = RoundMenu()

        # copy png
        pngAction = QAction('PNG', self)
        pngAction.triggered.connect(lambda: self.copyImage())
        menu2.addAction(pngAction)
        # copy jpg
        jpgAction = QAction('JPG', self)
        jpgAction.triggered.connect(lambda: self.copyImage())
        menu2.addAction(jpgAction)
        # copy svg
        svgAction = QAction('SVG', self)
        svgAction.triggered.connect(lambda: self.copyImage())
        menu2.addAction(svgAction)

        button2.setMenu(menu2)
        buttonsLayout.addWidget(button2)

        button3 = DropDownPushButton(FluentIcon.DOCUMENT, 'Copy Word')
        menu3 = RoundMenu()

        # copy mathml
        mathmlAction = QAction('MathML', self)
        mathmlAction.triggered.connect(self.copyMathML)
        menu3.addAction(mathmlAction)
        # copy word
        wordAction = QAction('Word', self)
        wordAction.triggered.connect(self.copyWord)
        menu3.addAction(wordAction)

        button3.setMenu(menu3)
        buttonsLayout.addWidget(button3)

        contentLayout.addLayout(buttonsLayout)

        self.viewLayout.addLayout(contentLayout)

    def updateLatex(self, latex_code):
        self.current_latex = latex_code

        background_color = "rgb(39, 39, 39)" if isDarkTheme() else "white"
        text_color = "white" if isDarkTheme() else "black"

        mathjax_url = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
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
                    enableMenu: false
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
        self.current_html = html_content
        self.webView.setHtml(html_content)

    def copyLatex(self):
        if self.current_latex:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_latex)
            self.successMessage("LaTex")
        else:
            self.warningMessage()

    def copyHtml(self):
        if self.current_latex:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_html)
            self.successMessage("HTML")
        else:
            self.warningMessage()

    @staticmethod
    def latex2image(latex_expression, image_size_in=(3, 0.5), fontsize=16, dpi=200):
        fig = plt.figure(figsize=image_size_in, dpi=dpi)
        fig.text(x=0.5, y=0.5, s=latex_expression, horizontalalignment='center', verticalalignment='center',
                 fontsize=fontsize)
        fig.canvas.draw()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        qimg = QImage()
        qimg.loadFromData(buf.getvalue(), 'PNG')
        pixmap = QPixmap.fromImage(qimg)

        return pixmap

    def copyImage(self):
        if not self.current_latex:
            self.warningMessage()
            return
        user_input = self.parent().inputCard.editBox.toPlainText().strip()
        latex = "$" + user_input + "$"
        pixmap = self.latex2image(latex, image_size_in=(3, 0.5))
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        self.successMessage("Image")

    def copyMathML(self):
        if self.current_latex:
            mathml_code = latex2mathml.converter.convert(self.current_latex)
            clipboard = QApplication.clipboard()
            clipboard.setText(mathml_code)
            self.successMessage("MathML")
        else:
            self.warningMessage()

    def copyWord(self):
        word_code = self.latexToWord(self.current_latex)
        clipboard = QApplication.clipboard()
        clipboard.setText(word_code)

    def warningMessage(self):
        InfoBar.warning(
            title='Empty',
            content="There is no content to copy.",
            parent=self.parent()
        ).show()

    def successMessage(self, content):
        InfoBar.success(
            title='Copied',
            content=f"{content} copied to clipboard.",
            parent=self.parent()
        ).show()
