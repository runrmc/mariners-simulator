class BasePaths:
    """Tracks runners on base."""
    def __init__(self):
        self.first = False
        self.second = False
        self.third = False

    def advance_all(self, bases: int) -> int:
        """Advance all runners by a number of bases. Returns runs scored."""
        runs = 0
        if self.third and bases >= 1:
            runs += 1
            self.third = False
        if self.second:
            if bases >= 2:
                runs += 1
                self.second = False
            elif bases == 1:
                self.third = True
                self.second = False
        if self.first:
            if bases >= 3:
                runs += 1
                self.first = False
            elif bases == 2:
                self.second = True
                self.first = False
            elif bases == 1:
                if not self.second:
                    self.second = True
                self.first = False
        return runs

    def place_runner(self, base: int):
        """Place a new runner on a base."""
        if base == 1:
            self.first = True
        elif base == 2:
            self.second = True
        elif base == 3:
            self.third = True

    def advance_walk(self) -> int:
        """Advance runners on a walk. Returns runs scored."""
        runs = 0
        if self.first and self.second and self.third:
            runs = 1
            self.third = False
        elif self.first and self.second:
            self.third = True
        elif self.first:
            self.second = True
        self.first = True
        return runs

    def clear(self):
        self.first = False
        self.second = False
        self.third = False

    def runners_on(self) -> int:
        return sum([self.first, self.second, self.third])

    def __str__(self):
        bases = []
        if self.first: bases.append("1st")
        if self.second: bases.append("2nd")
        if self.third: bases.append("3rd")
        return ", ".join(bases) if bases else "empty"