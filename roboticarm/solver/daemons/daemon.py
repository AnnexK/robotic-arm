import abc


class Daemon(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def daemon_actions(self):
        pass
