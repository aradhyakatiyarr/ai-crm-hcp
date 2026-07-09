"""The five LangGraph tools that drive the Log Interaction form.

Each tool receives the live form via `InjectedState`, mutates it, and returns a
`Command` that updates the graph state (form + actions + a ToolMessage). The LLM
(Groq gemma2-9b-it) decides which tool(s) to call and extracts the arguments.
"""

from datetime import date as date_cls
from typing import Annotated, List, Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from ..database import SessionLocal
from .. import models

VALID_SENTIMENTS = {"positive", "neutral", "negative"}
VALID_TYPES = {"Meeting", "Call", "Email", "Conference", "Virtual"}


def _append_unique(existing: list, additions: list) -> list:
    """Append items to a list copy, skipping blanks and duplicates."""
    result = list(existing)
    for item in additions:
        if item and item not in result:
            result.append(item)
    return result


def _non_empty(updates: dict) -> dict:
    """Keep only the fields that actually carry a new value.

    Tools return a PATCH (just the changed fields), never a full form
    snapshot — the graph's `form` reducer shallow-merges patches onto the
    current form. This is what makes it safe for the LLM to call multiple
    tools in the same turn (e.g. edit + add_material together): each tool
    only touches its own fields and can't clobber a sibling tool's changes.
    """
    return {k: v for k, v in updates.items() if v is not None and v != ""}


def _result(patch: dict, tool_name: str, detail: str, tool_call_id: str) -> Command:
    return Command(
        update={
            "form": patch,
            "actions": [{"tool": tool_name, "detail": detail}],
            "messages": [ToolMessage(content=detail, tool_call_id=tool_call_id)],
        }
    )


