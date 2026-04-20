#!/usr/bin/env python3
import unittest
import random
import time
import sys
import os
import hashlib
import importlib.util

# ==========================================
# CHAOS BACKEND IMPLEMENTATION
# ==========================================

class ChaosError(Exception):
    """Base class for chaos errors."""
    pass

class ConnectionError(ChaosError):
    pass

class TimeoutError(ChaosError):
    pass

class DiskError(ChaosError):
    pass

class ChaosBackend:
    """
    An intentionally unreliable storage backend.
    Stores data in memory but simulates network/disk failures.
    """
    def __init__(self, failure_rate=0.0):
        self._storage = {}
        self.failure_rate = failure_rate
        self.chaos_enabled = True

    def _simulate_chaos(self, op_type):
        """Simulate random failures."""
        if not self.chaos_enabled:
            return

        r = random.random()
        
        # 15% chance of latency spike (0.1s to 0.5s for test speed)
        if r < 0.15:
            time.sleep(random.uniform(0.1, 0.5))

        # Check failure rate
        if r < self.failure_rate:
            error_type = random.choice([ConnectionError, TimeoutError, DiskError])
            raise error_type(f"Simulated {op_type} failure")

    def save(self, key: str, data: str):
        """Save data to storage."""
        self._simulate_chaos("save")
        
        # 10% chance of data corruption on save if failure rate is high
        if self.chaos_enabled and self.failure_rate > 0.1 and random.random() < 0.1:
            data = data[::-1] # Corrupt by reversing
            
        self._storage[key] = data

    def load(self, key: str) -> str:
        """Load data from storage."""
        self._simulate_chaos("load")
        
        if key not in self._storage:
            return None
            
        return self._storage[key]

    def delete(self, key: str):
        """Delete data from storage."""
        self._simulate_chaos("delete")
        if key in self._storage:
            del self._storage[key]

# ==========================================
# TEST SUITE
# ==========================================

class TestResilientStore(unittest.TestCase):
    def setUp(self):
        # Load submission dynamically
        submission_path = os.environ.get("SUBMISSION_PATH", "submission.py")
        if not os.path.exists(submission_path):
            self.fail(f"Submission file not found: {submission_path}")
            
        spec = importlib.util.spec_from_file_location("submission", submission_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, "ResilientStore"):
            self.fail("ResilientStore class not found in submission")
            
        self.ResilientStore = module.ResilientStore

    def test_01_basic_functionality(self):
        """Test basic put/get/delete with 0% failure rate. (30 pts)"""
        backend = ChaosBackend(failure_rate=0.0)
        store = self.ResilientStore(backend)
        
        # Put
        store.put("k1", "value1")
        
        # Get
        val = store.get("k1")
        self.assertEqual(val, "value1", f"Get returned wrong value: {val}")
        
        # Update
        store.put("k1", "value2")
        self.assertEqual(store.get("k1"), "value2")
        
        # Delete
        if hasattr(store, "delete"):
            store.delete("k1")
            self.assertIsNone(store.get("k1"))

    def test_02_resilience(self):
        """Test resilience against 30% failure rate. (40 pts)"""
        backend = ChaosBackend(failure_rate=0.3)
        store = self.ResilientStore(backend)
        
        success_count = 0
        total_ops = 50
        
        for i in range(total_ops):
            key = f"rk_{i}"
            val = f"rv_{i}"
            
            # Should eventually succeed due to retries
            if store.put(key, val):
                # Verify read
                retrieved = store.get(key)
                if retrieved == val:
                    success_count += 1
        
        success_rate = success_count / total_ops
        self.assertGreater(success_rate, 0.90, f"Success rate too low: {success_rate:.2%}")

    def test_03_data_integrity(self):
        """Test data integrity (corruption detection). (30 pts)"""
        backend = ChaosBackend(failure_rate=0.2)
        store = self.ResilientStore(backend)
        
        # Manually inject corruption
        store.put("integrity_key", "important_data")
        backend._storage["integrity_key"] = "corrupted_data_garbage"
        
        result = store.get("integrity_key")
        self.assertNotEqual(result, "corrupted_data_garbage", "Store returned corrupted data!")
        self.assertTrue(result is None or result == "important_data", 
                       "Store should return None (if unrecoverable) or original data")

def grade_submission(submission_path):
    os.environ["SUBMISSION_PATH"] = submission_path
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResilientStore)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    score = 0
    
    # Identify failed tests
    failed_tests = set()
    for test, _ in result.failures + result.errors:
        failed_tests.add(test._testMethodName)
        
    # Calculate score
    if "test_01_basic_functionality" not in failed_tests:
        score += 30
    if "test_02_resilience" not in failed_tests:
        score += 40
    if "test_03_data_integrity" not in failed_tests:
        score += 30
        
    return score, result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grade.py <submission_path>")
        sys.exit(1)
        
    path = sys.argv[1]
    print(f"Grading {path}...")
    
    try:
        score, result = grade_submission(path)
        print(f"Total Score: {score}/100")
        if not result.wasSuccessful():
            print("\nFailures:")
            for failed_test, traceback in result.failures + result.errors:
                print(f"- {failed_test._testMethodName}: {traceback.splitlines()[-1]}")
    except Exception as e:
        print(f"Grading Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
