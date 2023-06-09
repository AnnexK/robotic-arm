import serial.tools.list_ports as list_ports


def get_ports() -> list[str]:
    """
    Получить набор доступных в системе последовательных портов.

    :return: Набор имен портов.
    """

    return [port.device for port in list_ports.comports()]
