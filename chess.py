"""
THis module contains classes to define each chess piece
"""


class King:
    """
    Class to define a King
    """

    def __init__(self, location, m, n):
        self.location = location
        self.m = m
        self.n = n

    def get_threatening(self):
        """
        Defines all squares threatened by the king, and then ensures theyre actually on the board
        """
        threatened = [
            [self.location[0] + 0, self.location[1] - 1],
            [self.location[0] + 0, self.location[1] + 0],
            [self.location[0] + 0, self.location[1] + 1],
            [self.location[0] + 1, self.location[1] - 1],
            [self.location[0] + 1, self.location[1] + 0],
            [self.location[0] + 1, self.location[1] + 1],
            [self.location[0] - 1, self.location[1] - 1],
            [self.location[0] - 1, self.location[1] + 0],
            [self.location[0] - 1, self.location[1] + 1],
        ]
        threatened = [
            x for x in threatened if (0 <= x[0] < self.m and 0 <= x[1] < self.n)
        ]
        return threatened


class Queen:
    def __init__(self, location, m, n):
        self.location = location
        self.m = m
        self.n = n

    def get_threatening(self):
        """
        Defines all squares threatened by the queen, and then ensures theyre actually on the board
        """
        base_threatened = []
        for a in range(max(self.m, self.n)):
            base_threatened += [
                [self.location[0] + 0, self.location[1] - a],
                [self.location[0] + 0, self.location[1] + 0],
                [self.location[0] + 0, self.location[1] + a],
                [self.location[0] + a, self.location[1] - a],
                [self.location[0] + a, self.location[1] + 0],
                [self.location[0] + a, self.location[1] + a],
                [self.location[0] - a, self.location[1] - a],
                [self.location[0] - a, self.location[1] + 0],
                [self.location[0] - a, self.location[1] + a],
            ]

        threatened = []
        [threatened.append(x) for x in base_threatened if x not in threatened]

        threatened = [
            x for x in threatened if (0 <= x[0] < self.m and 0 <= x[1] < self.n)
        ]
        return threatened


class Rook:
    def __init__(self, location, m, n):
        self.location = location
        self.m = m
        self.n = n

    def get_threatening(self):
        """
        Defines all squares threatened by the rook, and then ensures theyre actually on the board
        """
        base_threatened = []
        for a in range(max(self.m, self.n)):
            base_threatened += [
                [self.location[0] + 0, self.location[1] - a],
                [self.location[0] + 0, self.location[1] + 0],
                [self.location[0] + 0, self.location[1] + a],
                [self.location[0] + a, self.location[1] + 0],
                [self.location[0] - a, self.location[1] + 0],
            ]

        threatened = []
        [threatened.append(x) for x in base_threatened if x not in threatened]

        threatened = [
            x for x in threatened if (0 <= x[0] < self.m and 0 <= x[1] < self.n)
        ]
        return threatened


class Bishop:
    def __init__(self, location, m, n):
        self.location = location
        self.m = m
        self.n = n

    def get_threatening(self):
        """
        Defines all squares threatened by the bishop, and then ensures theyre actually on the board
        """
        base_threatened = []
        for a in range(max(self.m, self.n)):
            base_threatened += [
                [self.location[0] + 0, self.location[1] + 0],
                [self.location[0] + a, self.location[1] + a],
                [self.location[0] + a, self.location[1] - a],
                [self.location[0] - a, self.location[1] - a],
                [self.location[0] - a, self.location[1] + a],
            ]

        threatened = []
        [threatened.append(x) for x in base_threatened if x not in threatened]

        threatened = [
            x for x in threatened if (0 <= x[0] < self.m and 0 <= x[1] < self.n)
        ]
        return threatened


class Knight:
    def __init__(self, location, m, n):
        self.location = location
        self.m = m
        self.n = n

    def get_threatening(self):
        """
        Defines all squares threatened by the knight, and then ensures theyre actually on the board
        """
        threatened = [
            [self.location[0] + 0, self.location[1] + 0],
            [self.location[0] + 1, self.location[1] + 2],
            [self.location[0] + 1, self.location[1] - 2],
            [self.location[0] + 2, self.location[1] + 1],
            [self.location[0] + 2, self.location[1] - 1],
            [self.location[0] - 1, self.location[1] + 2],
            [self.location[0] - 1, self.location[1] - 2],
            [self.location[0] - 2, self.location[1] + 1],
            [self.location[0] - 2, self.location[1] - 1],
        ]

        threatened = [
            x for x in threatened if (0 <= x[0] < self.m and 0 <= x[1] < self.n)
        ]
        return threatened
