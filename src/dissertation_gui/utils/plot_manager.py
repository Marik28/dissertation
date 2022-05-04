import time
from collections import deque

from loguru import logger
from pyqtgraph import (
    PlotWidget,
    PlotDataItem,
    mkPen,
)

from ..models.plot import PlotPoint

__all__ = ["TemperaturePlotManager", "PlotManager"]


class PlotManager:
    def __init__(self, graph_to_manage: PlotWidget, max_points: int = 100):
        self._graph = graph_to_manage
        self._time_axis: deque[float] = deque(maxlen=max_points)
        self._values_axis: deque[float] = deque(maxlen=max_points)

    def update_graph(self, point: PlotPoint):
        self._graph.clear()
        self._time_axis.append(point.time)
        self._values_axis.append(point.value)
        self._graph.plot(self._time_axis, self._values_axis)


class CurveManager:
    def __init__(self, curve: PlotDataItem, max_points: int):
        self._curve = curve
        self._values: deque[float] = deque(maxlen=max_points)
        self._times: deque[float] = deque(maxlen=max_points)

    def update(self, time: float, value: float):
        self._times.append(time)
        self._values.append(value)
        self._curve.setData(self._times, self._values)
        self._curve.appendData()


# TODO: можно тут же отрисовывать рассчитанную температуру
class TemperaturePlotManager:
    def __init__(self, plot_widget: PlotWidget, max_points: int = 1000):
        self._plot_widget = plot_widget
        self._max_points = max_points
        self._start_time = time.time()
        self._setpoint_curve = self._create_curve("Уставка", "g")
        self._measured_temp_curve = self._create_curve("Измеренная температура", "b")
        self._set_temp_curve = self._create_curve("Заданная температура", "r")

    def _create_curve(self, name: str, color: str, width: int = 1) -> CurveManager:
        self._plot_widget.addLegend()
        return CurveManager(
            self._plot_widget.plot(name=name, pen=mkPen(color=color, width=width)),
            self._max_points,
        )

    def _update_curve(self, curve: CurveManager, value: float):
        now = time.time() - self._start_time
        curve.update(now, value)

    def update_setpoint_curve(self, value: float):
        self._update_curve(self._setpoint_curve, value)

    def update_measured_temp_curve(self, value: float):
        self._update_curve(self._measured_temp_curve, value)

    def update_set_temp_curve(self, value: float):
        self._update_curve(self._set_temp_curve, value)
