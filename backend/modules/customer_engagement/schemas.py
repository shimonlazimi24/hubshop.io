from pydantic import BaseModel


class CreateEngagementTaskRequest(BaseModel):
    shop_id: str
    template_id: str
    audience: str


class EngagementTaskResponse(BaseModel):
    task_id: str
    status: str


class EngagementTemplateResponse(BaseModel):
    template_id: str
    name: str
    content: str


class CustomEngagementTaskRequest(BaseModel):
    shop_id: str
    message: str
    audience_ids: list[str] = []
