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
        )  # base will be fixed, floating will change
        self.x = m  # width
        self.y = n  # height
        self.base_board = pd.DataFrame([["x"] * self.x] * self.y)  # create the board
        self.valid_configurations = []  # list of configs, each a pandas df
        self.current_threatened = []  # current config, which squares are threatened
        self.existing_positions = self.base_board.copy()  # positions in current config
        self.moves = []  # list of moves, will traverse back up this
        self.removed_moves = []

    @my_logger
    def check_board_legal(self):
        """
        Checks the given board is sufficiently large
        """
        if not self.x * self.y > sum(self.base_pieces.values()):
            raise SmallBoard("Board too small")

    def find_next_square(self, square):
        if square[1] < self.y - 1:
            square[1] += 1
        elif square[0] < self.x - 1:
            square[1] = 0
            square[0] += 1
        elif square[0] == self.x - 1 and square[1] == self.y - 1:
            square[0] = self.x
            square[1] = self.y
        return square

    @my_logger
    def step_forward(self, square):
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
            # print(position_options[piece])
            existing_list = [
                self.existing_positions[position_options[piece][a][1]].iloc[
                    position_options[piece][a][0]
                ]
                for a in range(len(position_options[piece]))
            ]
            # print(existing_list)
            if (
                (self.floating_pieces[piece] > 0)
                and (all(a == self.base_board[0].iloc[0] for a in existing_list))
                and ({"piece": piece, "position": square} not in self.removed_moves)
            ):

                # print(square)
                self.current_threatened.append(
                    {
                        "piece": piece,
                        "location": square,
                        "threatening": position_options[piece],
                    }
                )
                # print(self.current_threatened)
                self.existing_positions.loc[square[0], square[1]] = piece
                self.moves.append({"piece": piece, "position": square})
                self.floating_pieces[piece] -= 1
                if (sum(self.floating_pieces.values()) == 0) and (
                    self.existing_positions.to_dict(orient="records")
                    not in self.valid_configurations
                ):

                    # print(self.current_threatened)
                    # print(self.existing_positions)
                    # print("++++++++++++++++++++")
                    logging.info("Solution found!")
                    self.valid_configurations.append(
                        self.existing_positions.to_dict(orient="records")
                    )
                    self.step_backward(square)
                    return
                elif sum(self.floating_pieces.values()) > 0:
                    while square != [self.x, self.y]:
                        square = self.find_next_square(square)
                        # print(square)
                        threatened = []
                        for i in range(len(self.current_threatened)):
                            threatened += self.current_threatened[i]["threatening"]
                        if square == [self.x, self.y]:
                            return
                        elif square not in threatened:
                            self.step_forward(square)

    # @my_logger
    def step_backward(self, square):
        if square[0] >= self.x or square[1] >= self.y:
            return
        position_options = {
            "Q": Queen(square, self.x, self.y).get_threatening(),
            "R": Rook(square, self.x, self.y).get_threatening(),
            "B": Bishop(square, self.x, self.y).get_threatening(),
            "N": Knight(square, self.x, self.y).get_threatening(),
            "K": King(square, self.x, self.y).get_threatening(),
        }
        self.current_threatened = self.current_threatened[:-1]
        self.existing_positions.loc[
            self.moves[-1]["position"][0], self.moves[-1]["position"][1]
        ] = self.base_board[0].iloc[0]
        self.floating_pieces[self.moves[-1]["piece"]] += 1
        self.removed_moves.append(self.moves[-1])
        self.moves = self.moves[:-1]
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
        while self.start_square[0] < self.x or self.start_square[1] < self.y:
            # Changes the starting square for each loop through, appends on the start of the board to the end
            for row_loc, row_value in (
                self.base_board[self.start_square[0] :]
                .append(self.base_board[: self.start_square[0]])
                .iterrows()
            ):
                # Changing the starting col for each loop through
                for col_loc in (
                    row_value[self.start_square[1] :]
                    .append(row_value[: self.start_square[1]])
                    .index.tolist()
                ):
                    threatened = []
                    for i in range(len(self.current_threatened)):
                        threatened += self.current_threatened[i]["threatening"]
                    if ([row_loc, col_loc] not in threatened) and sum(
                        self.floating_pieces.values()
                    ) > 0:
                        self.step_forward([row_loc, col_loc])
                    elif ([row_loc, col_loc] == self.last_square) or (
                        sum(self.floating_pieces.values()) == 0
                    ):
                        if len(self.moves) > 0:
                            self.step_backward([row_loc, col_loc])

            self.start_square = self.find_next_square(self.start_square)
            self.existing_positions = self.base_board.copy()
            self.current_threatened = []
            self.floating_pieces = self.base_pieces.copy()
            self.moves = []
            self.removed_moves = []

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
