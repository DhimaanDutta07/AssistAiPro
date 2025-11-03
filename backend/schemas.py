from pydantic import BaseModel
from typing import List, Dict, Any

class LeaveInput(BaseModel):
    employee_id: str | None = None
    days_requested: int = 0
    balance: int = 0

class MeetingInput(BaseModel):
    title: str = "Team Meeting"
    agenda: str = "General"
    participants: List[str] = []
    date: str = "TBD"