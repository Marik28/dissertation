import time
from collections import deque
from typing import List

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

    def clear(self):
        self._times.clear()
        self._values.clear()


# TODO: можно тут же отрисовывать рассчитанную температуру
class TemperaturePlotManager:
    def __init__(self, plot_widget: PlotWidget, max_points: int = 1000):
        self._plot_widget = plot_widget
        self._start_time = time.time()
        self._curves: List[CurveManager] = []
        # self._setpoint_curve = self._create_curve("Уставка", "g")
        self._measured_temp_curve = self._create_curve("Измеренная температура", "b", max_points=max_points)
        self._set_temp_curve = self._create_curve("Заданная температура", "r", max_points=10000)

    def _create_curve(self, name: str, color: str, width: int = 1, max_points: int = 1000) -> CurveManager:
        self._plot_widget.addLegend()
        curve = CurveManager(
            self._plot_widget.plot(name=name, pen=mkPen(color=color, width=width)),
            max_points,
        )
        self._curves.append(curve)
        return curve

    def _update_curve(self, curve: CurveManager, value: float):
        now = time.time() - self._start_time
        curve.update(now, value)

    def update_setpoint_curve(self, value: float):
        pass
        # self._update_curve(self._setpoint_curve, value)

    def update_measured_temp_curve(self, value: float):
        self._update_curve(self._measured_temp_curve, value)

    def update_set_temp_curve(self, value: float):
        self._update_curve(self._set_temp_curve, value)

    def clear(self):
        for curve in self._curves:
            curve.clear()
