from typing import List

from pydantic import BaseModel, Field


class InteractionForm(BaseModel):
    """The state of the 'Log HCP Interaction' form on the left panel."""

    hcpName: str = ""
    interactionType: str = "Meeting"
    date: str = ""
    time: str = ""
    attendees: str = ""
    topicsDiscussed: str = ""
    materialsShared: List[str] = Field(default_factory=list)
    samplesDistributed: List[str] = Field(default_factory=list)
    sentiment: str = ""
    outcomes: str = ""
    followUpDate: str = ""
    followUpActions: str = ""


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    form: InteractionForm
    history: List[ChatMessage] = Field(default_factory=list)


class ToolAction(BaseModel):
    tool: str
    detail: str


class ChatResponse(BaseModel):
    reply: str
    form: InteractionForm
    actions: List[ToolAction] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
