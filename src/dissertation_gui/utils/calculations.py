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
        self.self_oscillations_enabled = True

    def set_self_oscillations(self, mode: bool):
        self.self_oscillations_enabled = mode

    def set_direction(self, direction: int):
        self.direction = direction
        self.reset_start_temperature()

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

    def set_setpoint(self, temperature: float):
        if temperature == self.setpoint:
            return
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

    def reached_set_temperature(self) -> bool:
        if self.direction_positive():
            return self.temperature > self.setpoint + self.hysteresis + self.k
        else:
            return self.temperature < self.setpoint - self.hysteresis - self.k

    def calculate_temperature(self, time: float) -> float:
        self.temperature = self.start_temperature + self.k * time * self.direction
        return self.temperature


class SquareSolver(LinearSolver):
    def calculate_temperature(self, time: float) -> float:
        return super().calculate_temperature(time) ** 2


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

    def __init__(self):
        super().__init__()

    def calculate_interference(self, time: float) -> float:
        interference = self._amplitude * math.sin(2 * math.pi * self._frequency * time)
        if abs(self._amplitude - interference) <= (0.05 * self._amplitude):
            return interference
        return 0.0


class ControlLogic(metaclass=ABCMeta):

    def __init__(self, init_output: int = 1):
        self._output = init_output
        """Состояние выхода ТРМ-а"""

    def set_output(self, output: int):
        self._output = output

    @abstractmethod
    def calculate_direction(self, solver: "Solver") -> None:
        pass


class NoControlLogic(ControlLogic):
    """Отсутствие управления"""

    def calculate_direction(self, solver: "Solver") -> None:
        pass


class ReversedControlLogic(ControlLogic):
    """Обратное управление (холодильник)"""

    def calculate_direction(self, solver: "Solver") -> None:
        direction = -1 if self._output else 1
        if direction == solver.direction:
            return
        solver.set_direction(direction)


class DirectControlLogic(ControlLogic):
    """Прямое управление - (нагреватель)"""

    def calculate_direction(self, solver: "Solver") -> None:
        direction = 1 if self._output else -1
        if direction == solver.direction:
            return
        solver.set_direction(direction)


class PShapedControlLogic(ControlLogic):
    """П-образная"""

    def calculate_direction(self, solver: "Solver") -> None:
        pass


class UShapedControlLogic(ControlLogic):
    """U-образная"""

    def calculate_direction(self, solver: "Solver") -> None:
        pass
