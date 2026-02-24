from src.app import add

def test_add():
    assert add(2, 3) == 5  # Will fail because 2*3=6
