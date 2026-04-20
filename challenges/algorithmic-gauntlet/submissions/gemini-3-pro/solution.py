import heapq
import math

# Task 1: Balanced Brackets
def balanced_brackets(s: str) -> bool:
    stack = []
    mapping = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in mapping.values():
            stack.append(char)
        elif char in mapping.keys():
            if not stack or mapping[char] != stack.pop():
                return False
    return not stack

# Task 2: Run-Length Encoding/Decoding
def rle_encode(s: str) -> str:
    if not s:
        return ''
    
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            result.append(s[i-1])
            if count > 1:
                result.append(str(count))
            count = 1
    
    result.append(s[-1])
    if count > 1:
        result.append(str(count))
    
    return ''.join(result)

def rle_decode(s: str) -> str:
    if not s:
        return ''
    
    result = []
    i = 0
    n = len(s)
    
    while i < n:
        char = s[i]
        i += 1
        
        count_str = ''
        while i < n and s[i].isdigit():
            count_str += s[i]
            i += 1
            
        count = int(count_str) if count_str else 1
        result.append(char * count)
        
    return ''.join(result)

# Task 3: Longest Increasing Subsequence
def lis_length(nums: list[int]) -> int:
    if not nums:
        return 0
        
    tails = []
    for num in nums:
        # Binary search for the first element in tails >= num
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

# Task 4: Evaluate Arithmetic Expression
def eval_expr(expr: str) -> float:
    # Remove whitespace
    expr = expr.replace(' ', '')
    
    def parse_expression(index):
        # Parse term
        value, index = parse_term(index)
        
        while index < len(expr) and expr[index] in ('+', '-'):
            op = expr[index]
            index += 1
            rhs, index = parse_term(index)
            if op == '+':
                value += rhs
            else:
                value -= rhs
        return value, index

    def parse_term(index):
        # Parse factor
        value, index = parse_factor(index)
        
        while index < len(expr) and expr[index] in ('*', '/'):
            op = expr[index]
            index += 1
            rhs, index = parse_factor(index)
            if op == '*':
                value *= rhs
            else:
                value /= rhs
        return value, index

    def parse_factor(index):
        if index >= len(expr):
            raise ValueError('Unexpected end of expression')
            
        if expr[index] == '(':
            value, index = parse_expression(index + 1)
            if index >= len(expr) or expr[index] != ')':
                raise ValueError('Missing closing parenthesis')
            return value, index + 1
        
        if expr[index] == '-':
            value, index = parse_factor(index + 1)
            return -value, index
            
        # Parse number
        start = index
        while index < len(expr) and (expr[index].isdigit() or expr[index] == '.'):
            index += 1
        
        if start == index:
            raise ValueError(f'Expected number at index {index}')
             
        return float(expr[start:index]), index

    result, _ = parse_expression(0)
    return float(result)

# Task 5: Shortest Path in Weighted Grid
def shortest_path(grid: list[list[int]]) -> int:
    if not grid or not grid[0]:
        return 0
        
    rows, cols = len(grid), len(grid[0])
    # Dijkstra
    # (cost, r, c)
    pq = [(grid[0][0], 0, 0)]
    visited = set()
    min_costs = {(0, 0): grid[0][0]}
    
    while pq:
        cost, r, c = heapq.heappop(pq)
        
        if (r, c) == (rows - 1, cols - 1):
            return cost
            
        if (r, c) in visited:
            continue
        visited.add((r, c))
        
        # Directions: up, down, left, right
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            
            if 0 <= nr < rows and 0 <= nc < cols:
                new_cost = cost + grid[nr][nc]
                if new_cost < min_costs.get((nr, nc), float('inf')):
                    min_costs[(nr, nc)] = new_cost
                    heapq.heappush(pq, (new_cost, nr, nc))
                    
    return -1 # Should not reach here given problem constraints
