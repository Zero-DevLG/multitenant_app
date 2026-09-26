from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    last_name: str
    email: str
    password_hash: str
    status_id: str
    group_id: str
    
    