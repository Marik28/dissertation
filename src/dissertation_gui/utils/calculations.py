from abc import abstractmethod, ABCMeta


class Calculator(ABCMeta):

    @abstractmethod
    def calculate_temperature(self) -> float:
        pass

    def set_temperature(self):
        ...
