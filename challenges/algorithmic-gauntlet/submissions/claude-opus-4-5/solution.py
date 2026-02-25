"""
Challenge 8: The Algorithmic Gauntlet
Solution by Claude Opus 4.5
"""
import heapq
from typing import List


# Task 1: Balanced Brackets
def balanced_brackets(s: str) -> bool:
    """Return True if brackets are balanced, False otherwise."""
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
    """Compress using run-length encoding. Single chars stay as-is; runs of 2+ become char+count."""
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
    """Reverse the run-length encoding."""
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


# Task 3: Longest Increasing Subsequence Length (O(n log n) algorithm)
def lis_length(nums: list[int]) -> int:
    """Return the length of the longest strictly increasing subsequence."""
    if not nums:
        return 0
    
    # tails[i] = smallest tail element for LIS of length i+1
    tails = []
    
    for num in nums:
        # Binary search for the position where num should go
        left, right = 0, len(tails)
        while left < right:
            mid = (left + right) // 2
            if tails[mid] < num:
                left = mid + 1
            else:
                right = mid
        
        if left == len(tails):
            tails.append(num)
        else:
            tails[left] = num
    
    return len(tails)


# Task 4: Evaluate Arithmetic Expression (recursive descent parser)
def eval_expr(expr: str) -> float:
    """Evaluate a mathematical expression without using eval()."""
    
    class Parser:
        def __init__(self, expression: str):
            self.expr = expression.replace(" ", "")
            self.pos = 0
        
        def parse(self) -> float:
            result = self.parse_expression()
            return result
        
        def parse_expression(self) -> float:
            """Parse addition and subtraction (lowest precedence)."""
            result = self.parse_term()
            
            while self.pos < len(self.expr) and self.expr[self.pos] in '+-':
                op = self.expr[self.pos]
                self.pos += 1
                right = self.parse_term()
                if op == '+':
                    result += right
                else:
                    result -= right
            
            return result
        
        def parse_term(self) -> float:
            """Parse multiplication and division (higher precedence)."""
            result = self.parse_factor()
            
            while self.pos < len(self.expr) and self.expr[self.pos] in '*/':
                op = self.expr[self.pos]
                self.pos += 1
                right = self.parse_factor()
                if op == '*':
                    result *= right
                else:
                    result /= right
            
            return result
        
        def parse_factor(self) -> float:
            """Parse numbers, parentheses, and unary minus."""
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
                self.pos += 1  # skip '('
                result = self.parse_expression()
                self.pos += 1  # skip ')'
                return result
            
            # Parse number (integer or decimal)
            start = self.pos
            while self.pos < len(self.expr) and (self.expr[self.pos].isdigit() or self.expr[self.pos] == '.'):
                self.pos += 1
            
            return float(self.expr[start:self.pos])
    
    parser = Parser(expr)
    return parser.parse()


# Task 5: Shortest Path in Weighted Grid (Dijkstra's algorithm)
def shortest_path(grid: list[list[int]]) -> int:
    """Find minimum cost path from top-left to bottom-right using Dijkstra's."""
    if not grid or not grid[0]:
        return 0
    
    n, m = len(grid), len(grid[0])
    
    # Distance array
    dist = [[float('inf')] * m for _ in range(n)]
    dist[0][0] = grid[0][0]
    
    # Min-heap: (cost, row, col)
    heap = [(grid[0][0], 0, 0)]
    
    # 4 directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while heap:
        cost, row, col = heapq.heappop(heap)
        
        # If we've reached the destination
        if row == n - 1 and col == m - 1:
            return cost
        
        # Skip if we've found a better path already
        if cost > dist[row][col]:
            continue
        
        # Explore neighbors
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            if 0 <= new_row < n and 0 <= new_col < m:
                new_cost = cost + grid[new_row][new_col]
                
                if new_cost < dist[new_row][new_col]:
                    dist[new_row][new_col] = new_cost
                    heapq.heappush(heap, (new_cost, new_row, new_col))
    
    return dist[n-1][m-1]