# --------------------------------------------------------------------------- #
# Tool 1 (mandatory): LOG INTERACTION
# --------------------------------------------------------------------------- #
@tool
def log_interaction(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    sentiment: Optional[str] = None,
    materials_shared: Optional[List[str]] = None,
    samples_distributed: Optional[List[str]] = None,
    outcomes: Optional[str] = None,
    state: Annotated[dict, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Extract the details of a NEW HCP interaction from the rep's message and fill
    the Log Interaction form. Use this the first time the rep describes a visit.

    Pass every field you can extract:
    - sentiment MUST be one of: positive, neutral, negative
    - interaction_type MUST be one of: Meeting, Call, Email, Conference, Virtual
    - date as YYYY-MM-DD, time as 24h HH:MM. Resolve 'today' to today's date.
    - materials_shared: brochures / printed leave-behinds mentioned.
    - samples_distributed: physical drug samples handed over.
    - outcomes: key outcomes or agreements from the interaction.
    """
    current_form = state["form"]

    norm_sentiment = None
    if sentiment and sentiment.lower() in VALID_SENTIMENTS:
        norm_sentiment = sentiment.lower()

    norm_type = interaction_type if interaction_type in VALID_TYPES else None

    patch = _non_empty(
        {
            "hcpName": hcp_name,
            "interactionType": norm_type,
            # default to today only if no date extracted and form has none yet
            "date": date or (date_cls.today().isoformat() if not current_form.get("date") else None),
            "time": time,
            "attendees": attendees,
            "topicsDiscussed": topics_discussed,
            "sentiment": norm_sentiment,
            "outcomes": outcomes,
        }
    )

    if materials_shared:
        patch["materialsShared"] = _append_unique(
            current_form.get("materialsShared", []), materials_shared
        )
    if samples_distributed:
        patch["samplesDistributed"] = _append_unique(
            current_form.get("samplesDistributed", []), samples_distributed
        )

    detail = f"Logged interaction with {patch.get('hcpName') or current_form.get('hcpName') or 'the HCP'}."
    return _result(patch, "log_interaction", detail, tool_call_id)


# --------------------------------------------------------------------------- #
# Tool 2 (mandatory): EDIT INTERACTION
# --------------------------------------------------------------------------- #
@tool
def edit_interaction(
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    state: Annotated[dict, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Correct or change SPECIFIC fields on the existing form, leaving everything
    else untouched. Use when the rep fixes previously entered info, e.g.
    "sorry, the name was actually Dr. John and the sentiment was negative".
    Only pass the fields that should change.
    """
    norm_sentiment = None
    if sentiment and sentiment.lower() in VALID_SENTIMENTS:
        norm_sentiment = sentiment.lower()
    norm_type = interaction_type if interaction_type in VALID_TYPES else None

    patch = _non_empty(
        {
            "hcpName": hcp_name,
            "interactionType": norm_type,
            "date": date,
            "time": time,
            "attendees": attendees,
            "topicsDiscussed": topics_discussed,
            "sentiment": norm_sentiment,
            "outcomes": outcomes,
        }
    )

    detail = "Updated " + (", ".join(patch.keys()) if patch else "the form") + "."
    return _result(patch, "edit_interaction", detail, tool_call_id)


# --------------------------------------------------------------------------- #
# Tool 3: ADD MATERIAL / SAMPLE
# --------------------------------------------------------------------------- #
@tool
def add_material(
    material: str,
    is_sample: bool = False,
    state: Annotated[dict, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Add an item to the interaction. Brochures/printed leave-behinds go to
    'Materials Shared'; physical drug samples go to 'Samples Distributed'.
    Set is_sample=True for a physical sample, False for a brochure/material.
    """
    if is_sample:
        updated = _append_unique(state["form"].get("samplesDistributed", []), [material])
        detail = f"Added '{material}' to samples distributed."
        return _result({"samplesDistributed": updated}, "add_material", detail, tool_call_id)

    updated = _append_unique(state["form"].get("materialsShared", []), [material])
    detail = f"Added '{material}' to materials shared."
    return _result({"materialsShared": updated}, "add_material", detail, tool_call_id)


# --------------------------------------------------------------------------- #
# Tool 4: SCHEDULE FOLLOW-UP
# --------------------------------------------------------------------------- #
@tool
def schedule_follow_up(
    follow_up_date: str,
    notes: str = "",
    state: Annotated[dict, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Schedule a follow-up visit/task for this HCP. follow_up_date as YYYY-MM-DD.
    Resolve relative dates ('next Monday', 'in two weeks') using today's date.
    """
    patch = {"followUpDate": follow_up_date}
    if notes:
        patch["followUpActions"] = notes

    detail = f"Follow-up scheduled for {follow_up_date}."
    return _result(patch, "schedule_follow_up", detail, tool_call_id)


# --------------------------------------------------------------------------- #
# Tool 5: SAVE INTERACTION (persist to DB)
# --------------------------------------------------------------------------- #
@tool
def save_interaction(
    state: Annotated[dict, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Persist the current interaction form to the database. Call when the rep asks
    to save / submit / log the interaction permanently.
    """
    form = dict(state["form"])
    db = SessionLocal()
    try:
        record = models.Interaction(
            hcp_name=form.get("hcpName", ""),
            interaction_type=form.get("interactionType", ""),
            date=form.get("date", ""),
            time=form.get("time", ""),
            attendees=form.get("attendees", ""),
            topics_discussed=form.get("topicsDiscussed", ""),
            materials_shared=form.get("materialsShared", []),
            samples_distributed=form.get("samplesDistributed", []),
            sentiment=form.get("sentiment", ""),
            outcomes=form.get("outcomes", ""),
            follow_up_date=form.get("followUpDate", ""),
            follow_up_actions=form.get("followUpActions", ""),
            summary=(
                f"{form.get('interactionType', 'Meeting')} with "
                f"{form.get('hcpName', 'HCP')}: {form.get('topicsDiscussed', '')}"
            ),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        new_id = record.id
    finally:
        db.close()

    detail = f"Saved interaction #{new_id} to the database."
    return _result({}, "save_interaction", detail, tool_call_id)


TOOLS = [
    log_interaction,
    edit_interaction,
    add_material,
    schedule_follow_up,
    save_interaction,
]
