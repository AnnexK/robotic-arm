from typing import Protocol


class Writer(Protocol):
    """
    Протокол писателя.
    """

    def write(data: bytes) -> int:
        """
        Записать данные.

        :param data: Данные.
        :return: Количество записанных данных.
        """
        ...
