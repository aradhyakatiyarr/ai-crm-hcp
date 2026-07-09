"""Builds the LangGraph agent: an LLM (Groq gemma2-9b-it) bound to the 5 tools,
looping through a ToolNode until it produces a final natural-language reply.
"""

import json
import re
from datetime import date

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from ..config import settings
from .state import AgentState
from .tools import TOOLS

SYSTEM_PROMPT = """You are the AI Assistant inside an AI-first pharmaceutical CRM, \
embedded in the "Log HCP Interaction" screen. You help a field sales representative \
log and manage interactions with Healthcare Professionals (HCPs) entirely through \
conversation — the rep should never have to fill the form by hand.

You control the form on the left ONLY by calling tools. Never claim you changed a \
field unless you actually called a tool to do it.

Tools:
- log_interaction: extract details of a NEW interaction and fill the form
  (HCP name, type, date, time, attendees, topics, sentiment, materials shared,
  samples distributed, outcomes).
- edit_interaction: change ONLY the specific fields the rep is correcting.
- add_material: add a brochure (is_sample=false) OR a physical drug sample
  (is_sample=true). Samples and brochures are tracked in separate lists.
- schedule_follow_up: set a follow-up date and follow-up actions.
- save_interaction: persist the interaction to the database when asked to save/submit.

Rules:
- Extract entities carefully from natural language.
- Normalize sentiment to exactly one of: positive, neutral, negative.
- Normalize interaction type to one of: Meeting, Call, Email, Conference, Virtual.
- Resolve relative dates ('today', 'tomorrow', 'next Monday') to YYYY-MM-DD using \
today's date given below.
- Only fill a field the rep actually mentioned. Never invent a time, attendee, or \
outcome that wasn't stated (e.g. do NOT set time to 00:00 if no time was given).
- Call add_material ONCE per distinct item. If the rep gives a quantity ("5 sample \
packs"), still call it once — include the quantity in the item name if useful.
- Use log_interaction for a fresh description; use edit_interaction when the rep is \
correcting something already on the form.
- You may call several tools in one turn.
- If the rep just asks a question or for help, answer normally without calling a tool.
- After tools run, reply with a short, friendly confirmation (1-2 sentences) of exactly \
what you changed."""


def _make_llm():
    """LLM is Groq `gemma2-9b-it`, as mandated by the assignment."""
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        temperature=0,
    )


_llm_with_tools = _make_llm().bind_tools(TOOLS)


def agent_node(state: AgentState):
    context = (
        f"\n\nToday's date is {date.today().isoformat()}."
        f"\nThe current form state is:\n{json.dumps(state.get('form', {}), indent=2)}"
    )
    system = SystemMessage(content=SYSTEM_PROMPT + context)
    response = _llm_with_tools.invoke([system] + state["messages"])
    return {"messages": [response]}


_suggest_llm = _make_llm()

_SUGGEST_PROMPT = """You are a pharmaceutical CRM assistant. Given a logged HCP \
interaction as JSON, propose exactly 3 concise, specific next-step follow-up actions a \
field sales rep would realistically take next. Each 4-9 words, action-oriented, and \
grounded in the interaction's HCP, product, and topics — e.g. \
"Schedule follow-up meeting in 2 weeks", "Send Phase III efficacy PDF", \
"Add to advisory board invite list".

Return ONLY a JSON array of exactly 3 short strings. No prose, no markdown."""


def generate_suggestions(form: dict) -> list[str]:
    """Ask the LLM for 3 contextual follow-up suggestions for the current form.
    Best-effort: returns [] if the form is empty or parsing fails."""
    if not form.get("hcpName"):
        return []
    try:
        response = _suggest_llm.invoke(
            [
                SystemMessage(content=_SUGGEST_PROMPT),
                HumanMessage(content=json.dumps(form)),
            ]
        )
        text = response.content if isinstance(response.content, str) else str(response.content)
        match = re.search(r"\[.*\]", text, re.S)
        if not match:
            return []
        items = json.loads(match.group(0))
        return [str(s).strip() for s in items if str(s).strip()][:3]
    except Exception:
        return []


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.set_entry_point("agent")
    # tools_condition routes to "tools" when the LLM emits tool calls, else END.
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    return builder.compile()


graph = build_graph()
