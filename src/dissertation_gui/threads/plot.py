import math
import time

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

from ..models.plot import PlotPoint


class ExamplePlotThread(QThread):
    my_signal = pyqtSignal(PlotPoint)

    def run(self) -> None:
        start_time = time.time()
        while True:
            now = time.time() - start_time
            value = math.sin(now)
            self.my_signal.emit(PlotPoint(time=now, value=value))  # noqa
            time.sleep(0.1)
