"""
Challenge 8: The Algorithmic Gauntlet - Claude Haiku 4.5 Solution
"""

import heapq
from bisect import bisect_left


def balanced_brackets(s: str) -> bool:
    """
    Task 1: Check if brackets are balanced.
    """
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    
    for char in s:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack or pairs[stack.pop()] != char:
                return False
    
    return len(stack) == 0


def rle_encode(s: str) -> str:
    """
    Task 2: Run-Length Encoding.
    Single characters stay as-is; runs of 2+ become <char><count>.
    """
    if not s:
        return ""
    
    result = []
    i = 0
    while i < len(s):
        char = s[i]
        count = 1
        while i + count < len(s) and s[i + count] == char:
            count += 1
        
        if count == 1:
            result.append(char)
        else:
            result.append(f"{char}{count}")
        i += count
    
    return "".join(result)


def rle_decode(s: str) -> str:
    """
    Task 2: Run-Length Decoding.
    Reverse the encoding: <char><count> becomes char repeated count times.
    """
    result = []
    i = 0
    while i < len(s):
        char = s[i]
        i += 1
        
        # Check if there's a number following
        num_str = ""
        while i < len(s) and s[i].isdigit():
            num_str += s[i]
            i += 1
        
        if num_str:
            count = int(num_str)
            result.append(char * count)
        else:
            result.append(char)
    
    return "".join(result)


def lis_length(nums: list[int]) -> int:
    """
    Task 3: Longest Increasing Subsequence - O(n log n) with binary search.
    """
    if not nums:
        return 0
    
    tails = []  # tails[i] = smallest tail of all increasing subsequences of length i+1
    
    for num in nums:
        pos = bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    
    return len(tails)


def eval_expr(expr: str) -> float:
    """
    Task 4: Evaluate arithmetic expression with +, -, *, / and parentheses.
    Uses recursive descent parsing.
    """
    expr = expr.replace(" ", "")
    pos = [0]
    
    def parse_expression():
        result = parse_term()
        while pos[0] < len(expr) and expr[pos[0]] in "+-":
            op = expr[pos[0]]
            pos[0] += 1
            right = parse_term()
            if op == '+':
                result += right
            else:
                result -= right
        return result
    
    def parse_term():
        result = parse_factor()
        while pos[0] < len(expr) and expr[pos[0]] in "*/":
            op = expr[pos[0]]
            pos[0] += 1
            right = parse_factor()
            if op == '*':
                result *= right
            else:
                result /= right
        return result
    
    def parse_factor():
        # Handle unary minus/plus at the factor level
        if pos[0] < len(expr) and expr[pos[0]] == '-':
            pos[0] += 1
            return -parse_factor()
        elif pos[0] < len(expr) and expr[pos[0]] == '+':
            pos[0] += 1
            return parse_factor()
        
        # Handle parentheses
        if pos[0] < len(expr) and expr[pos[0]] == '(':
            pos[0] += 1
            result = parse_expression()
            pos[0] += 1  # skip ')'
            return result
        
        # Parse number
        return parse_number()
    
    def parse_number():
        start = pos[0]
        if pos[0] < len(expr) and expr[pos[0]].isdigit():
            while pos[0] < len(expr) and expr[pos[0]].isdigit():
                pos[0] += 1
            if pos[0] < len(expr) and expr[pos[0]] == '.':
                pos[0] += 1
                while pos[0] < len(expr) and expr[pos[0]].isdigit():
                    pos[0] += 1
        return float(expr[start:pos[0]])
    
    return parse_expression()


def shortest_path(grid: list[list[int]]) -> int:
    """
    Task 5: Shortest path from top-left (0,0) to bottom-right (N-1, M-1).
    Uses Dijkstra's algorithm.
    """
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    
    pq = [(grid[0][0], 0, 0)]  # (cost, row, col)
    
    while pq:
        cost, r, c = heapq.heappop(pq)
        
        if cost > dist[r][c]:
            continue
        
        # Try all 4 directions
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_cost = cost + grid[nr][nc]
                if new_cost < dist[nr][nc]:
                    dist[nr][nc] = new_cost
                    heapq.heappush(pq, (new_cost, nr, nc))
    
    return dist[rows - 1][cols - 1]
