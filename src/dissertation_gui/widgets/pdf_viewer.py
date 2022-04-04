# from pathlib import Path
# from typing import Union
#
# from PyQt5 import QtCore
# from PyQt5 import QtWebEngineWidgets
#
#  Example - https://gist.github.com/eyllanesc/7566bab2f8a91593c460015ee2151717
#
# class PdfViewer(QtWebEngineWidgets.QWebEngineView):
#     def load_pdf(self, filename: Union[str, Path]):
#         url = QtCore.QUrl.fromLocalFile(str(filename))
#         self.load(url)
#
#     def sizeHint(self):
#         return QtCore.QSize(640, 480)
