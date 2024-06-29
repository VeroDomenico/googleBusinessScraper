class Query:
    """
        Query Class that represents 
    """
    def __init__(self, 
                 search_string: str, 
                 status: str = "ADDED", 
                 created_time: Optional[datetime] = None, 
                 completed_time: Optional[datetime] = None, 
                 number_of_business_scraped: int = 0):
        self.redis_task_id = None
        self.search_string = search_string
        self.status = status
        self.created_time = created_time #if created_time else datetime.utcnow()
        self.completed_time = completed_time
        self.number_of_business_scraped = number_of_business_scraped

    def to_dict(self):
        return vars(self)
    
class Job:
    def __init__(self,) -> None:
        self.redis_task_id = None
        self.gcardList = []
