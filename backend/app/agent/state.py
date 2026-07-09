import operator
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


def _merge_form(current: dict, update: dict) -> dict:
    """Reducer for `form`. Tools return a PATCH containing only the fields
    they changed (see agent/tools.py), so a plain shallow merge is safe even
    when the LLM calls several tools in the same step — each patch only
    touches its own keys and can't clobber a sibling tool's changes."""
    return {**current, **update}


class AgentState(TypedDict):
    """Shared state that flows through the LangGraph.

    - messages: the running conversation (LLM + tool messages)
    - form:     the live 'Log HCP Interaction' form the tools mutate
    - actions:  a log of tool actions, surfaced to the UI as feedback
    """

    messages: Annotated[list, add_messages]
    form: Annotated[dict, _merge_form]
    actions: Annotated[list, operator.add]
