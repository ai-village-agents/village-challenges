"""Reference solution for Challenge 8: The Algorithmic Gauntlet"""

import bisect
import heapq

def balanced_brackets(s: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in '([{':
            stack.append(c)
        elif c in ')]}':
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
    return len(stack) == 0

def rle_encode(s: str) -> str:
    if not s:
        return ""
    result = []
    i = 0
    while i < len(s):
        c = s[i]
        count = 1
        while i + count < len(s) and s[i + count] == c:
            count += 1
        if count == 1:
            result.append(c)
        else:
            result.append(f"{c}{count}")
        i += count
    return "".join(result)

def rle_decode(s: str) -> str:
    if not s:
        return ""
    result = []
    i = 0
    while i < len(s):
        c = s[i]
        i += 1
        num = ""
        while i < len(s) and s[i].isdigit():
            num += s[i]
            i += 1
        if num:
            result.append(c * int(num))
        else:
            result.append(c)
    return "".join(result)

def lis_length(nums: list) -> int:
    if not nums:
        return 0
    tails = []
    for x in nums:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)

def eval_expr(expr: str) -> float:
    tokens = tokenize(expr)
    pos = [0]
    result = parse_expr(tokens, pos)
    return float(result)

def tokenize(expr):
    tokens = []
    i = 0
    expr = expr.strip()
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        if expr[i] in '+-*/()':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(float(expr[i:j]))
            i = j
        else:
            i += 1
    return tokens

def parse_expr(tokens, pos):
    left = parse_term(tokens, pos)
    while pos[0] < len(tokens) and tokens[pos[0]] in ('+', '-'):
        op = tokens[pos[0]]
        pos[0] += 1
        right = parse_term(tokens, pos)
        if op == '+':
            left += right
        else:
            left -= right
    return left

def parse_term(tokens, pos):
    left = parse_unary(tokens, pos)
    while pos[0] < len(tokens) and tokens[pos[0]] in ('*', '/'):
        op = tokens[pos[0]]
        pos[0] += 1
        right = parse_unary(tokens, pos)
        if op == '*':
            left *= right
        else:
            left /= right
    return left

def parse_unary(tokens, pos):
    if pos[0] < len(tokens) and tokens[pos[0]] == '-':
        pos[0] += 1
        return -parse_unary(tokens, pos)
    if pos[0] < len(tokens) and tokens[pos[0]] == '+':
        pos[0] += 1
        return parse_unary(tokens, pos)
    return parse_primary(tokens, pos)

def parse_primary(tokens, pos):
    if pos[0] < len(tokens) and tokens[pos[0]] == '(':
        pos[0] += 1
        result = parse_expr(tokens, pos)
        if pos[0] < len(tokens) and tokens[pos[0]] == ')':
            pos[0] += 1
        return result
    if pos[0] < len(tokens) and isinstance(tokens[pos[0]], float):
        val = tokens[pos[0]]
        pos[0] += 1
        return val
    return 0.0

def shortest_path(grid: list) -> int:
    if not grid or not grid[0]:
        return 0
    n, m = len(grid), len(grid[0])
    dist = [[float('inf')] * m for _ in range(n)]
    dist[0][0] = grid[0][0]
    heap = [(grid[0][0], 0, 0)]
    while heap:
        d, r, c = heapq.heappop(heap)
        if d > dist[r][c]:
            continue
        if r == n - 1 and c == m - 1:
            return d
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                nd = d + grid[nr][nc]
                if nd < dist[nr][nc]:
                    dist[nr][nc] = nd
                    heapq.heappush(heap, (nd, nr, nc))
    return dist[n-1][m-1]
