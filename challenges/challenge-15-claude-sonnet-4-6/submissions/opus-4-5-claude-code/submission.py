"""Fixed versions of all 10 buggy functions."""


def binary_search(arr, target):
    """Return index of target in sorted list, or -1 if not found."""
    left = 0
    right = len(arr) - 1
    while left <= right:  # FIX: was `left < right`, misses single-element case
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
        if ch.lower() in vowels:  # FIX: was `ch in vowels`, missed uppercase
            count += 1
    return count


def rotate_list(lst, k):
    """Rotate list k steps to the right."""
    if not lst:
        return []
    k = k % len(lst)
    return lst[-k:] + lst[:-k]  # FIX: was `lst[k:] + lst[:k]` (rotated left)


def is_prime(n):
    """Return True if n is a prime number."""
    if n <= 1:  # FIX: added guard for n <= 1
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
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # FIX: was `dp[i-1][j-1]`
    return dp[-1][-1]


def valid_parentheses(s):
    """Return True if the brackets in s are balanced."""
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs.values():
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:  # FIX: added return False
                return False
            stack.pop()
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
    result += l1[i:]  # FIX: was `l1[i + 1:]`, skipped current element
    result += l2[j:]
    return result


def fibonacci(n):
    """Return the nth Fibonacci number (0-indexed)."""
    if n <= 1:
        return n  # FIX: was `return 1`, should be `return n` (fib(0)=0, fib(1)=1)
    return fibonacci(n - 1) + fibonacci(n - 2)


def matrix_transpose(matrix):
    """Return the transpose of a 2D matrix."""
    if not matrix:
        return []
    transposed = []
    for i in range(len(matrix[0])):  # FIX: was `len(matrix)`, need columns not rows
        row = []
        for j in range(len(matrix)):
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
    result.append(f"{s[-1]}{count}")  # FIX: was missing final group
    return "".join(result)
