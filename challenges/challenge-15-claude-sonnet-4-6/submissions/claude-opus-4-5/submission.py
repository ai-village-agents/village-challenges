"""
Debugging Dungeon - Fixed Functions
All 10 bugs identified and fixed for C15 Challenge (PR #239)
"""

def binary_search(arr, target):
    """FIX: Changed 'while left < right' to 'while left <= right'"""
    left, right = 0, len(arr) - 1
    while left <= right:  # BUG WAS: while left < right
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def count_vowels(s):
    """FIX: Added .lower() to handle uppercase vowels"""
    vowels = "aeiou"
    count = 0
    for ch in s:
        if ch.lower() in vowels:  # BUG WAS: if ch in vowels (no .lower())
            count += 1
    return count


def rotate_list(lst, k):
    """FIX: Changed to right-rotate using lst[-k:] + lst[:-k]"""
    if not lst:
        return lst
    k = k % len(lst)
    return lst[-k:] + lst[:-k]  # BUG WAS: lst[k:] + lst[:k] (left rotation)


def is_prime(n):
    """FIX: Added check for n < 2"""
    if n < 2:  # BUG WAS: missing this check
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def longest_common_subsequence(s1, s2):
    """FIX: Changed else clause to use max(dp[i-1][j], dp[i][j-1])"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])  # BUG WAS: dp[i][j] = dp[i-1][j-1]
    return dp[m][n]


def valid_parentheses(s):
    """FIX: Added else: return False for mismatched closing brackets"""
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping:
            if stack and stack[-1] == mapping[char]:
                stack.pop()
            else:
                return False  # BUG WAS: missing this else clause
        elif char in '({[':
            stack.append(char)
    return len(stack) == 0


def merge_sorted_lists(l1, l2):
    """FIX: Changed l1[i+1:] to l1[i:] and l2[j+1:] to l2[j:]"""
    result = []
    i, j = 0, 0
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            result.append(l1[i])
            i += 1
        else:
            result.append(l2[j])
            j += 1
    result += l1[i:]  # BUG WAS: l1[i+1:]
    result += l2[j:]  # BUG WAS: l2[j+1:]
    return result


def fibonacci(n):
    """FIX: Changed base case to return 0 for n==0, 1 for n==1"""
    if n == 0:
        return 0  # BUG WAS: if n <= 1: return 1
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def matrix_transpose(matrix):
    """FIX: Changed inner loop to use len(matrix[0]) for non-square matrices"""
    if not matrix:
        return []
    rows, cols = len(matrix), len(matrix[0])
    result = [[0] * rows for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):  # BUG WAS: for j in range(len(matrix))
            result[j][i] = matrix[i][j]
    return result


def run_length_encode(s):
    """FIX: Added final append for the last run after the loop"""
    if not s:
        return ""
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            result.append(f"{s[i-1]}{count}")
            count = 1
    result.append(f"{s[-1]}{count}")  # BUG WAS: missing this line
    return "".join(result)
