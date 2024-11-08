from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class User:
    username: str
    rank: int
    
    def __hash__(self):
        return (hash(self.username) << 8) + hash(self.rank)

class Rank(object):
    GUEST = 0
    USER = 1
    ADMINISTRATOR = 2
    MODERATOR = 3

    ELEMENTS = {0: "guest", 1: "user", 2: "administrator", 3: "moderator"}