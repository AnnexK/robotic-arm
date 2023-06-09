import serial


class SerialPort:
    """
    Последовательный порт.
    Поддерживает операции чтения и записи.
    Является неблокирующим, обязательно задание таймаута на операции I/O.

    :param device: Путь к устройству порта.
    :param baudrate: Частота обмена данных порта.
    :param timeout: Таймаут на операции I/O.
    """

    def __init__(self, device: str, baudrate: int, timeout: float):
        self._serial = serial.Serial(
            port=device,
            baudrate=baudrate,
            timeout=timeout
        )

    def read(self, size: int) -> bytes:
        return self._serial.read(size)

    def write(self, data: bytes) -> int:

        # какой-то алкаш написал Serial.write так, что он возвращает Optional
        return self._serial.write(data) or 0
