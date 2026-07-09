# 🎬 Demo Video Script & Checklist (10–15 min)

Covers all four required points: **task understanding · frontend walkthrough ·
all 5 LangGraph tools · code/architecture explanation.**

## Before you hit record
- [ ] Backend running: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Open http://localhost:5173 and **hard-refresh** (`Cmd/Ctrl + Shift + R`)
- [ ] `/api/health` returns `"key_configured": true`
- [ ] Close noisy tabs/notifications; share the browser + editor windows only
- [ ] Have this script on a second screen / phone

---

## Part 1 — Intro & what you understood (~1.5 min)
> "This is an **AI-first CRM module** for pharmaceutical field sales reps — the
> **Log HCP Interaction** screen. The goal: a rep should log an interaction with a
> Healthcare Professional **by chatting in natural language**, instead of filling a form
> by hand. An **LLM + LangGraph agent** extracts the details and drives the form through
> **tools**. The stack is **React + Redux, FastAPI, LangGraph, and a Groq LLM**, with the
> data persisted to a SQL database."

- [ ] Point out the **split screen**: left = structured form, right = AI Assistant chat.
- [ ] One sentence on the model: *"The brief named `gemma2-9b-it`, but Groq has
      decommissioned it, so I use Groq's `llama-3.3-70b-versatile` — still 100% Groq."*

---

## Part 2 — Frontend walkthrough (~2 min)
- [ ] Show the empty form: HCP Name, Interaction Type, Date, Time, Attendees, Topics,
      Materials Shared, Samples Distributed, Sentiment, Outcomes, Follow-up Actions.
- [ ] Stress the rule: **"I will not type in the form — everything is filled by the AI."**
- [ ] Show the AI Assistant panel + the example hint bubble.

---

## Part 3 — Live demo of all 5 tools (~5–6 min)
Type each prompt into the **AI Assistant** and narrate what fields change on the left.

**1. `log_interaction`** — type:
> `Today I met with Dr. Smith and discussed Prodo-X efficacy. Sentiment was positive and I shared the brochure.`
- [ ] HCP Name → *Dr. Smith*, Date → today, Topics → *Prodo-X efficacy*,
      Sentiment → *Positive*, Materials → *brochure*. Say *"the LLM did entity extraction."*

**2. `edit_interaction`** — type:
> `Sorry, the name was actually Dr. John and the sentiment was negative.`
- [ ] Only Name → *Dr. John* and Sentiment → *Negative* change; **topics & materials stay**.
      Say *"only the named fields update — everything else is preserved."*

**3. `add_material`** (samples path) — type:
> `Also add 5 sample packs of Prodo-X.`
- [ ] Appears under **Samples Distributed** (not Materials) — show the separate list.

**4. `schedule_follow_up`** — type:
> `Schedule a follow-up next Monday to review lab results.`
- [ ] Follow-up Date resolves to the real date; Follow-up Actions → *review lab results*.
      Say *"the LLM resolved the relative date."*

**5. `save_interaction`** — type:
> `Save this interaction.`
- [ ] Assistant confirms *"Saved interaction #1 to the database."*
- [ ] **Prove persistence:** open http://localhost:8000/api/interactions in a new tab and
      show the saved JSON row.

**Bonus — AI Suggested Follow-ups:**
- [ ] Scroll to the bottom of the form — show the 3 AI-generated suggestion links.
- [ ] Click one (e.g. *"Send … PDF"*) and show it feeding back into the assistant.

---

## Part 4 — Code & architecture explanation (~4 min)
Open the editor and walk these files briefly:

- [ ] **`backend/app/agent/graph.py`** — the LangGraph: `agent` node (Groq LLM bound to
      tools) ↔ `ToolNode`, looping via `tools_condition`. Show `generate_suggestions`.
- [ ] **`backend/app/agent/tools.py`** — the 5 `@tool` functions; each reads the form via
      `InjectedState` and returns a `Command` with a **field-level patch**.
- [ ] **`backend/app/agent/state.py`** — `AgentState` + the `form` merge reducer that lets
      multiple tools run in one turn safely.
- [ ] **`backend/app/routers/chat.py`** — `/api/chat`: injects the form, invokes the graph,
      returns reply + updated form + suggestions.
- [ ] **`frontend/src/store/`** — Redux `formSlice` (form state) and `chatSlice`
      (`sendMessage` thunk → POST `/api/chat` → `setForm`).
- [ ] **`frontend/src/components/`** — `LogInteractionForm` (left) and `AIAssistant` (right).
- [ ] One line on the DB: SQLAlchemy `Interaction` model, SQLite by default, Postgres/MySQL
      via one env var.

---

## Closing (~30 sec)
> "So the LangGraph agent orchestrates five tools driven by a Groq LLM to turn plain
> English into a fully structured, saved HCP interaction — plus AI-suggested follow-ups.
> Thanks for watching."

## Recording tips
- Speak while the field visibly updates — the on-screen change is the proof.
- If a tool call is ever flaky, just resend the prompt; keep the take moving.
- Keep it 10–15 min; Part 3 (the tools demo) is the most important — don't rush it.
