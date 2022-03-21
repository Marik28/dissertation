from PyQt5.QtSerialPort import QSerialPortInfo


def main():
    ports = QSerialPortInfo.availablePorts()
    port_names = [port.portName() for port in ports]
    print(f"Available ports: {port_names}")


if __name__ == '__main__':
    main()
