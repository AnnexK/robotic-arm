class SSC32ControllerError(Exception):
    """
    Ошибка контроллера SSC-32.
    """


class CommandSendError(Exception):
    """
    Исключение, возникающее при ошибке при отправке команды.
    """
    def __init__(self, command: str):
        self._command = command

    def __str__(self) -> str:
        return f"Could not send a command {self._command}"


class CommandReadError(Exception):
    """
    Исключение, возникающее при ошибке при чтении результата
    исполнения команды.
    """

    def __str__(self) -> str:
        return "Could not read command result"


class CommandChannelDuplicateError(Exception):
    """
    Исключение, возникающее при передаче в наборе команд
    нескольких команд с одинаковыми каналами
    (если это запрещено командой).
    """

    def __str__(self) -> str:
        return "Encountered multiple commands with same channel number"
