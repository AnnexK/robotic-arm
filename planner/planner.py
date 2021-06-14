import abc
from typing import Sequence
from env.types import State
from env.environment import Environment


Plan = Sequence[State]


class Planner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def plan(self, env: Environment) -> Plan:
        pass
