"""
Challenge 8: Algorithmic Gauntlet
Submitted by: Claude Sonnet 4.6
"""
import bisect
import heapq
import re


def balanced_brackets(s: str) -> bool:
    """Return True if all brackets in s are balanced, False otherwise."""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0


def rle_encode(s: str) -> str:
    """Run-length encode a string. e.g. 'aaabb' -> 'a3b2', single chars omit count."""
    if not s:
        return ''
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(s[i-1] if count == 1 else f"{s[i-1]}{count}")
            count = 1
    result.append(s[-1] if count == 1 else f"{s[-1]}{count}")
    return ''.join(result)


def rle_decode(s: str) -> str:
    """Decode a run-length encoded string. e.g. 'a3b2' -> 'aaabb'"""
    result = []
    i = 0
    while i < len(s):
        ch = s[i]
        i += 1
        # collect digits
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        if j > i:
            count = int(s[i:j])
            i = j
        else:
            count = 1
        result.append(ch * count)
    return ''.join(result)


def lis_length(nums: list) -> int:
    """Return the length of the longest increasing subsequence (O(n log n))."""
    tails = []
    for n in nums:
        i = bisect.bisect_left(tails, n)
        if i == len(tails):
            tails.append(n)
        else:
            tails[i] = n
    return len(tails)


def eval_expr(expr: str) -> float:
    """Evaluate a mathematical expression string with +, -, *, /, and parentheses."""
    expr = expr.replace(' ', '')
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isdigit() or expr[i] == '.':
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(float(expr[i:j]))
            i = j
        else:
            tokens.append(expr[i])
            i += 1

    pos = [0]

    def parse_expr():
        left = parse_term()
        while pos[0] < len(tokens) and tokens[pos[0]] in ('+', '-'):
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_term()
            left = left + right if op == '+' else left - right
        return left

    def parse_term():
        left = parse_factor()
        while pos[0] < len(tokens) and tokens[pos[0]] in ('*', '/'):
            op = tokens[pos[0]]
            pos[0] += 1
            right = parse_factor()
            left = left * right if op == '*' else left / right
        return left

    def parse_factor():
        # handle unary minus
        if pos[0] < len(tokens) and tokens[pos[0]] == '-':
            pos[0] += 1
            return -parse_factor()
        # handle unary plus
        if pos[0] < len(tokens) and tokens[pos[0]] == '+':
            pos[0] += 1
            return parse_factor()
        if tokens[pos[0]] == '(':
            pos[0] += 1
            val = parse_expr()
            pos[0] += 1  # consume ')'
            return val
        val = tokens[pos[0]]
        pos[0] += 1
        return val

    return parse_expr()


def shortest_path(grid: list) -> int:
    """
    Find the shortest path from top-left to bottom-right of a weighted grid
    using Dijkstra's algorithm. Returns the minimum cost (sum of cell weights).
    """
    rows, cols = len(grid), len(grid[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    heap = [(grid[0][0], 0, 0)]

    while heap:
        d, r, c = heapq.heappop(heap)
        if d > dist[r][c]:
            continue
        if r == rows - 1 and c == cols - 1:
            return d
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                nd = d + grid[nr][nc]
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    heapq.heappush(heap, (nd, nr, nc))

    return dist[rows - 1][cols - 1]
