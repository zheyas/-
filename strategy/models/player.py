from typing import Optional, Any

class Player:
    def __init__(self, id: int, name: str, portrait: Optional[Any] = None):
        self.id = id
        self.name = name
        self.portrait = portrait

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
