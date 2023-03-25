from typing import Protocol


class Reader(Protocol):
    """
    Протокол читателя.
    """

    def read(self, size: int = 1) -> bytes:
        """
        Прочитать набор данных.

        :param size: Размер данных.
        :return: Прочитанные данные.
        """
        ...
