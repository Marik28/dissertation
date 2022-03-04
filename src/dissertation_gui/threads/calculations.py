import time

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

from ..models.plot import PlotPoint


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

    def set_k_ratio(self, k: float) -> None:
        """Слот для изменения коэффициента 'k'"""
        self._k = float(k)
        self._reset_start_temperature()
        self._defer_reset_time()

    # fixme
    def set_temperature(self, new_set_temperature: float) -> None:
        """Слот для изменения заданной температуры"""
        _new_temperature = float(new_set_temperature)
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
        print(f"ДО:\t Направление - {self._direction}\t"
              f"Стартовая температура - {self._start_temperature}\t"
              f"Текущая температура - {self._temperature}")
        if self._direction_positive():
            if _new_temperature < self._temperature:
                print("зашел в 1")
                self._change_direction()
                self._defer_reset_time()
                self._reset_start_temperature()
            elif _new_temperature > self._temperature:
                self._defer_reset_time()
                self._reset_start_temperature()
                pass
        else:
            if _new_temperature > self._temperature:
                print("зашел в 2")
                self._change_direction()
                self._defer_reset_time()
                self._reset_start_temperature()
            elif _new_temperature < self._temperature:
                self._defer_reset_time()
                self._reset_start_temperature()
        print(f"ПОСЛЕ:\t Направление - {self._direction}\t"
              f"Стартовая температура - {self._start_temperature}\t"
              f"Текущая температура - {self._temperature}")

        # if _new_temperature > self._set_temperature and not self._direction_positive():
        #     self._change_direction()
        #     self._reset_start_time()
        #     self._reset_start_temperature()
        # elif _new_temperature < self._set_temperature and self._direction_positive():
        #     self._change_direction()
        #     self._reset_start_time()
        #     self._reset_start_temperature()

        self._set_temperature = _new_temperature

    # TODO протестировать
    def run(self) -> None:
        self._reset_start_time()
        pseudo_time = 0.
        while True:
            if self._reset_time_required():
                self._reset_start_time()
            now = time.time() - self._start_time
            self._temperature = self._start_temperature + self._k * now * self._direction

            if self._reached_set_temp():
                self._temperature = self._set_temperature

            self.temperature_signal.emit(PlotPoint(time=pseudo_time, value=self._temperature))
            pseudo_time += 1.
            time.sleep(self._update_period)

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
