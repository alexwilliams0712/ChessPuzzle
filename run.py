import pandas as pd
import numpy as np
import argparse
from functools import wraps
import logging
from distutils.util import strtobool
import tracemalloc

from chess import King, Queen, Knight, Rook, Bishop


def my_logger(orig_func):
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s - %(message)s", level=logging.INFO
    )

    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        if len(args) > 1:
            logging.info(
                f"Running class method {orig_func.__name__} with input square {args[1]}"
            )
        else:
            logging.info(f"Running class method {orig_func.__name__}")
        return orig_func(*args, **kwargs)

    return wrapper


def handle_input():
    parser = argparse.ArgumentParser()
    integers = [str(i) for i in range(20)]
    parser.add_argument("--m", required=True, choices=integers)
    parser.add_argument("--n", required=True, choices=integers)
    parser.add_argument("--king", required=False, choices=integers, default=0)
    parser.add_argument("--queen", required=False, choices=integers, default=0)
    parser.add_argument("--knight", required=False, choices=integers, default=0)
    parser.add_argument("--rook", required=False, choices=integers, default=0)
    parser.add_argument("--bishop", required=False, choices=integers, default=0)
    parser.add_argument(
        "--view", required=False, choices=["True", "False"], default="False"
    )
    args = parser.parse_args()
    return args


class SmallBoard(Exception):
    def __init__(self, value):
        self.value = value


