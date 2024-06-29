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
        self.redis_task_id = None

    def to_dict(self):
        return {
            "_id": str(self.id) if self.id else None,
            "search_string": self.search_string,
            "status": self.status,
            "createdTime": self.createdTime,
            "completedTime": self.completedTime,
            "numberOfBusinessScraped": self.numberOfBusinessScraped,
            "redis_task_id": self.redis_task_id
        }

class QueryStatus:
    ADDED = "ADDED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
