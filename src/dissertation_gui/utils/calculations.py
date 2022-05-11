import math
from abc import abstractmethod, ABCMeta


class Solver(metaclass=ABCMeta):  # TODO учитывать логику компаратора ТРМ-а

    def __init__(
            self,
            k: float,
            start_temperature: float,
            set_temperature: float,
            interference_amplitude: float,
            interference_frequency: float,
    ):
        self.k = k
        self.start_temperature = start_temperature
        self.temperature = start_temperature
        self.set_temperature = set_temperature
        self.interference_amplitude = interference_amplitude
        self.interference_frequency = interference_frequency
        self.sinusoidal_interference_enabled = False
        self.burst_interference_enabled = False
        self.direction = 1

    def set_k_ratio(self, k: float):
        self.k = k
        self.start_temperature = self.temperature

    def direction_positive(self) -> bool:
        return self.direction == 1

    def reached_set_temperature(self) -> bool:
        if self.direction_positive():
            return self.temperature > self.set_temperature
        else:
            return self.temperature < self.set_temperature

    def set_sinusoidal_interference_enabled(self, value: bool):
        self.sinusoidal_interference_enabled = value

    def set_burst_interference_enabled(self, value: bool):
        self.burst_interference_enabled = value

    def set_set_temperature(self, temperature: float):
        self.reset_start_temperature()
        self.set_temperature = temperature

    def set_interference_amplitude(self, amplitude: float):
        self.interference_amplitude = amplitude

    def set_interference_frequency(self, frequency: float):
        self.interference_frequency = frequency

    def reset_start_temperature(self):
        self.start_temperature = self.temperature

    @abstractmethod
    def calculate_temperature(self, time: float) -> float:
        pass

    def calculate_burst_interference(self, time: float) -> float:  # TODO: реализовать
        return 0.0

    def calculate_sinusoidal_interference(self, time: float) -> float:
        return self.interference_amplitude * math.sin(2 * math.pi * self.interference_frequency * time)


class LinearSolver(Solver):

    def calculate_temperature(self, time: float) -> float:
        self.direction = int(math.copysign(1, self.set_temperature - self.temperature))
        self.temperature = self.start_temperature + self.k * time * self.direction

        if self.reached_set_temperature():
            self.temperature = self.set_temperature

        if self.burst_interference_enabled:
            interference = self.calculate_burst_interference(time)
        elif self.sinusoidal_interference_enabled:
            interference = self.calculate_sinusoidal_interference(time)
        else:
            interference = 0
        return self.temperature + interference


class ControlLogic(metaclass=ABCMeta):

    def __init__(self, init_output: int = 1):
        self._output = init_output
        """Состояние выхода ТРМ-а"""

    def set_output(self, output: int):
        self._output = output


class NoControlLogic(ControlLogic):
    """Отсутствие управления"""


class ReversedControlLogic(ControlLogic):
    """Обратное управление"""


class DirectControlLogic(ControlLogic):
    """Прямое управление"""


class PShapedControlLogic(ControlLogic):
    """П-образная"""


class UShapedControlLogic(ControlLogic):
    """U-образная"""
