from enum import Enum, auto
import platform


class OSType(Enum):
    Windows = auto()
    MacOS = auto()
    Linux = auto()
    Unknown = auto()


def get_current_os() -> OSType:
    match platform.system():
        case "Windows":
            return OSType.Windows
        case "Darwin":
            return OSType.MacOS
        case "Linux":
            return OSType.Linux

    return OSType.Unknown