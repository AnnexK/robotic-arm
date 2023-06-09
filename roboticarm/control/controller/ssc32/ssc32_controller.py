import time
from roboticarm.control.communication import Reader, Writer
from . import commands as cmds, exceptions


class SSC32Controller:
    """
    Контроллер SSC-32.
    Реализует операции, описанные в референсе.

    :param reader: Читатель.
    :param writer: Писатель.
    """

    CHANNEL_AMOUNT = 32

    def __init__(self, reader: Reader, writer: Writer):
        self._reader = reader
        self._writer = writer

    def _send_command(self, command: str):
        """
        Отправить команду в порт.

        :param command: Строковое представление команды.
        """
        command += "\r"

        if self._writer.write(command.encode(encoding="ascii")) < len(command):
            raise exceptions.CommandSendError(command)

    def set_initial_state(self):
        """
        Задать начальное положение по всем каналам для
        инициализации контроллера.
        """

        commands = [
            cmds.ServoMoveCommand(channel=i, pulse_width=1500)
            for i in range(self.CHANNEL_AMOUNT)
        ]
        self.servo_move_group(commands)

    def servo_move(self, command: cmds.ServoMoveCommand):
        """
        Послать команду перемещения на один сервопривод.

        :param command: Команда.
        """

        self._send_command(str(command))

    def servo_move_group(self, commands: list[cmds.ServoMoveCommand]):
        """
        Послать команду перемещения на несколько сервоприводов.

        :param commands: Набор объединяемых команд.
        """
        distinct_chans = {cmd.channel for cmd in commands}
        commands_are_distinct = len(distinct_chans) == len(commands)

        if not commands_are_distinct:
            raise ValueError(commands)

        command = "".join(str(cmd) for cmd in commands)
        self._send_command(command)

    def pulse_offset(self, command: cmds.PulseOffsetCommand):
        """
        Послать команду задания смещения импульса на один сервопривод.

        :param command: Команда.
        """
        self._send_command(str(command))

    def pulse_offset_group(self, commands: list[cmds.PulseOffsetCommand]):
        """
        Послать команду задания смещения на несколько сервоприводов.

        :param commands: Набор объединяемых команд.
        """
        distinct_chans = {cmd.channel for cmd in commands}
        commands_are_distinct = len(distinct_chans) == len(commands)

        if not commands_are_distinct:
            raise ValueError(commands)

        command = "".join(str(cmd) for cmd in commands)
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
        return response == b"+"

    def query_pulse_width(self, command: cmds.QueryPulseWidthCommand) -> int:
        """
        Послать запрос заданной ширины импульса для одного сервопривода.

        :param command: Команда.
        :return: Ширина импульса.
        """
        cmd = str(command)
        self._send_command(cmd)
        # Would be nice to be async
        time.sleep(0.005)
        return self._read_pw_query(1)[0]

    def query_pulse_width_group(
        self, commands: list[cmds.QueryPulseWidthCommand]
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

        command = "".join(str(cmd) for cmd in commands)
        self._send_command(command)
        time.sleep(0.005)
        return self._read_pw_query(len(command))

    def cancel(self):
        """
        Отменить исполняемую в данный момент команду.
        """
        if self._writer.write(b"\x1B") < 1:
            raise cmds.CommandSendError

    def discrete_output(self, commands: list[cmds.DiscreteOutputCommand]):
        """
        Выполнить набор команд дискретного вывода.

        :param commands: Набор команд.
        """
        distinct_chans = {cmd.channel for cmd in commands}
        commands_are_distinct = len(distinct_chans) == len(commands)

        if not commands_are_distinct:
            raise ValueError(commands)

        command = "".join(str(cmd) for cmd in commands)
        self._send_command(command)

    def byte_output(self, command: cmds.ByteOutputCommand):
        """
        Отправить команду побайтового вывода.

        :param command: Команда.
        """
        self._send_command(str(command))

    def digital_input(self, commands: list[cmds.DigitalInputCommand]) -> list[bool]:
        """
        Отправить команду цифрового ввода.

        :param commands: Набор объединяемых команд.
        :return: Прочитанные с входов значения.
        """

        command_num = len(commands)
        if command_num > 8:
            raise ValueError(commands)

        command = "".join(str(cmd) for cmd in commands)
        self._send_command(command)
        time.sleep(0.08)
        return self._read_digital_input(command_num)

    def analog_input(self, commands: list[cmds.AnalogInputCommand]) -> list[int]:
        """
        Отправить команду аналогового ввода.

        :param commands: Набор объединяемых команд.
        :return: Прочитанные с входов значения.
        """
        command_num = len(commands)

        command = "".join(str(cmd) for cmd in commands)
        self._send_command(command)
        time.sleep(0.008)
        return self._read_analog_input(command_num)

    def _read_pw_query(self, command_number: int) -> list[int]:
        """
        Прочитать и декодировать ответ на запрос ширин импульсов.

        :param command_number: Сколько команд было в запросе.
        :return: Ширины импульсов (с точностью до 10мкс).
        """

        response = self._reader.read(command_number)
        if len(response) < command_number:
            raise exceptions.CommandReadError

        return [int(w) * 10 for w in response]

    def _read_digital_input(self, command_number: int) -> list[bool]:
        """
        Прочитать и декодировать ответ на запрос цифрового ввода.

        :param command_number: Сколько команд было в запросе.
        :return: Ответ.
        """

        response = self._reader.read(command_number)
        if len(response) < command_number:
            raise exceptions.CommandReadError

        return [bool(resp_bit - ord("0")) for resp_bit in response]

    def _read_analog_input(self, command_number: int) -> list[int]:
        """
        Прочитать и декодировать ответ на запрос аналогового ввода.

        :param command_number: Сколько команд было в запросе.
        :return: Ответ.
        """

        response = self._reader.read(command_number)
        if len(response) < command_number:
            raise exceptions.CommandReadError

        return [int(b) for b in response]
