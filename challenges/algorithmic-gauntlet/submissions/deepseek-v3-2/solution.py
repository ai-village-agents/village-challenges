"""
Solutions for Challenge 8: Algorithmic Gauntlet.
Implements balanced brackets, RLE encode/decode, LIS length,
expression evaluator, and grid shortest path (Dijkstra).
"""

from bisect import bisect_left
import heapq
import re
from typing import List


def balanced_brackets(s: str) -> bool:
    """Return True if (), [], {} are balanced and properly nested."""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    opens = set(pairs.values())

    for ch in s:
        if ch in opens:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        # ignore other characters
    return not stack


def rle_encode(s: str) -> str:
    """
    Run-length encode the string.
    Single characters remain as-is; runs of 2+ become char followed by count.
    """
    if not s:
        return ""
    res = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            if count == 1:
                res.append(s[i - 1])
            else:
                res.append(f"{s[i - 1]}{count}")
            count = 1
    # flush last run
    if count == 1:
        res.append(s[-1])
    else:
        res.append(f"{s[-1]}{count}")
    return "".join(res)


def rle_decode(s: str) -> str:
    """Decode a run-length encoded string produced by rle_encode."""
    res = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        i += 1
        count_start = i
        while i < n and s[i].isdigit():
            i += 1
        count_str = s[count_start:i]
        count = int(count_str) if count_str else 1
        res.append(ch * count)
    return "".join(res)


def lis_length(nums: List[int]) -> int:
    """Return length of the longest strictly increasing subsequence in O(n log n)."""
    tails = []  # tails[i] = smallest tail of an increasing subsequence of length i+1
    for num in nums:
        idx = bisect_left(tails, num)
        if idx == len(tails):
            tails.append(num)
        else:
            tails[idx] = num
    return len(tails)


class _ExprParser:
    """Recursive descent parser for +, -, *, / with parentheses and unary signs."""

    number_pattern = re.compile(r"\d+(?:\.\d+)?|\.\d+")

    def __init__(self, expr: str):
        self.expr = expr
        self.n = len(expr)
        self.i = 0

    def parse(self) -> float:
        val = self._parse_expression()
        self._skip_ws()
        if self.i != self.n:
            raise ValueError(f"Unexpected token at position {self.i}")
        return val

    def _skip_ws(self) -> None:
        while self.i < self.n and self.expr[self.i].isspace():
            self.i += 1

    def _parse_expression(self) -> float:
        """expression := term {( '+' | '-' ) term}"""
        val = self._parse_term()
        while True:
            self._skip_ws()
            if self._match('+'):
                val += self._parse_term()
            elif self._match('-'):
                val -= self._parse_term()
            else:
                break
        return val

    def _parse_term(self) -> float:
        """term := factor {( '*' | '/' ) factor}"""
        val = self._parse_factor()
        while True:
            self._skip_ws()
            if self._match('*'):
                val *= self._parse_factor()
            elif self._match('/'):
                divisor = self._parse_factor()
                val /= divisor
            else:
                break
        return val

    def _parse_factor(self) -> float:
        """
        factor := {('+' | '-') } ( number | '(' expression ')' )
        Allows multiple unary signs.
        """
        self._skip_ws()
        sign = 1
        while True:
            if self._match('+'):
                pass
            elif self._match('-'):
                sign *= -1
            else:
                break
            self._skip_ws()

        self._skip_ws()
        if self._match('('):
            val = self._parse_expression()
            self._skip_ws()
            if not self._match(')'):
                raise ValueError(f"Missing closing parenthesis at position {self.i}")
            return sign * val

        num = self._parse_number()
        return sign * num

    def _parse_number(self) -> float:
        self._skip_ws()
        match = self.number_pattern.match(self.expr, self.i)
        if not match:
            raise ValueError(f"Expected number at position {self.i}")
        num_str = match.group(0)
        self.i = match.end()
        return float(num_str)

    def _match(self, ch: str) -> bool:
        if self.i < self.n and self.expr[self.i] == ch:
            self.i += 1
            return True
        return False


def eval_expr(expr: str) -> float:
    """
    Evaluate arithmetic expression containing +, -, *, /, parentheses, unary minus/plus,
    and whitespace. Uses recursive descent parsing; no eval/exec.
    """
    parser = _ExprParser(expr)
    return parser.parse()


def shortest_path(grid: List[List[int]]) -> int:
    """
    Minimum cost path from top-left to bottom-right in a weighted grid using Dijkstra.
    Movement allowed up, down, left, right. Includes cost of the starting cell.
    """
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    heap = [(grid[0][0], 0, 0)]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while heap:
        cost, r, c = heapq.heappop(heap)
        if cost != dist[r][c]:
            continue  # stale entry
        if (r, c) == (rows - 1, cols - 1):
            return cost
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_cost = cost + grid[nr][nc]
                if new_cost < dist[nr][nc]:
                    dist[nr][nc] = new_cost
                    heapq.heappush(heap, (new_cost, nr, nc))
    return dist[rows - 1][cols - 1]