class Board:
    def __init__(self, m, n, K, N, Q, B, R, view):
        self.view = view
        self.base_pieces = {"Q": Q, "R": R, "B": B, "N": N, "K": K}
        self.floating_pieces = (
            self.base_pieces.copy()
        )  # base will be fixed, floating will change as loop through
        self.x = m  # width - x because cartesian
        self.y = n  # height - y because cartesian
        self.base_board = pd.DataFrame([["x"] * self.x] * self.y)  # create the board
        self.valid_configurations = []  # list of configs, each a pandas df to dict
        self.existing_positions = self.base_board.copy()  # positions in current config
        self.moves = []  # list of moves, will traverse back up this
        self.removed_moves = []  # List of moves removed by backsteps
        self.completed = 0

    @my_logger
    def check_board_legal(self):
        """
        Checks the given board is sufficiently large
        """
        if not self.x * self.y > sum(self.base_pieces.values()):
            raise SmallBoard("Board too small")

    def find_next_square(self, square):
        """
        This function finds the next square after the current square
        """
        if square[1] < self.y - 1:
            square[1] += 1
        elif square[0] < self.x - 1:
            square[1] = 0
            square[0] += 1
        elif square == [self.x - 1, self.y - 1]:
            square = [0, 0]
        return square

    def piece_counter(self, potential_config):
        final_values = {"Q": 0, "R": 0, "B": 0, "N": 0, "K": 0}
        for row in potential_config:
            for piece in final_values:
                final_values[piece] += sum(value == piece for value in row.values())
        if final_values == self.base_pieces:
            return True
        else:
            return False

    @my_logger
    def step_forward(self, square):
        """
        This function steps forward through the tree
        """
        position_options = {
            "Q": Queen(square.copy(), self.x, self.y).get_threatening(),
            "R": Rook(square.copy(), self.x, self.y).get_threatening(),
            "B": Bishop(square.copy(), self.x, self.y).get_threatening(),
            "N": Knight(square.copy(), self.x, self.y).get_threatening(),
            "K": King(square.copy(), self.x, self.y).get_threatening(),
        }

        for piece in position_options:
            # Finds the value of the squares new piece can threaten if placed here
            existing_list = [
                self.existing_positions[position_options[piece][a][0]].iloc[
                    position_options[piece][a][1]
                ]
                for a in range(len(position_options[piece]))
            ]

            if (
                ({"piece": piece, "position": square.copy()} in self.removed_moves)
                and (piece == "K")
                and (len(self.moves) > 0)
            ):
                self.step_backward()
            threatened = []
            for i in range(len(self.moves)):
                threatened += self.moves[i]["threatening"]
            if (
                # Check we have enough remaining pieces
                (self.floating_pieces[piece] > 0)
                # Check all threatened squares are currently empty
                & (all(a == self.base_board[0].iloc[0] for a in existing_list))
                # Check we arent redoing a move we've just undone
                & (
                    {"piece": piece, "position": square.copy()}
                    not in self.removed_moves
                )
                & (square not in threatened)
            ):

                self.moves.append(
                    {
                        "piece": piece,
                        "position": square.copy(),
                        "threatening": position_options[piece].copy(),
                    }
                )
                logging.info(f"Adding {piece} to {square}")
                self.existing_positions[square.copy()[0]].iloc[square.copy()[1]] = piece
                self.floating_pieces[piece] -= 1
                if self.piece_counter(
                    self.existing_positions.to_dict(orient="records")
                ):
                    if (sum(self.floating_pieces.values()) == 0) and (
                        self.existing_positions.to_dict(orient="records")
                        not in self.valid_configurations
                    ):
                        logging.info("Solution found!")
                        self.valid_configurations.append(
                            self.existing_positions.to_dict(orient="records")
                        )

                        self.step_backward()
                elif sum(self.floating_pieces.values()) > 0:
                    sq = self.find_next_square(square.copy())
                    if (sq == self.start_square) and len(self.moves) > 0:

                        self.step_backward()
                    while sq != square.copy():
                        threatened = []
                        for i in range(len(self.moves)):
                            threatened += self.moves[i]["threatening"]
                        if sq == [self.x, self.y]:
                            return
                        elif sq not in threatened:
                            self.step_forward(sq)
                        sq = self.find_next_square(sq)
        if (square == self.last_square) and (len(self.moves) > 0):
            self.step_backward()

    @my_logger
    def step_backward(self):
        """
        This function backsteps up the tree and steps forward again if possible
        """
        self.existing_positions[self.moves[-1]["position"][0]].iloc[
            self.moves[-1]["position"][1]
        ] = self.base_board[0].iloc[0]
        self.floating_pieces[self.moves[-1]["piece"]] += 1
        removed_piece = self.moves[-1]["piece"]
        removed_position = self.moves[-1]["position"].copy()
        logging.info(f"Removing {removed_piece} from {removed_position}")
        self.removed_moves.append(
            {"piece": removed_piece, "position": removed_position}
        )
        self.moves = self.moves[:-1].copy()
        if (removed_position == self.last_square) and (len(self.moves) > 0):
            self.step_backward()
        else:
            threatened = []
            for i in range(len(self.moves)):
                threatened += self.moves[i]["threatening"]
            if self.removed_moves[-1]["position"] == [self.x, self.y]:
                return
            elif self.removed_moves[-1]["position"] not in threatened:
                self.step_forward(self.removed_moves[-1]["position"])

    @my_logger
    def display_configs(self):
        for conf in self.valid_configurations:
            print(pd.DataFrame(conf))
            print("-------------------------")

    @my_logger
    def run(self):
        self.check_board_legal()
        self.start_square = [0, 0]
        self.last_square = [self.x - 1, self.y - 1]
        # Stop once all squares have been looped over
        while self.completed < 2:
            square = self.start_square.copy()
            if square == [0, 0]:
                self.completed += 1
            self.step_forward(square)
            self.last_square = self.start_square.copy()
            self.start_square = self.find_next_square(square)
            logging.info(f"Starting square changing to {self.start_square}")
            self.existing_positions = self.base_board.copy()
            self.moves = []
            self.floating_pieces = self.base_pieces.copy()
            self.removed_moves = []

        if self.view:
            self.display_configs()
        logging.info(
            f"We have found {len(self.valid_configurations)} distinct configurations"
        )


if __name__ == "__main__":
    tracemalloc.start()
    args = handle_input()
    board = Board(
        m=int(args.m),
        n=int(args.n),
        K=int(args.king),
        N=int(args.knight),
        Q=int(args.queen),
        B=int(args.bishop),
        R=int(args.rook),
        view=strtobool(args.view),
    )
    board.run()
    current, peak = tracemalloc.get_traced_memory()
    logging.info(
        f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB"
    )
    tracemalloc.stop()
