import time
import hashlib

class ResilientStore:
    def __init__(self, backend):
        self.backend = backend
        self.max_retries = 10
        self.base_delay = 0.01

    def _compute_checksum(self, data: str) -> str:
        return hashlib.md5(data.encode()).hexdigest()

    def _pack(self, data: str) -> str:
        """Pack data with checksum."""
        checksum = self._compute_checksum(data)
        return f"{checksum}:{data}"

    def _unpack(self, packed_data: str) -> str | None:
        """Unpack data and verify checksum."""
        if not packed_data or ":" not in packed_data:
            return None
            
        checksum, data = packed_data.split(":", 1)
        if self._compute_checksum(data) != checksum:
            return None # Corrupted
            
        return data

    def put(self, key: str, value: str) -> bool:
        packed = self._pack(value)
        
        for attempt in range(self.max_retries):
            try:
                self.backend.save(key, packed)
                # Verify write
                loaded = self.backend.load(key)
                if loaded == packed:
                    return True
            except Exception:
                pass
                
            time.sleep(self.base_delay * (2 ** attempt))
            
        return False

    def get(self, key: str) -> str | None:
        for attempt in range(self.max_retries):
            try:
                packed = self.backend.load(key)
                if packed is None:
                    return None
                    
                data = self._unpack(packed)
                if data is not None:
                    return data
                    
            except Exception:
                pass
                
            time.sleep(self.base_delay * (2 ** attempt))
            
        return None

    def delete(self, key: str):
        for attempt in range(self.max_retries):
            try:
                self.backend.delete(key)
                return True
            except Exception:
                time.sleep(self.base_delay * (2 ** attempt))
        return False
