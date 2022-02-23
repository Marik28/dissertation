import time

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)


class TemperatureCalculationThread(QThread):
    my_signal = pyqtSignal(float)

    def __init__(self, parent=None, frequency: int = 10):
        """
        :param parent:
        :param frequency: Hz. Сколько раз в секунду пересчитывать
        """
        super().__init__(parent)
        self._update_period = 1 / frequency
        self._start_time = 0.
        self._k = 1.
        self._direction = 1
        self._temperature_limit = 25.
        self._temperature = 0.
        self._start_temperature = self._temperature

    def set_k_ratio(self, k: float) -> None:
        """Слот для изменения коэффициента 'k'"""
        self._k = k

    def change_direction(self, positive: bool) -> None:
        """Слот для изменения направления графика (положительное/отрицательное)"""
        if positive:
            self._direction = 1
        else:
            self._direction = -1

    def set_temperature_limit(self, new_limit) -> None:
        """Слот для изменения предела температуры"""
        self._temperature_limit = float(new_limit)
        if self._exceeds_limit():
            self._reset_start_time()
            self._reset_start_temperature()

    def run(self) -> None:
        self._reset_start_time()
        while True:
            now = time.time() - self._start_time
            self._temperature = self._start_temperature + self._k * now * self._direction

            if self._exceeds_limit():
                self._temperature = self._temperature_limit

            self.my_signal.emit(self._temperature)
            time.sleep(self._period)

    def _reset_start_time(self) -> None:
        self._start_time = time.time()

    def _direction_positive(self) -> bool:
        return self._direction == 1

    def _exceeds_limit(self) -> bool:
        if self._direction_positive():
            return self._temperature > self._temperature_limit
        else:
            return self._temperature < self._temperature_limit

    def _reset_start_temperature(self):
        self._start_temperature = self._temperature
