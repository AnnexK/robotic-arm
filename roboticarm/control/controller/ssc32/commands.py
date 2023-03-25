from enum import Enum
from pydantic import BaseModel, Field


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
        return f"QP{self.channel}"


class ByteOutputCommand(BaseModel):
    """
    Команда на выполнение побайтового вывода.

    :param bank: Банк выводов.
    :param value: Выводимое значение.
    """
    bank: int = Field(ge=0, lt=4)
    value: int = Field(ge=0, le=255)

    def __str__(self) -> str:
        return f"{self.bank}:{self.value}"


class DiscreteOutputCommand(BaseModel):
    """
    Команда на выполнение дискретного вывода.

    :param channel: Канал вывода.
    :param value: Значение (True -- значение HIGH, False -- значение LOW).
    """
    channel: int = Field(ge=0, lt=32)
    value: bool

    def __str__(self) -> str:
        return f"#{self.channel}{'H' if self.value else 'L'}"


class DigitalInputPin(str, Enum):
    """
    Возможные значения пометок вводов для команды цифрового ввода.
    """

    PIN_A = "A"
    PIN_B = "B"
    PIN_C = "C"
    PIN_D = "D"
    PIN_E = "E"
    PIN_F = "F"


class DigitalInputCommand(BaseModel):
    """
    Команда на выполнение цифрового ввода.

    :param input_pin: Пометка ввода.
    :param latching: Является ли ввод 'запоминающим'.
    """

    input_pin: DigitalInputPin
    latching: bool

    def __str__(self) -> str:
        return f"{self.input_pin}{'L' if self.latching else ''}"


class AnalogInputPin(str, Enum):
    """
    Возможные значения пометок вводов для команды цифрового ввода.
    """

    PIN_A = "A"
    PIN_B = "B"
    PIN_C = "C"
    PIN_D = "D"
    PIN_E = "E"
    PIN_F = "F"


class AnalogInputCommand(BaseModel):
    """
    Команда на выполнение аналогового ввода.

    :param input_pin: Пометка ввода.
    """

    input_pin: AnalogInputPin

    def __str__(self) -> str:
        return f"V{self.input_pin}"
