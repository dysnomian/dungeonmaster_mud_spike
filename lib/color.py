class Color:
    COLORS = {
        "PURPLE": "\033[95m",
        "CYAN": "\033[96m",
        "DARKCYAN": "\033[36m",
        "BLUE": "\033[94m",
        "GREEN": "\033[92m",
        "YELLOW": "\033[93m",
        "RED": "\033[91m",
        "BOLD": "\033[1m",
        "UNDERLINE": "\033[4m",
        "END": "\033[0m",
    }

    @property
    def purple(self):
        return self.COLORS["PURPLE"]

    @property
    def cyan(self):
        return self.COLORS["CYAN"]

    @property
    def darkcyan(self):
        return self.COLORS["DARKCYAN"]

    @property
    def blue(self):
        return self.COLORS["BLUE"]

    @property
    def green(self):
        return self.COLORS["GREEN"]

    @property
    def yellow(self):
        return self.COLORS["YELLOW"]

    @property
    def red(self):
        return self.COLORS["RED"]

    @property
    def bold(self):
        return self.COLORS["BOLD"]

    @property
    def underline(self):
        return self.COLORS["UNDERLINE"]

    @property
    def end(self):
        return self.COLORS["END"]


color = Color()
