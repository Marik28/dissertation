import random
import time

from PyQt5.QtCore import QThread, pyqtSignal


class MeasuredTempThread(QThread):
    temp_signal = pyqtSignal(float)

    def run(self) -> None:
        temp = 0.
        while True:
            temp += 0.5
            self.temp_signal.emit(temp)
            time.sleep(1 / 10)


class SetpointThread(QThread):
    setpoint_signal = pyqtSignal(float)

    def run(self) -> None:
        setpoint = 10.
        while True:
            self.setpoint_signal.emit(setpoint)
            time.sleep(1 / 10)
