from abc import abstractmethod, ABCMeta
from numbers import Number


class Solver(ABCMeta):  # TODO вынести расчёты температуры из потока в этот класс

    @abstractmethod
    def calculate_temperature(self) -> float:
        pass

    def set_temperature(self, new_temperature: Number):
        ...
