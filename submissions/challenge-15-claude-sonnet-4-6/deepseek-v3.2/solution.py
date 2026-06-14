"""Collection of intentionally buggy functions for grading exercises."""


def binary_search(arr, target):
    """Return index of target in sorted list, or -1 if not found."""
    left = 0
    right = len(arr) - 1
    while left <= right:  # FIXED: <= to check the final single element
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def count_vowels(s):
    """Count vowels (a, e, i, o, u) case-insensitively in a string."""
    vowels = "aeiou"
    count = 0
    for ch in s:
        if ch.lower() in vowels:  # FIXED: convert to lowercase
            count += 1
    return count


def rotate_list(lst, k):
    """Rotate list k steps to the right."""
    if not lst:
        return []
    k = k % len(lst)
    return lst[-k:] + lst[:-k]  # FIXED: right-rotating


def is_prime(n):
    """Return True if n is a prime number."""
    if n < 2:  # FIXED: handle n < 2
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def longest_common_subsequence(s1, s2):
    """Return length of the longest common subsequence between s1 and s2."""
    dp = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # FIXED: max of left/up
    return dp[-1][-1]


def valid_parentheses(s):
    """Return True if the brackets in s are balanced."""
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs.values():
            stack.append(ch)
        elif ch in pairs:
            if stack and stack[-1] == pairs[ch]:
                stack.pop()
            else:
                return False  # FIXED: return False for mismatched closing bracket
    return not stack


def merge_sorted_lists(l1, l2):
    """Merge two sorted lists into a single sorted list."""
    i = 0
    j = 0
    result = []
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            result.append(l1[i])
            i += 1
        else:
            result.append(l2[j])
            j += 1
    result += l1[i:]  # FIXED: include all remaining elements from i
    result += l2[j:]
    return result


def fibonacci(n):
    """Return the nth Fibonacci number (0-indexed)."""
    if n == 0:
        return 0  # FIXED: fib(0) = 0
    if n == 1:
        return 1  # FIXED: fib(1) = 1
    return fibonacci(n - 1) + fibonacci(n - 2)


def matrix_transpose(matrix):
    """Return the transpose of a 2D matrix."""
    if not matrix:
        return []
    transposed = []
    for i in range(len(matrix[0])):  # FIXED: iterate over columns
        row = []
        for j in range(len(matrix)):  # iterate over rows
            row.append(matrix[j][i])
        transposed.append(row)
    return transposed


def run_length_encode(s):
    """Encode a string using run-length encoding (e.g., 'aaabb' -> 'a3b2')."""
    if not s:
        return ""
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(f"{s[i-1]}{count}")
            count = 1
    # FIXED: append final run
    result.append(f"{s[-1]}{count}")
    return "".join(result)
