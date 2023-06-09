from typing import Sequence, Protocol

from roboticarm.env.types import State
from roboticarm.env.environment import Environment


Plan = Sequence[State]


class Planner(Protocol):
    """
    Протокол планировщика траектории.
    """

    def plan(self, env: Environment, goal_state: State) -> Plan:
        """
        Спланировать траекторию перемещения для робота в среде
        для определенного целевого положения.

        :param env: Среда робота.
        :param goal_state: Целевое положение.
        :return: Траектория перемещения.
        """
        ...
