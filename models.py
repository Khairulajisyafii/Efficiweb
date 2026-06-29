import os
import json
from typing import Dict, List, Optional, Any
from config import DATABASE_DIR

class Project:
    """Kelas model proyek untuk melacak daftar nama dan data palet warna dalam format JSON."""
    def __init__(self, name: str, short_desc: str = "", full_desc: str = "") -> None:
        self.name = name
        self.short_desc = short_desc
        self.full_desc = full_desc
        self.colors: List[Dict[str, str]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "short_desc": self.short_desc, "full_desc": self.full_desc, "colors": self.colors}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        p = cls(data.get("name", "Project Baru"), data.get("short_desc", ""), data.get("full_desc", ""))
        p.colors = data.get("colors", [])
        return p

    def get_path(self) -> str:
        return os.path.join(DATABASE_DIR, f"{self.name.lower().replace(' ', '_')}.json")

    def save(self) -> None:
        with open(self.get_path(), 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, name: str) -> Optional["Project"]:
        path = os.path.join(DATABASE_DIR, f"{name.lower().replace(' ', '_')}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return cls.from_dict(json.load(f))
            except Exception as e: 
                print(f"Error loading project: {e}")
        return None

    def delete(self) -> bool:
        try:
            os.remove(self.get_path())
            return True
        except OSError: 
            return False