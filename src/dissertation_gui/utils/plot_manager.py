from collections import deque

from pyqtgraph import PlotWidget

from ..models.plot import PlotPoint


class PlotManager:
    def __init__(self, graph_to_manage: PlotWidget, plot_length: int = 100):
        self._graph = graph_to_manage
        self._time_axis: deque[float] = deque(maxlen=plot_length)
        self._values_axis: deque[float] = deque(maxlen=plot_length)

    def update_graph(self, point: PlotPoint):
        self._graph.clear()
        self._time_axis.append(point.time)
        self._values_axis.append(point.value)
        self._graph.plot(self._time_axis, self._values_axis)
