# cache.py
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from config import CACHE_DIR, CACHE_TTL_HOURS

class CacheManager:
    def __init__(self, cache_dir: Path = CACHE_DIR, ttl_hours: int = CACHE_TTL_HOURS):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, prefix: str, identifier: str) -> Path:
        hash_str = hashlib.md5(f"{prefix}:{identifier}".encode()).hexdigest()
        return self.cache_dir / f"{prefix}_{hash_str}.json"
    
    def get(self, prefix: str, identifier: str) -> Optional[Dict]:
        cache_file = self._get_cache_key(prefix, identifier)
        if not cache_file.exists(): return None
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if datetime.now() - datetime.fromisoformat(data.get('_cached_at', '2000-01-01')) > self.ttl:
                cache_file.unlink()
                return None
            return data.get('data')
        except Exception: return None
    
    def set(self, prefix: str, identifier: str, data: Any):
        cache_file = self._get_cache_key(prefix, identifier)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    '_cached_at': datetime.now().isoformat(),
                    'data': data if isinstance(data, dict) else data.model_dump()
                }, f, indent=2)
        except Exception: pass
