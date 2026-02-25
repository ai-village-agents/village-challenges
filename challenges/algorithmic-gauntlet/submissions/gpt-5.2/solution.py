"""Challenge 8: The Algorithmic Gauntlet (stdlib only).

Implements 5 required functions:
- balanced_brackets
- rle_encode / rle_decode
- lis_length
- eval_expr
- shortest_path
"""

from __future__ import annotations

from bisect import bisect_left
import heapq


def balanced_brackets(s: str) -> bool:
    """Return True iff s contains balanced (), [], {} brackets."""
    pairs = {')': '(', ']': '[', '}': '{'}
    opens = set(pairs.values())
    stack: list[str] = []
    for ch in s:
        if ch in opens:
            stack.append(ch)
        else:
            want = pairs.get(ch)
            if want is None:
                # Spec says only bracket chars appear; treat unknown as unbalanced.
                return False
            if not stack or stack[-1] != want:
                return False
            stack.pop()
    return not stack


def rle_encode(s: str) -> str:
    """Run-length encode: single chars as-is; runs >=2 as <char><count>."""
    if not s:
        return ""

    out: list[str] = []
    cur = s[0]
    run = 1
    for ch in s[1:]:
        if ch == cur:
            run += 1
        else:
            out.append(cur)
            if run > 1:
                out.append(str(run))
            cur = ch
            run = 1
    out.append(cur)
    if run > 1:
        out.append(str(run))
    return "".join(out)


def rle_decode(s: str) -> str:
    """Inverse of rle_encode for the specified format."""
    out: list[str] = []
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]
        i += 1

        # parse a (possibly multi-digit) count
        j = i
        while j < n and s[j].isdigit():
            j += 1
        if j == i:
            count = 1
        else:
            count = int(s[i:j])
        out.append(ch * count)
        i = j

    return "".join(out)


def lis_length(nums: list[int]) -> int:
    """Length of the longest strictly-increasing subsequence (O(n log n))."""
    # Patience sorting: tails[k] = minimum possible tail of an inc subseq of len k+1
    tails: list[int] = []
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)


class _ExprParser:
    __slots__ = ("s", "i", "n")

    def __init__(self, s: str):
        self.s = s
        self.i = 0
        self.n = len(s)

    def _skip_ws(self) -> None:
        s = self.s
        i = self.i
        n = self.n
        while i < n and s[i].isspace():
            i += 1
        self.i = i

    def _peek(self) -> str | None:
        self._skip_ws()
        if self.i >= self.n:
            return None
        return self.s[self.i]

    def _consume(self, ch: str) -> bool:
        if self._peek() == ch:
            self.i += 1
            return True
        return False

    def _expect(self, ch: str) -> None:
        if not self._consume(ch):
            raise ValueError(f"Expected {ch!r} at position {self.i}")

    def _number(self) -> float:
        self._skip_ws()
        start = self.i
        s = self.s
        n = self.n

        saw_digit = False

        # digits before dot (optional)
        while self.i < n and s[self.i].isdigit():
            saw_digit = True
            self.i += 1

        # optional dot + digits (digits after dot optional, e.g. '5.')
        if self.i < n and s[self.i] == '.':
            self.i += 1
            while self.i < n and s[self.i].isdigit():
                saw_digit = True
                self.i += 1

        # Require at least one digit overall (so '.' alone is invalid)
        if not saw_digit:
            raise ValueError(f"Expected number at position {start}")

        return float(s[start:self.i])

    def parse(self) -> float:
        val = self._expr()
        self._skip_ws()
        if self.i != self.n:
            raise ValueError(f"Unexpected trailing input at position {self.i}")
        return val

    def _expr(self) -> float:
        val = self._term()
        while True:
            if self._consume('+'):
                val += self._term()
            elif self._consume('-'):
                val -= self._term()
            else:
                return val

    def _term(self) -> float:
        val = self._factor()
        while True:
            if self._consume('*'):
                val *= self._factor()
            elif self._consume('/'):
                val /= self._factor()
            else:
                return val

    def _factor(self) -> float:
        # unary +/-
        if self._consume('+'):
            return self._factor()
        if self._consume('-'):
            return -self._factor()

        ch = self._peek()
        if ch == '(':
            self.i += 1
            val = self._expr()
            self._expect(')')
            return val

        return self._number()


def eval_expr(expr: str) -> float:
    """Evaluate an arithmetic expression with + - * /, parens, unary minus."""
    return _ExprParser(expr).parse()


def shortest_path(grid: list[list[int]]) -> int:
    """Minimum cost path in a 4-neighbor weighted grid (includes start+end)."""
    if not grid or not grid[0]:
        raise ValueError("grid must be non-empty")

    n = len(grid)
    m = len(grid[0])

    # Dijkstra
    INF = 10**30
    dist = [[INF] * m for _ in range(n)]
    dist[0][0] = grid[0][0]

    heap: list[tuple[int, int, int]] = [(dist[0][0], 0, 0)]
    while heap:
        d, r, c = heapq.heappop(heap)
        if d != dist[r][c]:
            continue
        if r == n - 1 and c == m - 1:
            return d

        nd_base = d
        if r > 0:
            nd = nd_base + grid[r - 1][c]
            if nd < dist[r - 1][c]:
                dist[r - 1][c] = nd
                heapq.heappush(heap, (nd, r - 1, c))
        if r + 1 < n:
            nd = nd_base + grid[r + 1][c]
            if nd < dist[r + 1][c]:
                dist[r + 1][c] = nd
                heapq.heappush(heap, (nd, r + 1, c))
        if c > 0:
            nd = nd_base + grid[r][c - 1]
            if nd < dist[r][c - 1]:
                dist[r][c - 1] = nd
                heapq.heappush(heap, (nd, r, c - 1))
        if c + 1 < m:
            nd = nd_base + grid[r][c + 1]
            if nd < dist[r][c + 1]:
                dist[r][c + 1] = nd
                heapq.heappush(heap, (nd, r, c + 1))

    # Grid is connected under 4-neighbor moves, so this shouldn't happen.
    return dist[n - 1][m - 1]
