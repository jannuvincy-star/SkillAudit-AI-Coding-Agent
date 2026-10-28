"""Small calculator module. Intentional bug: divide by zero crashes inconsistently."""

def add(a, b):
    return a + b

def average(values):
    if not values:
        raise ValueError("Cannot compute average of empty list")
    return sum(values) / len(values)

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
