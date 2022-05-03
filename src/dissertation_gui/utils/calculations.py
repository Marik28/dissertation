from abc import abstractmethod, ABCMeta
from numbers import Number


class Solver(metaclass=ABCMeta):  # TODO вынести расчёты температуры из потока в этот класс

    @abstractmethod
    def reset_time(self):
        pass

    @abstractmethod
    def set_temperature(self, temperature: Number):
        pass

    @abstractmethod
    def set_interference_amplitude(self, amplitude: Number):
        pass

    @abstractmethod
    def set_interference_frequency(self):
        pass

    @abstractmethod
    def calculate_temperature(self, time: Number) -> Number:
        pass

    @abstractmethod
    def calculate_burst_noise(self) -> Number:
        pass

    @abstractmethod
    def calculate_sinusoidal_noise(self) -> Number:
        pass


class LinearSolver(Solver):
    pass
