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
        self.sinusoidal_interference_enabled = False
        self.burst_interference_enabled = False

    def set_set_temperature(self, temperature: float):
        self.temperature = self.set_temperature
        self.set_temperature = temperature

    def set_interference_amplitude(self, amplitude: float):
        self.interference_amplitude = amplitude

    def set_interference_frequency(self, frequency: float):
        self.interference_frequency = frequency

    @abstractmethod
    def calculate_temperature(self, time: float) -> float:
        pass

    def calculate_burst_interference(self, time: float) -> float:
        pass

    def calculate_sinusoidal_interference(self, time: float) -> float:
        return self.interference_amplitude * math.sin(2 * math.pi * self.interference_frequency * time)


class LinearSolver(Solver):

    def calculate_temperature(self, time: float) -> float:
        direction = int(math.copysign(1, self.set_temperature - self.temperature))
        temperature = self.start_temperature + self.k * time * direction
        if self.burst_interference_enabled:
            interference = self.calculate_burst_interference(time)
        elif self.sinusoidal_interference_enabled:
            interference = self.calculate_sinusoidal_interference(time)
        else:
            interference = 0
        temperature += interference
        return temperature
