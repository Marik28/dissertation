import time
from typing import Dict

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

from ..models.interference import InterferenceMode
from ..utils.calculations import (
    Solver,
    ControlLogic,
    InterferenceSolver,
)

__all__ = ["TemperatureCalculationThread"]


class TemperatureCalculationThread(QThread):
    temperature_signal = pyqtSignal(float)

    def __init__(self,
                 solver: Solver,
                 control_logic: Dict[int, ControlLogic],
                 interferences: Dict[InterferenceMode, InterferenceSolver],
                 frequency: int = 100,
                 parent=None):
        """
        :param solver: Объект, симулирующий изменение температуры
        :param parent:
        :param frequency: Hz. Сколько раз в секунду пересчитывать
        """
        super().__init__(parent)
        self._solver = solver
        self._interferences = interferences
        self._interference = interferences[InterferenceMode.NO]
        self._control_logic_dict = control_logic
        self._control_logic = control_logic[0]
        self._update_period = 1 / frequency
        """Частота обновления температуры"""
        self._start_time = 0.
        """Время с начала процесса"""
        self._reset = False
        """Флаг, сигнализирущий о том, что необходимо сбросить начальное время"""

    def set_k_ratio(self, k: float) -> None:
        """Слот для изменения коэффициента, задающего быстроту изменения температуры"""
        self._solver.set_k_ratio(k)
        self._defer_reset_time()

    def set_interference_amplitude(self, amplitude: float):
        for interference in self._interferences.values():
            interference.set_amplitude(amplitude)

    def set_interference_frequency(self, frequency: float):
        for interference in self._interferences.values():
            interference.set_frequency(frequency)

    def now(self):
        """Время со старта нового процесса симуляции"""
        return time.time() - self._start_time

    def set_control_logic(self, code: int):
        self._control_logic = self._control_logic_dict[code]

    def set_interference_mode(self, mode: InterferenceMode):
        self._interference = self._interferences[mode]

    def set_temperature(self, temperature: float) -> None:
        """Слот для изменения заданной температуры"""
        self._solver.set_set_temperature(temperature)
        self._defer_reset_time()

    def run(self) -> None:
        self._reset_start_time()
        while True:
            if self._reset_time_required():
                self._reset_start_time()
            now = self.now()
            temperature = self._solver.calculate_temperature(now)
            interference = self._interference.calculate_interference(now)
            control_signal = self._control_logic.calculate_control_signal(now)
            self.temperature_signal.emit(temperature + control_signal + interference)  # noqa
            time.sleep(self._update_period)

    def _defer_reset_time(self):
        self._reset = True

    def _reset_time_required(self) -> bool:
        return self._reset

    def _reset_start_time(self) -> None:
        self._start_time = time.time()
        self._reset = False
