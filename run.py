import pandas as pd
import numpy as np
import argparse
from functools import wraps
import logging

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
    parser.add_argument("--M", required=True, choices=integers)
    parser.add_argument("--N", required=True, choices=integers)
    parser.add_argument("--king", required=False, choices=integers, default=0)
    parser.add_argument("--queen", required=False, choices=integers, default=0)
    parser.add_argument("--knight", required=False, choices=integers, default=0)
    parser.add_argument("--rook", required=False, choices=integers, default=0)
    parser.add_argument("--bishop", required=False, choices=integers, default=0)
    args = parser.parse_args()
    return args


class Board:
    def __init__(self, m, n, K, N, Q, B, R):
        self.base_pieces = {"queen": Q, "rook": R, "bishop": B, "knight": N, "king": K}
        self.floating_pieces = (
            self.base_pieces.copy()
        )  # base will be fixed, floating will change
        self.m = m  # width
        self.n = n  # height
        self.base_board = pd.DataFrame([["x"] * self.m] * self.n)  # create the board
        self.valid_configurations = []  # list of configs, each a pandas df
        self.current_threatened = []  # current config, which squares are threatened
        self.existing_positions = self.base_board.copy()  # positions in current config
        self.moves = []  # list of moves, will traverse back up this
        self.removed_moves = []

    @my_logger
    def check_board_legal(self,):
        """
        Checks the given board is sufficiently large
        """
        if not self.m * self.n > sum(self.base_pieces.values()):
            raise SmallBoard("Board too small")

    @my_logger
    def step_forward(self, square):
        # print("going forward")
        print(square)
        position_options = {
            "queen": Queen(square, self.m, self.n).get_threatening(),
            "rook": Rook(square, self.m, self.n).get_threatening(),
            "bishop": Bishop(square, self.m, self.n).get_threatening(),
            "knight": Knight(square, self.m, self.n).get_threatening(),
            "king": King(square, self.m, self.n).get_threatening(),
        }
        for piece in position_options:
            existing_list = [
                self.existing_positions[position_options[piece][x][1]].iloc[
                    position_options[piece][x][0]
                ]
                for x in range(len(position_options[piece]))
            ]
            if (
                (self.floating_pieces[piece] > 0)
                and (all(y == self.base_board[0].iloc[0] for y in existing_list))
                and ({"piece": piece, "position": square} not in self.removed_moves)
            ):
                # print("Forward ", self.floating_pieces[piece])
                print("----------------")
                self.current_threatened += position_options[piece]
                self.existing_positions.loc[square[0], square[1]] = piece
                self.moves.append({"piece": piece, "position": square})
                self.floating_pieces[piece] -= 1
                print(self.existing_positions)
                return

    @my_logger
    def step_backward(self, square):
        # print("stepping back", square)
        position_options = {
            "queen": Queen(square, self.m, self.n).get_threatening(),
            "rook": Rook(square, self.m, self.n).get_threatening(),
            "bishop": Bishop(square, self.m, self.n).get_threatening(),
            "knight": Knight(square, self.m, self.n).get_threatening(),
            "king": King(square, self.m, self.n).get_threatening(),
        }


        # y = [self.valid_configurations[x] for x, _ in enumerate(self.valid_configurations) if self.valid_configurations[x].equals(self.valid_configurations[x-1]) is False]
        # for a in y:
        #     print(a)
        #     print("++++++++++++++++++++")




        if (sum(self.floating_pieces.values()) == 0) and all(
            [
                ~self.existing_positions.equals(self.valid_configurations[x])
                for x in range(len(self.valid_configurations))
            ]
        ):
            # print(sum(self.floating_pieces.values()))

            self.valid_configurations.append(self.existing_positions)
        # print(self.existing_positions)
        for coordinates in position_options[self.moves[-1]["piece"]]:
            if coordinates in self.current_threatened:
                self.current_threatened.remove(coordinates)

        self.existing_positions.loc[
            self.moves[-1]["position"][0], self.moves[-1]["position"][1]
        ] = self.base_board[0].iloc[0]
        self.floating_pieces[self.moves[-1]["piece"]] += 1
        self.removed_moves.append(self.moves[-1])
        self.moves = self.moves[:-1]
        self.step_forward(square)
        # print("Backward ", self.moves)
        # print("Removed moves", self.removed_moves)
        # print("Threatened", self.current_threatened)

    @my_logger
    def run(self):
        self.check_board_legal()
        self.start_square = [0, 0]
        self.last_square = [self.m - 1, self.n - 1]
        # Stop once all squares have been looped over
        while self.start_square[0] < self.m or self.start_square[1] < self.n:
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
                    if ([row_loc, col_loc] not in self.current_threatened) and sum(
                        self.floating_pieces.values()
                    ) > 0:
                        self.step_forward([row_loc, col_loc])
                    elif ([row_loc, col_loc] == self.last_square) or sum(
                        self.floating_pieces.values()
                    ) == 0:
                        if len(self.moves) > 0:
                            self.step_backward([row_loc, col_loc])
            input()

            if self.start_square[1] < self.m - 1:
                self.last_square = self.start_square
                self.start_square[1] += 1
            elif self.start_square[0] < self.n - 1:
                self.last_square = self.start_square
                self.start_square[1] = 0
                self.start_square[0] += 1
            elif (
                self.start_square[0] == self.n - 1
                and self.start_square[1] == self.m - 1
            ):
                self.start_square[0] = self.n
                self.start_square[1] = self.m

            self.existing_positions = self.base_board.copy()
            self.current_threatened = []
            self.floating_pieces = self.base_pieces.copy()
            self.moves = []
            self.removed_moves = []


        self.valid_configurations = pd.Series(self.valid_configurations).drop_duplicates().tolist()
        print(len(self.valid_configurations))
        for conf in self.valid_configurations:
            print(conf)
            print("-------------------------")


if __name__ == "__main__":
    args = handle_input()
    board = Board(
        m=int(args.M),
        n=int(args.N),
        K=int(args.king),
        N=int(args.knight),
        Q=int(args.queen),
        B=int(args.bishop),
        R=int(args.rook),
    )
    board.run()
