import math
from abc import abstractmethod, ABCMeta


class Solver(metaclass=ABCMeta):  # TODO вынести расчёты температуры из потока в этот класс

    def __init__(self,
                 k: float,
                 start_temperature: float,
                 interference_amplitude: float,
                 interference_frequency: float,
                 set_temperature: float):
        self.k = k
        self.start_temperature = start_temperature
        self.temperature = start_temperature
        self.interference_amplitude = interference_amplitude
        self.interference_frequency = interference_frequency
        self.set_temperature = set_temperature
        self.direction = 1

    def set_set_temperature(self, temperature: float):
        self.set_temperature = temperature

    def set_interference_amplitude(self, amplitude: float):
        self.interference_amplitude = amplitude

    def set_interference_frequency(self, frequency: float):
        self.interference_frequency = frequency

    @abstractmethod
    def calculate_temperature(self, time: float) -> float:
        pass

    def calculate_burst_noise(self) -> float:
        pass

    def calculate_sinusoidal_noise(self, time: float) -> float:
        return self.interference_amplitude * math.sin(2 * math.pi * self.interference_frequency * time)


class LinearSolver(Solver):

    def calculate_temperature(self, time: float) -> float:
        self.direction = int(math.copysign(1, self.set_temperature - self.temperature))
        return self.start_temperature + self.k * time * self.direction
