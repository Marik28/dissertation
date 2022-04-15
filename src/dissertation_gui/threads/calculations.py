import random
import time

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

from ..models.plot import PlotPoint

# st - set temp
# nt - new temp
# ct - current temp
# d - direction
# 1. d+; nt > st; nt > ct; всё ок
# 2. d+; nt > st; nt < ct; не бывает
# 3. d+; nt < st; nt > ct; всё ок
# 4. d+; nt < st; nt < ct; d = -d
# 5. d-; nt > st; nt > ct; d = -d
# 6. d-; nt > st; nt < ct;
# 7. d-; nt < st; nt < ct;
# 8. d-; nt < st; nt > ct;

# TODO: функции отправки рассчитанного значения нужному устройству и переключение устройств
#  можно вынести вынести в воркер, который будет находиться в отдельном потоке
#  https://stackoverflow.com/questions/35527439/pyqt4-wait-in-thread-for-user-input-from-gui/35534047#35534047
__all__ = ["TemperatureCalculationThread"]


class TemperatureCalculationThread(QThread):
    temperature_signal = pyqtSignal(PlotPoint)

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
        self._set_temperature = 25.
        self._temperature = 0.
        self._start_temperature = self._temperature
        self._reset = False
        self._enable_bursts = False

    def set_enable_bursts(self, new_val: int):
        self._enable_bursts = bool(new_val)

    def bursts_enabled(self) -> bool:
        return self._enable_bursts

    def set_k_ratio(self, k: float) -> None:
        """Слот для изменения коэффициента 'k'"""
        self._k = float(k)
        self._reset_start_temperature()
        self._defer_reset_time()

    def set_temperature(self, new_set_temperature: float) -> None:
        """Слот для изменения заданной температуры"""
        _new_temperature = float(new_set_temperature)
        if self._direction_positive():
            if _new_temperature < self._temperature:
                self._change_direction()
                self._defer_reset_time()
                self._reset_start_temperature()
            elif _new_temperature > self._temperature:
                self._defer_reset_time()
                self._reset_start_temperature()
                pass
        else:
            if _new_temperature > self._temperature:
                self._change_direction()
                self._defer_reset_time()
                self._reset_start_temperature()
            elif _new_temperature < self._temperature:
                self._defer_reset_time()
                self._reset_start_temperature()
        self._set_temperature = _new_temperature

    # TODO протестировать
    def run(self) -> None:
        thread_start_time = time.time()
        self._reset_start_time()
        while True:
            if self._reset_time_required():
                self._reset_start_time()
            self._temperature = self.calculate_temperature()

            if self._reached_set_temp():
                self._temperature = self._set_temperature
            # TODO: реализовать помехи
            if self.bursts_enabled():
                burst = random.choice([1, -1]) * random.random() * 2
                self.temperature_signal.emit(
                    PlotPoint(
                        time=time.time() - thread_start_time,
                        value=self._temperature * burst),
                )

            self.temperature_signal.emit(PlotPoint(time=time.time() - thread_start_time, value=self._temperature))
            time.sleep(self._update_period)

    def calculate_temperature(self) -> float:
        now = time.time() - self._start_time
        return self._start_temperature + self._k * now * self._direction

    def _defer_reset_time(self):
        self._reset = True

    def _reset_time_required(self) -> bool:
        return self._reset

    def _change_direction(self) -> None:
        """Изменяет направление графика на противоположное"""
        self._direction = -self._direction

    def _reset_start_time(self) -> None:
        self._start_time = time.time()
        self._reset = False

    def _direction_positive(self) -> bool:
        return self._direction == 1

    def _reached_set_temp(self) -> bool:
        if self._direction_positive():
            return self._temperature > self._set_temperature
        else:
            return self._temperature < self._set_temperature

    def _reset_start_temperature(self):
        self._start_temperature = self._temperature
