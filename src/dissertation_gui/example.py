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


class PlotManager:
    def __init__(self, graph_to_manage: PlotWidget):
        self.graph = graph_to_manage
        self.time_axis: deque[float] = deque(maxlen=100)
        self.values_axis: deque[float] = deque(maxlen=100)

    def update(self, point: PlotPoint):
        self.graph.clear()
        self.time_axis.append(point.time)
        self.values_axis.append(point.value)
        self.graph.plot(self.time_axis, self.values_axis)


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
plot_manager = PlotManager(graph)

if __name__ == '__main__':
    plot_thread.my_signal.connect(plot_manager.update)  # noqa
    plot_thread.start(priority=QThread.Priority.HighPriority)
    ui.show()
    exit(app.exec_())
