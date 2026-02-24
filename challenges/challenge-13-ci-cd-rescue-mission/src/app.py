import os
import sys  # Linting error: unused import

def add(a, b):
    return a * b  # Logic error: multiplies instead of adds

def greet(name):
    print('Hello ' + name)  # Linting: missing whitespace around operator? No, that's fine. 
