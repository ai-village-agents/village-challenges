from __future__ import annotations

from collections import deque
import heapq
from typing import List


# Task 1: Balanced Brackets

def balanced_brackets(s: str) -> bool:
    pairs = {')': '(', ']': '[', '}': '{'}
    stack: List[str] = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        else:
            if ch not in pairs:
                # According to spec, input only contains bracket chars; treat others as invalid
                return False
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


# Task 2: Run-Length Encoding/Decoding

def rle_encode(s: str) -> str:
    if not s:
        return ""
    result: List[str] = []
    current = s[0]
    count = 1
    for ch in s[1:]:
        if ch == current:
            count += 1
        else:
            if count == 1:
                result.append(current)
            else:
                result.append(f"{current}{count}")
            current = ch
            count = 1
    if count == 1:
        result.append(current)
    else:
        result.append(f"{current}{count}")
    return "".join(result)


def rle_decode(s: str) -> str:
    if not s:
        return ""
    result: List[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        i += 1
        # parse optional count (one or more digits)
        count = 0
        while i < n and s[i].isdigit():
            count = count * 10 + (ord(s[i]) - 48)
            i += 1
        if count == 0:
            count = 1
        result.append(ch * count)
    return "".join(result)


# Task 3: Longest Increasing Subsequence Length

def lis_length(nums: List[int]) -> int:
    # Standard patience sorting with binary search, O(n log n)
    if not nums:
        return 0
    tails: List[int] = []
    for x in nums:
        # Find leftmost index >= x
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(x)
        else:
            tails[lo] = x
    return len(tails)


# Task 4: Evaluate Arithmetic Expression

class _TokenStream:
    __slots__ = ("tokens", "pos")

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        tok = self.peek()
        if tok is None:
            return None
        if expected is not None and tok != expected:
            raise ValueError(f"Expected {expected!r}, got {tok!r}")
        self.pos += 1
        return tok


def _tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "+-*/()":
            tokens.append(ch)
            i += 1
        elif ch.isdigit() or ch == '.':
            j = i
            dot_seen = ch == '.'
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not dot_seen)):
                if expr[i] == '.':
                    dot_seen = True
                i += 1
            tokens.append(expr[j:i])
        else:
            raise ValueError(f"Invalid character in expression: {ch!r}")
    return tokens


def eval_expr(expr: str) -> float:
    tokens = _tokenize(expr)
    ts = _TokenStream(tokens)

    def parse_expression():
        value = parse_term()
        while True:
            tok = ts.peek()
            if tok == '+':
                ts.consume('+')
                value += parse_term()
            elif tok == '-':
                ts.consume('-')
                value -= parse_term()
            else:
                break
        return value

    def parse_term():
        value = parse_factor()
        while True:
            tok = ts.peek()
            if tok == '*':
                ts.consume('*')
                value *= parse_factor()
            elif tok == '/':
                ts.consume('/')
                divisor = parse_factor()
                value /= divisor
            else:
                break
        return value

    def parse_factor():
        tok = ts.peek()
        if tok == '+':
            ts.consume('+')
            return parse_factor()
        if tok == '-':
            ts.consume('-')
            return -parse_factor()
        if tok == '(': 
            ts.consume('(')
            value = parse_expression()
            ts.consume(')')
            return value
        # number
        tok = ts.consume()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        return float(tok)

    result = parse_expression()
    if ts.peek() is not None:
        raise ValueError("Unexpected trailing tokens")
    return float(result)


# Task 5: Shortest Path in Weighted Grid

def shortest_path(grid: List[List[int]]) -> int:
    if not grid or not grid[0]:
        raise ValueError("Grid must be non-empty")
    n, m = len(grid), len(grid[0])
    # Dijkstra's algorithm on grid cells
    dist = [[float('inf')] * m for _ in range(n)]
    dist[0][0] = grid[0][0]
    heap: list[tuple[int, int, int]] = [(grid[0][0], 0, 0)]
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while heap:
        cost, i, j = heapq.heappop(heap)
        if cost > dist[i][j]:
            continue
        if i == n - 1 and j == m - 1:
            return cost
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < m:
                new_cost = cost + grid[ni][nj]
                if new_cost < dist[ni][nj]:
                    dist[ni][nj] = new_cost
                    heapq.heappush(heap, (new_cost, ni, nj))
    # In a connected grid, we should always reach the target
    return dist[n - 1][m - 1]


if __name__ == "__main__":
    # tiny sanity checks
    assert balanced_brackets("({[]})") is True
    assert balanced_brackets("([)]") is False
    assert rle_decode(rle_encode("aaabbc")) == "aaabbc"
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert abs(eval_expr("2 + 3 * 4") - 14.0) < 1e-9
    assert shortest_path([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
