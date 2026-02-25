"""
Challenge 8: The Algorithmic Gauntlet
Solution by: Opus 4.5 Claude Code
"""

import heapq
from bisect import bisect_left


# Task 1: Balanced Brackets
def balanced_brackets(s: str) -> bool:
    """Check if brackets are balanced."""
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()
    
    return len(stack) == 0


# Task 2: Run-Length Encoding/Decoding
def rle_encode(s: str) -> str:
    """Encode string using run-length encoding."""
    if not s:
        return ""
    
    result = []
    count = 1
    prev = s[0]
    
    for i in range(1, len(s)):
        if s[i] == prev:
            count += 1
        else:
            if count == 1:
                result.append(prev)
            else:
                result.append(f"{prev}{count}")
            prev = s[i]
            count = 1
    
    # Handle last run
    if count == 1:
        result.append(prev)
    else:
        result.append(f"{prev}{count}")
    
    return "".join(result)


def rle_decode(s: str) -> str:
    """Decode run-length encoded string."""
    if not s:
        return ""
    
    result = []
    i = 0
    
    while i < len(s):
        char = s[i]
        i += 1
        
        # Check if followed by digits
        num_str = ""
        while i < len(s) and s[i].isdigit():
            num_str += s[i]
            i += 1
        
        if num_str:
            result.append(char * int(num_str))
        else:
            result.append(char)
    
    return "".join(result)


# Task 3: Longest Increasing Subsequence Length
def lis_length(nums: list[int]) -> int:
    """Return length of longest strictly increasing subsequence."""
    if not nums:
        return 0
    
    # O(n log n) solution using patience sorting
    tails = []
    
    for num in nums:
        pos = bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    
    return len(tails)


# Task 4: Evaluate Arithmetic Expression
def eval_expr(expr: str) -> float:
    """Evaluate arithmetic expression without using eval()."""
    # Recursive descent parser
    
    class Parser:
        def __init__(self, expression):
            self.expr = expression.replace(" ", "")
            self.pos = 0
        
        def parse(self):
            result = self.parse_expression()
            return result
        
        def parse_expression(self):
            """Parse addition and subtraction (lowest precedence)."""
            left = self.parse_term()
            
            while self.pos < len(self.expr) and self.expr[self.pos] in '+-':
                op = self.expr[self.pos]
                self.pos += 1
                right = self.parse_term()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            
            return left
        
        def parse_term(self):
            """Parse multiplication and division (higher precedence)."""
            left = self.parse_factor()
            
            while self.pos < len(self.expr) and self.expr[self.pos] in '*/':
                op = self.expr[self.pos]
                self.pos += 1
                right = self.parse_factor()
                if op == '*':
                    left = left * right
                else:
                    left = left / right
            
            return left
        
        def parse_factor(self):
            """Parse numbers, unary minus, and parentheses."""
            # Handle unary minus
            if self.pos < len(self.expr) and self.expr[self.pos] == '-':
                self.pos += 1
                return -self.parse_factor()
            
            # Handle unary plus
            if self.pos < len(self.expr) and self.expr[self.pos] == '+':
                self.pos += 1
                return self.parse_factor()
            
            # Handle parentheses
            if self.pos < len(self.expr) and self.expr[self.pos] == '(':
                self.pos += 1  # Skip '('
                result = self.parse_expression()
                self.pos += 1  # Skip ')'
                return result
            
            # Parse number
            return self.parse_number()
        
        def parse_number(self):
            """Parse a number (integer or decimal)."""
            start = self.pos
            
            # Parse digits before decimal point
            while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                self.pos += 1
            
            # Parse decimal point and digits after
            if self.pos < len(self.expr) and self.expr[self.pos] == '.':
                self.pos += 1
                while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                    self.pos += 1
            
            return float(self.expr[start:self.pos])
    
    parser = Parser(expr)
    return parser.parse()


# Task 5: Shortest Path in Weighted Grid
def shortest_path(grid: list[list[int]]) -> int:
    """Find minimum cost path from top-left to bottom-right using Dijkstra's."""
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    
    # Distance matrix initialized to infinity
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = grid[0][0]
    
    # Priority queue: (distance, row, col)
    pq = [(grid[0][0], 0, 0)]
    
    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while pq:
        d, r, c = heapq.heappop(pq)
        
        # If we've reached the destination
        if r == rows - 1 and c == cols - 1:
            return d
        
        # Skip if we've already found a better path
        if d > dist[r][c]:
            continue
        
        # Explore neighbors
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < rows and 0 <= nc < cols:
                new_dist = d + grid[nr][nc]
                
                if new_dist < dist[nr][nc]:
                    dist[nr][nc] = new_dist
                    heapq.heappush(pq, (new_dist, nr, nc))
    
    return dist[rows - 1][cols - 1]
