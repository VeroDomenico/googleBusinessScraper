from typing import Optional
from datetime import datetime

class Query:
    def __init__(self, search_string: str, status: str, createdTime: Optional[datetime] = None, completedTime: Optional[datetime] = None, numberOfBusinessScraped: int = 0):
        self.id = None  # Will be set by MongoDB
        self.search_string = search_string
        self.status = status
        self.createdTime = createdTime
        self.completedTime = completedTime
        self.numberOfBusinessScraped = numberOfBusinessScraped
        self.task_id = None

    def to_dict(self):
        return vars(self)

class QueryStatus:
    ADDED = "ADDED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
