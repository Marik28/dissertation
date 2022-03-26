from pathlib import Path
from typing import Union

from PyQt5 import QtCore
from PyQt5 import QtWebEngineWidgets


class PdfViewer(QtWebEngineWidgets.QWebEngineView):
    def load_pdf(self, filename: Union[str, Path]):
        url = QtCore.QUrl.fromLocalFile(filename)
        self.load(url)

    def sizeHint(self):
        return QtCore.QSize(640, 480)
