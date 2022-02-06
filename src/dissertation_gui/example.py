import math
import time
from collections import deque

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
)
from PyQt5.uic import loadUi
from pyqtgraph.widgets.PlotWidget import PlotWidget

from .models.plot import PlotPoint
from .settings import settings

time_axis: deque[float] = deque(maxlen=100)
values_axis: deque[float] = deque(maxlen=100)


class PlotThread(QThread):
    my_signal = pyqtSignal(PlotPoint)

    def run(self) -> None:
        start_time = time.time()
        while True:
            now = time.time() - start_time
            value = math.sin(now)
            self.my_signal.emit(PlotPoint(time=now, value=value))  # noqa
            time.sleep(0.1)


app = QApplication([])
ui: QMainWindow = loadUi(settings.base_dir / "dissertation_gui" / "main_window.ui")
plot_thread = PlotThread()
tab_menu: QTabWidget = ui.tab_menu
graph: PlotWidget = ui.graph


def update_graph(point: PlotPoint):
    graph.clear()
    time_axis.append(point.time)
    values_axis.append(point.value)
    graph.plot(time_axis, values_axis)


if __name__ == '__main__':
    plot_thread.my_signal.connect(update_graph)  # noqa
    plot_thread.start(priority=QThread.Priority.HighPriority)
    ui.show()
    exit(app.exec_())
