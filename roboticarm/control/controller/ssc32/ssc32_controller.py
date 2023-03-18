import time
from pydantic import BaseModel, Field
from roboticarm.control.communication import Reader, Writer


class CommandSendError(Exception):
    """
    Исключение, возникающее при ошибке при отправке команды.
    """    
    def __str__(self) -> str:
        return "Could not send a command"


class UnsupportedChannel(Exception):
    def __init__(self, ch: int):
        self._ch = ch

    def __str__(self) -> str:
        return f"Unsupported channel nr. {self._ch}"


class ServoMoveCommand(BaseModel):
    """
    Команда на перемещение одного сервопривода.

    :param channel: Канал контроллера.
    :param pulse_width: Ширина импульса для привода (мкс).
    :param time: Время исполнения команды.
    :param speed: Скорость изменения импульса (мкс/сек).
    """
    channel: int = Field(ge=0, lt=32)
    pulse_width: int = Field(ge=500, le=2500)
    time: int | None = Field(None, gt=0, le=65535)
    speed: int | None = Field(None, gt=0)

    def __str__(self) -> str:
        return (
            f"#{self.channel}P{self.pulse_width}"
            f"{f'S{self.speed}' if self.speed else ''}"
            f"{f'T{self.time}' if self.time else ''}"
        )


class PulseOffsetCommand(BaseModel):
    """
    Команда на задание смещения центра ширины импульса.

    :param channel: Канал контроллера.
    :param pulse_offset: Ширина смещения.
    """
    channel: int = Field(ge=0, lt=32)
    pulse_offset: int = Field(ge=-100, le=100)

    def __str__(self) -> str:
        return f"#{self.channel}PO{self.pulse_offset}"


class QueryPulseWidthCommand(BaseModel):
    """
    Команда на получение заданной ширины импульса на канале.

    :param channel: Канал контроллера.
    """
    channel: int = Field(ge=0, lt=32)

    def __str__(self) -> str:
        return f"#{self.channel}QP"


class SSC32Controller:
    """
    Контроллер SSC-32.
    Реализует операции, описанные в референсе.

    :param reader: Читатель.
    :param writer: Писатель.
    """

    def __init__(self, reader: Reader, writer: Writer):
        self._reader = reader
        self._writer = writer

    def _send_command(self, command: str):
        """
        Отправить команду в порт.

        :param command: Строковое представление команды.
        """
        command += "\r"
        if self._writer.write(command.encode(encoding='ascii')) < len(command):
            raise CommandSendError

    def servo_move(self, command: ServoMoveCommand):
        """
        Послать команду перемещения на один сервопривод.

        :param command: Команда.
        """

        self._send_command(str(command))

    def servo_move_group(self, commands: list[ServoMoveCommand]):
        """
        Послать команду перемещения на несколько сервоприводов.

        :param commands: Набор объединяемых команд.
        """
        distinct_chans = {cmd.channel for cmd in commands}
        commands_are_distinct = len(distinct_chans) == len(commands)

        if not commands_are_distinct:
            raise ValueError(commands)

        command = ''.join(str(cmd) for cmd in commands)
        self._send_command(command)

    def pulse_offset(self, command: PulseOffsetCommand):
        """
        Послать команду задания смещения импульса на один сервопривод.

        :param command: Команда.
        """
        self._send_command(str(command))

    def pulse_offset_group(self, commands: list[PulseOffsetCommand]):
        """
        Послать команду задания смещения на несколько сервоприводов.

        :param commands: Набор объединяемых команд.
        """
        distinct_chans = {cmd.channel for cmd in commands}
        commands_are_distinct = len(distinct_chans) == len(commands)

        if not commands_are_distinct:
            raise ValueError(commands)

        command = ''.join(str(cmd) for cmd in commands)
        self._send_command(command)

    def query_movement_status(self) -> bool:
        """
        Запросить состояние перемещения.

        :return: Выполняется ли в данный момент команда перемещения.
        """
        command = "Q"
        self._send_command(command)
        time.sleep(0.005)
        response = self._reader.read(1)
        return response == b'+'

    def query_pulse_width(self, command: QueryPulseWidthCommand) -> int:
        self._send_command(str(command))
        """
        Послать запрос заданной ширины импульса для одного сервопривода.

        :param command: Команда.
        :return: Ширина импульса.
        """
        # Would be nice to be async
        time.sleep(0.005)
        return self._read_pw_query(len(command))[0]

    def query_pulse_width_group(
            self,
            commands: list[QueryPulseWidthCommand]
    ) -> list[int]:
        """
        Послать запрос заданной ширины импульса для нескольких сервоприводов.

        :param commands: Набор объединяемых команд.
        :return: Набор ширин импульсов, соответственно каналу команды.
        """
        distinct_chans = {cmd.channel for cmd in commands}
        commands_are_distinct = len(distinct_chans) == len(commands)

        if not commands_are_distinct:
            raise ValueError(commands)

        command = ''.join(str(cmd) for cmd in commands)
        self._send_command(command)
        time.sleep(0.005)
        return self._read_pw_query(len(command))

    def _read_pw_query(self, command_number: int) -> list[int]:
        """
        Прочитать и декодировать ответ на запрос ширин импульсов.

        :param command_number: Сколько команд было в запросе.
        :return: Ширины импульсов (с точностью до 10мкс).
        """

        response = self._reader.read(command_number)
        return [int(w) for w in response]
