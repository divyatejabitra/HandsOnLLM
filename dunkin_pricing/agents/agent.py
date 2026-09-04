import logging


class Agent:
    """
    An abstract superclass for Agents
    Used to log messages in a way that can identify each Agent
    """

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BG_BLACK = '\033[40m'
    RESET = '\033[0m'

    name: str = ""
    color: str = '\033[37m'

    def log(self, message):
        color_code = self.BG_BLACK + self.color
        logging.info(f"{color_code}[{self.name}] {message}{self.RESET}")
