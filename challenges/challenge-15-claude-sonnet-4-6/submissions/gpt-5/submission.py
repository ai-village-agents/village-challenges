from typing import List
def binary_search(arr: List[int], target: int) -> int:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
def count_vowels(s: str) -> int:
    vowels = set("aeiou")
    return sum(1 for ch in s.lower() if ch in vowels)
def rotate_list(lst: List[int], k: int) -> List[int]:
    if not lst:
        return []
    n = len(lst)
    k = k % n
    if k == 0:
        return lst[:]
    return lst[-k:] + lst[:-k]
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True
def longest_common_subsequence(a: str, b: str) -> int:
    # classic DP, O(len(a)*len(b))
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
def valid_parentheses(s: str) -> bool:
    pairs = {')': '(', ']': '[', '}': '{'}
    stack: List[str] = []
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack
def merge_sorted_lists(l1: List[int], l2: List[int]) -> List[int]:
    i = j = 0
    out: List[int] = []
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            out.append(l1[i])
            i += 1
        else:
            out.append(l2[j])
            j += 1
    if i < len(l1):
        out.extend(l1[i:])
    if j < len(l2):
        out.extend(l2[j:])
    return out
def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
def matrix_transpose(matrix: List[List[int]]) -> List[List[int]]:
    if not matrix or not matrix[0]:
        return []
    # Use zip to transpose, then convert to lists
    return [list(row) for row in zip(*matrix)]
def run_length_encode(s: str) -> str:
    if not s:
        return ""
    res: List[str] = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            res.append(f"{s[i-1]}{count}")
            count = 1
    res.append(f"{s[-1]}{count}")
    return "".join(res)
