from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage

from ..agent.graph import generate_suggestions, graph
from ..config import settings
from ..schemas import ChatRequest, ChatResponse, InteractionForm, ToolAction

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Run one turn of the LangGraph agent. The current form is injected into the
    graph state; tools mutate it; the updated form + assistant reply come back."""
    history = []
    for m in req.history:
        if m.role == "user":
            history.append(HumanMessage(content=m.content))
        else:
            history.append(AIMessage(content=m.content))

    initial_state = {
        "messages": history + [HumanMessage(content=req.message)],
        "form": req.form.model_dump(),
        "actions": [],
    }

    try:
        result = graph.invoke(initial_state)
    except Exception as exc:  # surface LLM/config errors clearly to the UI
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc

    # The final natural-language reply is the last AIMessage with text content.
    reply = ""
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and isinstance(msg.content, str) and msg.content.strip():
            reply = msg.content.strip()
            break
    if not reply:
        reply = "Done — I've updated the form on the left."

    updated_form = result["form"]
    suggestions = generate_suggestions(updated_form) if settings.enable_suggestions else []
    return ChatResponse(
        reply=reply,
        form=InteractionForm(**updated_form),
        actions=[ToolAction(**a) for a in result.get("actions", [])],
        suggestions=suggestions,
    )
