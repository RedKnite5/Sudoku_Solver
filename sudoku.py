# sudoku.py

from typing import Literal, Callable

easy = """
000005409
451002300
982000561
607000980
003460000
500287010
040070096
300000700
005946802
"""

hard = """
530002000
009030200
027000010
700000000
018090005
090100002
000410070
085700029
004900500
"""

expert = """
479005000
000030008
000000060
340000001
006050009
800000006
000000427
007000000
000190000
"""

hidden = """
380290154
400050890
195000000
608000319
000010008
001000506
800000005
514080032
269345781
"""

evil = """
000600010
007000000
820009300
004000500
003007000
570900006
000080003
950002800
400000000
"""

#ToDo:
#  X-Wing
#  XY-Wing


class Board(object):
	def __init__(self, string: str):
		
		data = string.split("\n")
		
		self.size = len(data)
		digits = {i for i in range(1, self.size + 1)}
		
		self.board = [
			[{int(data[j][i])} if int(data[j][i]) else digits.copy()
			for i
			in range(self.size)] for j in range(self.size)
		]

	def sudoku(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> bool:
		present = set()
		modified = False
		
		squares = self.segment(direction, num)
		
		for square in squares:
			if len(square) == 1:
				present.add(next(iter(square)))
		
		for square in squares:
			if len(square) > 1:
				if not modified and present & square:
					modified = True
				square -= present
		
		return modified
	
	def naked_single(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> bool:
		modified = False
		
		squares = self.segment(direction, num)
		
		for d in range(1, self.size + 1):
			count = 0
			location = set()
			for square in squares:
				if d in square:
					count += 1
					location = square
			if count == 1 and len(location) > 1:
				location.clear()
				location.add(d)
				modified = True
		
		return modified

	def pair(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> bool:
		modified = False
		
		squares = self.segment(direction, num)
		
		pairs: dict[frozenset[int], int] = {}
		for square in squares:
			if len(square) == 2:
				pairs.setdefault(frozenset(square), 0)
				pairs[frozenset(square)] += 1
		
		for square in squares:
			for key, value in pairs.items():
				if value != 2 or square == set(key):
					continue
				
				if not modified and set(key) & square:
					modified = True
				square -= set(key)
		
		return modified
	
	# notepad++ highlighting bug? triple is not a keyword
	def triple(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> bool:
		modified = False
		
		squares = self.segment(direction, num)
		
		triples: dict[frozenset[int], int] = {}
		for square in squares:
			if len(square) == 3:
				triples.setdefault(frozenset(square), 0)
				triples[frozenset(square)] += 1

		for square in squares:
			if len(square) == 2:
				for key in triples:
					if square.issubset(key):
						triples[key] += 1
		
		for square in squares:
			for key, value in triples.items():
				if value != 3 or square.issubset(key):
					continue
				
				if not modified and set(key) & square:
					modified = True
				square -= set(key)
		
		return modified

	def hidden_pair(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> bool:
		modified = False
		
		squares = self.segment(direction, num)
		
		digits = {}
		for d in range(1, self.size + 1):
			for square in squares:
				if d in square:
					digits.setdefault(d, 0)
					digits[d] += 1
		
		digits = {d: c for d, c in digits.items() if c == 2}
		
		for d, count in digits.items():
			location = None
			location2 = None
			for square in squares:
				if d in square:
					if location is None:
						location = square
					else:
						location2 = square
						break
			
			intersect = {shared for shared in location & location2 if shared in digits}
			if len(intersect) == 2:
				for square in squares:
					if square not in (location, location2):
						if square & intersect:
							modified = True
							square -= intersect
				
				if not (len(location) == 2 and location == location2):
					modified = True
					location.clear()
					location2.clear()
					location |= intersect
					location2 |= intersect
		if modified:
			print("Hidden Pair!!!")
		return modified

	def x_wing(self, direction: Literal["hori", "vert"]) -> bool:
		modified = False
		
		for row in self.board:
		
			digits = {}
			for d in range(1, self.size + 1):
				for square in row:
					if d in square:
						digits.setdefault(d, 0)
						digits[d] += 1
			digits = {d: c for d, c in digits.items() if c == 2}
			
			

	def segment(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> list[set[int]]:
		if direction == "hori":
			return self.board[num]
		elif direction == "vert":
			return [row[num] for row in self.board]
		elif direction == "box":
			return [self.board[3 * (num // 3) + i // 3][3 * (num % 3) + i % 3]
				for i in range(self.size)]
		else:
			raise ValueError(f"direction must be 'hori', 'vert', or 'box', not {direction}")

	def show(self) -> str:
		s = "-" * 4 * self.size + "\n|"
		
		for row in self.board:
			for i in range(3):
				for square in row:
					for j in range(1, 4):
						d = i * 3 + j
						if d in square:
							s += str(d)
						else:
							s += " "
					s += "|"
				s += "\n|"
			s += "-" * 4 * self.size + "\n|"
		
		return s[:-1]

	def __str__(self) -> str:
		return self.show()

	def solve(self) -> None:

		modified = self.basic_pass()
		while modified:
			modified = self.basic_pass()
			if not modified:
				modified = modified or self.check_strategy(self.triple)
				modified = modified or self.check_strategy(self.hidden_pair)

	def basic_pass(self) -> bool:

		mod = False
		
		mod = mod or self.check_strategy(self.sudoku)
		mod = mod or self.check_strategy(self.naked_single)
		mod = mod or self.check_strategy(self.pair)
		
		return mod

	def check_strategy(self,
		strategy: Callable[
			[Literal["hori", "vert", "box"], int],
			bool]) -> bool:

		mod = False
		for i in range(self.size):
			mod = mod or strategy("hori", i)
			mod = mod or strategy("vert", i)
			mod = mod or strategy("box", i)
		return mod
	
	def to_string(self) -> str:

		s = ""
		for row in self.board:
			for square in row:
				if len(square) == 1:
					s += str(next(iter(square)))
				else:
					s += "0"
			s += "\n"
		return s


board = Board(evil[1:-1])
board.solve()
print(board)
rep = board.to_string()
print(rep)
if "0" in rep:
	print("unsolved")

	
	
	

