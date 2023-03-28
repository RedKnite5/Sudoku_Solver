#!/mnt/c/Users/RedKnite/AppData/Local/Programs/Python/Python310/python.exe
# tests.py

import unittest

from sudoku import Board
from boards import *



'''
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
'''


class Test_cand_in_wrong_cross_seg(unittest.TestCase):
	def test_xwing_positive(self):
		pat = """000000000
000000000
300000009
400000008
500000007
600000005
700000006
800000004
900000003"""
		board = Board(pat)
		val = board.cand_in_wrong_cross_seg("hori", {1}, [0, 1], [0, 9])
		self.assertTrue(val)



if __name__ == "__main__":
	unittest.main()

