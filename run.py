import pandas as pd
import numpy as np
import argparse
from functools import wraps
import logging
from distutils.util import strtobool

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
        self.completed = False

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
        elif square[0] == self.x - 1 and square[1] == self.y - 1:
            square[0] = 0
            square[1] = 0
        return square

    @my_logger
    def step_forward(self, square):
        """
        This function steps forward through the tree
        """
        if square[0] >= self.x or square[1] >= self.y:
            return
        position_options = {
            "Q": Queen(square, self.x, self.y).get_threatening(),
            "R": Rook(square, self.x, self.y).get_threatening(),
            "B": Bishop(square, self.x, self.y).get_threatening(),
            "N": Knight(square, self.x, self.y).get_threatening(),
            "K": King(square, self.x, self.y).get_threatening(),
        }

        for piece in position_options:
            # Finds the value of the squares this piece  can threaten
            existing_list = [
                self.existing_positions[position_options[piece][a][0]].iloc[
                    position_options[piece][a][1]
                ]
                for a in range(len(position_options[piece]))
            ]
            if (
                (self.floating_pieces[piece] > 0)
                & (all(a == self.base_board[0].iloc[0] for a in existing_list))
                & (
                    {"piece": piece, "position": square.copy()}
                    not in self.removed_moves
                )
            ):
                logging.info(f"Adding {piece} to {square}")
                self.moves.append(
                    {
                        "piece": piece,
                        "position": square.copy(),
                        "threatening": position_options[piece].copy(),
                    }
                )
                self.existing_positions[square[0]].iloc[square[1]] = piece
                self.floating_pieces[piece] -= 1
                if (sum(self.floating_pieces.values()) == 0) and (
                    self.existing_positions.to_dict(orient="records")
                    not in self.valid_configurations
                ):
                    logging.info("Solution found!")
                    self.valid_configurations.append(
                        self.existing_positions.to_dict(orient="records")
                    )
                    self.step_backward(square)
                    return
                elif sum(self.floating_pieces.values()) > 0:
                    sq = self.find_next_square(square.copy())
                    while sq != square:
                        # print(sq)

                        threatened = []
                        for i in range(len(self.moves)):
                            threatened += self.moves[i]["threatening"]
                        if sq == [self.x, self.y]:
                            return
                        elif sq not in threatened:
                            # print(sq, self.moves)
                            self.step_forward(sq)
                        sq = self.find_next_square(sq)

    @my_logger
    def step_backward(self, square):
        """
        This function backsteps up the tree and steps forward again if possible
        """
        if square[0] >= self.x or square[1] >= self.y:
            return
        position_options = {
            "Q": Queen(square, self.x, self.y).get_threatening(),
            "R": Rook(square, self.x, self.y).get_threatening(),
            "B": Bishop(square, self.x, self.y).get_threatening(),
            "N": Knight(square, self.x, self.y).get_threatening(),
            "K": King(square, self.x, self.y).get_threatening(),
        }
        self.existing_positions[self.moves[-1]["position"][0]].iloc[
            self.moves[-1]["position"][1]
        ] = self.base_board[0].iloc[0]
        self.floating_pieces[self.moves[-1]["piece"]] += 1
        removed_piece = self.moves[-1]["piece"]
        removed_position = self.moves[-1]["position"].copy()
        logging.info(f"Removing {removed_piece} from {removed_position}" )
        self.removed_moves.append(
            {"piece": removed_piece, "position": removed_position}
        )
        # print("removed: ", self.removed_moves)
        self.moves = self.moves[:-1].copy()
        self.step_forward(square)

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
        while (self.start_square[0] < self.x-1 or self.start_square[1] < self.y-1) and self.completed == False :
            square = self.start_square.copy()
            if square == self.last_square:
                self.completed = True

            self.step_forward(square)
            self.start_square = self.find_next_square(square)
            self.existing_positions = self.base_board.copy()
            self.moves = []
            self.floating_pieces = self.base_pieces.copy()
            self.removed_moves = []
            # input()

        if self.view:
            self.display_configs()
        print(f"We have found {len(self.valid_configurations)} distinct configurations")


if __name__ == "__main__":
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
