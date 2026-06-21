from enum import Enum


class PackMLState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    EXECUTE = "execute"
    COMPLETE = "complete"
    ABORTED = "aborted"
