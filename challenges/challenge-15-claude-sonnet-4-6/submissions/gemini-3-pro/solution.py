def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: return mid
        if arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return -1

def count_vowels(s):
    return sum(1 for ch in s.lower() if ch in "aeiou")

def rotate_list(lst, k):
    if not lst: return []
    k = k % len(lst)
    return lst[-k:] + lst[:-k]

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0: return False
    return True

def longest_common_subsequence(s1, s2):
    dp = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]: dp[i][j] = dp[i - 1][j - 1] + 1
            else: dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]

def valid_parentheses(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs.values(): stack.append(ch)
        elif ch in pairs:
            if stack and stack[-1] == pairs[ch]: stack.pop()
            else: return False
    return not stack

def merge_sorted_lists(l1, l2):
    i = j = 0
    result = []
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]: result.append(l1[i]); i += 1
        else: result.append(l2[j]); j += 1
    result += l1[i:] + l2[j:]
    return result

def fibonacci(n):
    if n <= 1: return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def matrix_transpose(matrix):
    if not matrix: return []
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def run_length_encode(s):
    if not s: return ""
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]: count += 1
        else: result.append(f"{s[i-1]}{count}"); count = 1
    result.append(f"{s[-1]}{count}")
    return "".join(result)
