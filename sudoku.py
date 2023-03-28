# sudoku.py

from dataclasses import dataclass, field
from functools import reduce
from operator import and_, or_
from itertools import chain

from typing import Literal, Callable
import logging as log

from boards import *

log.basicConfig(level=log.DEBUG)



#ToDo:
#  more general fish
#  XY-Wing


@dataclass
class FishParts:
	segments: list[tuple[set[int]]] = field(default_factory=list)
	segnums: list[int] = field(default_factory=list)
	digits: list[set[int]] = field(default_factory=list)

def in_identity(x, container):
	return any(x is obj for obj in container)


class Board(object):
	def __init__(self, string: str):

		data = string.split("\n")

		self.size = len(data)
		digits = {i for i in range(1, self.size + 1)}

		self.board = tuple(
			tuple({int(data[j][i])} if int(data[j][i]) else digits.copy()
			for i
			in range(self.size)) for j in range(self.size)
		)

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

		log.info("checking for pair")

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

	def triple(self,
				direction: Literal["hori", "vert", "box"],
				num: int) -> bool:
		modified = False

		log.info("checking for triple")

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

		log.info("checking for hidden pair")

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
				if d not in square:
					continue

				if location is None:
					location = square
				else:
					location2 = square
					break

			intersect = {shared for shared in location & location2 if shared in digits}
			if len(intersect) != 2:
				continue

			for square in squares:
				if square not in (location, location2):
					if square & intersect:
						modified = True
						square -= intersect

			if len(location) == 2 and location == location2:
				continue

			modified = True
			location.clear()
			location2.clear()
			location |= intersect
			location2 |= intersect

		if modified:
			log.info("Hidden Pair!!!")
		return modified

	def x_wing(self):
		log.info("hori")
		hori = self._fish("hori", 2)
		log.info("vert")
		vert = self._fish("vert", 2)
		return hori or vert

	def swordfish(self):
		log.info("hori")
		hori = self._fish("hori", 3)
		#log.info("vert")
		#vert = self._fish("vert", 3)
		return hori #or vert

	def _fish(
		self,
		direction: Literal["hori", "vert"],
		size: int,
		iteration = 0,
		data = None
		) -> bool:
		"""Check for fish. Size indicates how large the fish is."""
		log.info(f"Checking for size {size} fish")
		log.debug(str(self))

		if data is None:
			data = FishParts()

		board = self.board if direction == "hori" else tuple(zip(*self.board))
		start = data.segnums[iteration-1] if len(data.segnums) > 0 else -1
		log.debug(f"{start = }, {iteration = }, {data.segnums = }")
		for segnum, seg in enumerate(board[start+1:]):

			digits = self.digits_with_n_or_less_places(seg, size)
			segnum += start + 1

			if segnum in data.segnums:
				assert False  # should not happen
				continue

			# check if common numbers in all the rows/columns
			if not (candidates := reduce(and_, data.digits, digits)):
				continue

			log.debug(f"_fish {data.digits = }")
			log.debug(f"_fish {digits = }")
			log.debug(f"_fish {segnum = }")
			log.debug(f"_fish {seg = }")
			log.debug(f"_fish {candidates = }")

			data.segments.append(seg)
			data.segnums.append(segnum)
			data.digits.append(candidates)

			if iteration == size-1:
				modified = self.fish_segments(direction, size, data)
				if modified:
					log.info("return segments success!")
			else:
				modified = self._fish(direction, size, iteration+1, data)

			if modified:
				return True

			data.segments.pop()
			data.segnums.pop()
			data.digits.pop()

		return False

	def digits_with_n_or_less_places(
		self, squares: tuple[set[int]], n: int
	) -> set[int]:
		digit_counts = {}
		for d in range(1, self.size + 1):
			for square in squares:
				# should do this with filter and len
				if d in square:
					digit_counts.setdefault(d, 0)
					digit_counts[d] += 1
		digits = {d for d, c in digit_counts.items() if c <= n and c > 1}
		return digits

	def cand_in_wrong_cross_seg(
		self,
		direction: Literal["hori", "vert"],
		digits: set[int],
		nums1: list[int],
		nums2: list[int]) -> bool:
		""" """
		board = self.board if direction == "hori" else tuple(zip(*self.board))
		for d in digits:
			for index in nums1:
				total_count = sum(1 for segment in board[index] if d in segment)
				sub_count = len(tuple(filter(lambda st: d in st, (self.board[seg][i] for i in nums2))))
				log.debug(f"{total_count = } {sub_count = }")
				if total_count != sub_count:
					return False
		return True



	def fish_segments(
		self,
		direction: Literal["hori", "vert"],
		size: int,
		data: FishParts,
		iteration: int = 0,
		cross_data: FishParts=None) -> bool:

		if cross_data is None:
			cross_data = FishParts()

		log.info("Fish segments")

		# oppasite direction as in _fish

		#segtype = "row" if direction == "hori" else "col"
		#log.debug(f"Examining {segtype}: {segnum1} and {segnum2}")
		#log.debug(f"{segtype} {segnum1} is {seg1}")
		#log.debug(f"{segtype} {segnum2} is {seg2}")
		#log.debug(f"the common digit or digits are {common}")

		start = cross_data.segnums[iteration-1] if len(cross_data.segnums) > 0 else -1
		for index, squares in enumerate(tuple(zip(*data.segments))[start+1:]):
			digits = self.digits_with_n_or_less_places(squares, size)

			# need to check all occurances of the digit are acutally in the colnms

			if not (candidates := reduce(and_, chain(cross_data.digits, data.digits), digits)):
				log.debug(f"fish segments: {candidates = }")
				log.debug(f"fish segments: {data.digits, cross_data.digits, digits}")
				continue

			if self.cand_in_wrong_cross_seg(
				direction,
				candidates,
				data.segnums,
				cross_data.segnums + [index]):
				continue

			index += start + 1
			log.debug(f"{data.digits = }")
			log.debug(f"{cross_data.digits = }")
			log.debug(f"{squares = }")
			log.debug(f"{index = }")
			log.debug(f"{data.segnums = }")
			log.debug(f"{candidates = }")

			cross_data.segments.append(squares)
			cross_data.segnums.append(index)
			cross_data.digits.append(candidates)

			if iteration == size-1:
				modified = self.remove_fishy_dupes(direction, cross_data)
			else:
				modified = self.fish_segments(direction, size, data, iteration+1, cross_data)

			if modified:
				return True

			s = cross_data.segments.pop()
			cross_data.segnums.pop()
			cross_data.digits.pop()

			log.debug(f"popped: {s}")
		return False

	def remove_fishy_dupes(self, direction, cross_data):
		log.info("remove_fishy_dupes")

		oppisite = "vert" if direction == "hori" else "hori"
		cover_segments = zip(
			*map(lambda index: self.segment(oppisite, index), cross_data.segnums)
		)

		modified = False
		for non_base_cands in cover_segments:

			# not working
			is_bases = any(in_identity(cand, chain(*cross_data.segments)) for cand in non_base_cands)
			log.debug(f"is bases: {is_bases}")
			log.debug(f"{non_base_cands[0] = } continer[0] = {tuple(chain(*cross_data.segments))[0]}")
			log.debug(f"Basis: {tuple(chain(*cross_data.segments))}")
			log.debug(f"{is_bases = }")
			log.debug(f"candidates: {cross_data.digits[-1]}")

			if self.non_trival_overlap(
				cross_data.digits[-1],
				non_base_cands,
				is_bases
			):
				modified = True
				log.debug(f"{non_base_cands = }")
				log.debug(f"{direction = }")

				print(f"Before {cross_data.segnums}:\n {self}")

				log.debug(f"removing {cross_data.digits[-1]}")
				for not_base in non_base_cands:
					not_base -= cross_data.digits[-1]
				print("After:\n", self)
		#if modified:
			#log.debug(str(self))
			#log.info(f"{direction} x-wing!!!")

			#log.info(f"bases: {(square1a, square1b, square2a, square2b)}")
			#log.info(f"rows or cols: {segnum1, segnum2}")
		return modified


	def non_trival_overlap(
		self, final_cand, non_base_cands, is_bases):
		"""Check if squares contain the digit that is to be ruled out and that
		these are not the squares that form the x-wing"""

		#overlap: bool = not is_bases
		#for cand in non_base_cands:
		#	overlap = overlap or final_cand & cand
		#return overlap

		return any(map(lambda cand: final_cand & cand, non_base_cands)) and not is_bases


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
				#modified = modified or self.x_wing()
				modified = modified or self.swordfish()

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
				elif len(square) == 0:
					s += "X"
				else:
					s += "0"
			s += "\n"
		return s



def main():
	board = Board(expert)
	board.solve()
	print(board)
	rep = board.to_string()
	print(rep)
	if "X" in rep:
		print("ERROR")
	elif "0" in rep:
		print("unsolved")



if __name__ == "__main__":
	main()



