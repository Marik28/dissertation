import math
from abc import (
    abstractmethod,
    ABCMeta,
)


class Solver(metaclass=ABCMeta):

    def __init__(
            self,
            k: float,
            start_temperature: float,
            setpoint: float,
            hysteresis: float,
    ):
        self.k = k
        self.start_temperature = start_temperature
        self.temperature = start_temperature
        self.setpoint = setpoint
        self.hysteresis = hysteresis
        self.direction = 1

    def set_k_ratio(self, k: float):
        self.k = k
        self.start_temperature = self.temperature

    def direction_positive(self) -> bool:
        return self.direction == 1

    def reached_set_temperature(self) -> bool:
        if self.direction_positive():
            return self.temperature > self.setpoint
        else:
            return self.temperature < self.setpoint

    def set_set_temperature(self, temperature: float):
        self.reset_start_temperature()
        self.setpoint = temperature

    def reset_start_temperature(self):
        self.start_temperature = self.temperature

    def set_hysteresis(self, hysteresis: float):
        self.hysteresis = hysteresis

    @abstractmethod
    def calculate_temperature(self, time: float) -> float:
        pass


class LinearSolver(Solver):

    def calculate_temperature(self, time: float) -> float:
        self.direction = int(math.copysign(1, self.setpoint - self.temperature))
        self.temperature = self.start_temperature + self.k * time * self.direction

        if self.reached_set_temperature():
            self.temperature = self.setpoint

        return self.temperature


class InterferenceSolver(metaclass=ABCMeta):

    def __init__(self):
        self._amplitude = 1.
        self._frequency = 1.

    def set_frequency(self, frequency: float):
        self._frequency = frequency

    def set_amplitude(self, amplitude: float):
        self._amplitude = amplitude

    @abstractmethod
    def calculate_interference(self, time: float) -> float:
        pass


class NoInterferenceSolver(InterferenceSolver):
    def calculate_interference(self, time: float) -> float:
        return 0.0


class SinusoidalInterferenceSolver(InterferenceSolver):
    def calculate_interference(self, time: float) -> float:
        return self._amplitude * math.sin(2 * math.pi * self._frequency * time)


class BurstInterferenceSolver(InterferenceSolver):
    def calculate_interference(self, time: float) -> float:
        return 0.0  # TODO: реализовать


class ControlLogic(metaclass=ABCMeta):

    def __init__(self, init_output: int = 1):
        self._output = init_output
        """Состояние выхода ТРМ-а"""

    def set_output(self, output: int):
        self._output = output

    @abstractmethod
    def calculate_control_signal(self, time: float) -> float:
        pass


class NoControlLogic(ControlLogic):
    """Отсутствие управления"""

    def calculate_control_signal(self, time: float) -> float:
        return 0.


class ReversedControlLogic(ControlLogic):
    """Обратное управление"""

    def calculate_control_signal(self, time: float) -> float:
        return -1.


class DirectControlLogic(ControlLogic):
    """Прямое управление"""

    def calculate_control_signal(self, time: float) -> float:
        return 1.


class PShapedControlLogic(ControlLogic):
    """П-образная"""

    def calculate_control_signal(self, time: float) -> float:
        return 0.


class UShapedControlLogic(ControlLogic):
    """U-образная"""

    def calculate_control_signal(self, time: float) -> float:
        return 0.
