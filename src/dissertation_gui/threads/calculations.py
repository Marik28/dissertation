import time

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

from ..utils.calculations import Solver

__all__ = ["TemperatureCalculationThread"]


class TemperatureCalculationThread(QThread):
    temperature_signal = pyqtSignal(float)

    def __init__(self, solver: Solver, frequency: int = 100, parent=None):
        """
        :param solver: Объект, симулирующий изменение температуры
        :param parent:
        :param frequency: Hz. Сколько раз в секунду пересчитывать
        """
        super().__init__(parent)
        self.solver = solver
        self._update_period = 1 / frequency
        """Частота обновления температуры"""
        self._start_time = 0.
        """Время с начала процесса"""
        self._reset = False
        """Флаг, сигнализирущий о том, что необходимо сбросить начальное время"""

    def set_k_ratio(self, k: float) -> None:
        """Слот для изменения коэффициента, задающего быстроту изменения температуры"""
        self.solver.set_k_ratio(k)
        self._defer_reset_time()

    def now(self):
        """Время со старта нового процесса симуляции"""
        return time.time() - self._start_time

    def set_temperature(self, temperature: float) -> None:
        """Слот для изменения заданной температуры"""
        self.solver.set_set_temperature(temperature)
        self._defer_reset_time()

    def run(self) -> None:
        self._reset_start_time()
        while True:
            if self._reset_time_required():
                self._reset_start_time()
            now = self.now()
            temperature = self.solver.calculate_temperature(now)
            self.temperature_signal.emit(temperature)  # noqa
            time.sleep(self._update_period)

    def _defer_reset_time(self):
        self._reset = True

    def _reset_time_required(self) -> bool:
        return self._reset

    def _reset_start_time(self) -> None:
        self._start_time = time.time()
        self._reset = False
