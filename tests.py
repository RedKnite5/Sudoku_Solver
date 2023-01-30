
# tests.py

import unittest

from sudoku import Board
from boards import *




class TestFullPuzzles(unittest.TestCase):
	def test_puzzles(self):
		pairs = {
			"easy": (easy, easy_solved),
			"hard": (hard, hard_solved),
			"expert": (expert, expert_solved),
			"hidden": (hidden, hidden_solved),
			"x_wing": (x_wing, x_wing_solved),
			"swordfish": (swordfish, swordfish_solved)
		}

		for key, (puzzle, solution) in pairs.items():
			board = Board(puzzle)
			board.solve()

			with self.subTest(level=key):
				assert board.to_string() == solution






if __name__ == "__main__":
	unittest.main()

