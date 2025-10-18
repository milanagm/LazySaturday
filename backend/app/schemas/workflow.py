from pydantic import BaseModel


class WorkflowCallback(BaseModel):
    workflow_name: str
    status: str
    payload: dict
