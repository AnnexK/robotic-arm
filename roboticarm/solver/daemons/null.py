from .daemon import Daemon


class NullDaemon(Daemon):
    def __init__(self):
        pass

    def daemon_actions(self):
        pass
