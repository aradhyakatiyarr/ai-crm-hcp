# AI-First CRM — HCP Log Interaction Screen

An AI-first CRM module for pharmaceutical field sales reps. The rep logs interactions
with Healthcare Professionals (HCPs) **entirely by chatting** with an AI assistant — the
assistant extracts entities from natural language and drives the structured form on the
left through a **LangGraph agent** with **5 tools**, powered by a **Groq LLM**.

> Split screen: **left** = structured *Log HCP Interaction* form · **right** = *AI
> Assistant* chat. You never fill the form by hand — you tell the assistant, and its tools
> fill/edit the fields. After each turn the agent also proposes contextual
> **AI Suggested Follow-ups**.

---

## Tech stack (as required by the assignment)

| Layer            | Technology                                                     |
| ---------------- | -------------------------------------------------------------- |
| Frontend         | React + Redux Toolkit (Vite)                                   |
| Backend          | Python + FastAPI                                               |
| AI agent         | **LangGraph** (StateGraph + ToolNode)                          |
| LLM              | **Groq** via `langchain-groq` — model set by `MODEL_NAME`      |
| Database         | Postgres / MySQL / SQLite (SQLAlchemy)                         |
| Font             | Google **Inter**                                               |

> **Note on the model:** the assignment names `gemma2-9b-it`, but Groq has since
> **decommissioned** that model (its API now returns `400 model_decommissioned`; see
> https://console.groq.com/docs/deprecations). The assignment's own named alternative,
> `llama-3.3-70b-versatile`, works well but shares a low free-tier daily token quota
> across the whole account — heavy iteration during development can exhaust it. This
> repo defaults `MODEL_NAME` to **`openai/gpt-oss-120b`** (also served by Groq), which
> gave the most reliable tool-calling in testing. Any Groq model can be swapped in via
> `MODEL_NAME` in `.env` — everything still runs on Groq.

---

## The 5 LangGraph tools

The LangGraph agent is an LLM bound to the tools below. On each turn the current form is
injected into the graph state; the LLM decides which tool(s) to call and with what
arguments (entity extraction). Each tool returns a **field-level patch** via a `Command`;
a shallow-merge reducer applies it to the form, so the LLM can safely call several tools
in one turn. The loop continues until the LLM returns a plain-text confirmation.

| # | Tool                 | What it does                                                                                     |
| - | -------------------- | ------------------------------------------------------------------------------------------------ |
| 1 | `log_interaction`    | **(mandatory)** Extracts HCP name, type, date, time, attendees, topics, sentiment, materials, samples & outcomes from free text and fills the form. |
| 2 | `edit_interaction`   | **(mandatory)** Updates only the specific fields the rep corrects, leaving the rest unchanged.   |
| 3 | `add_material`       | Adds a brochure → *Materials Shared*, or a physical sample → *Samples Distributed* (`is_sample`). |
| 4 | `schedule_follow_up` | Sets the follow-up date + actions (resolves relative dates like "next Monday").                  |
| 5 | `save_interaction`   | Persists the current interaction to the database.                                                |

**Bonus AI capability — AI Suggested Follow-ups:** after every turn the backend makes a
lightweight Groq call (`generate_suggestions`) to propose 3 contextual next steps (e.g.
*"Send OncoBoost Phase III PDF"*). They render as clickable links under the form; clicking
one feeds it back to the assistant, which then runs the relevant tool.

### Try these prompts (in order)

1. `Today I met with Dr. Smith and discussed Prodo-X efficacy. Sentiment was positive and I shared the brochure.` → `log_interaction`
2. `Sorry, the name was actually Dr. John and the sentiment was negative.` → `edit_interaction`
3. `Also add 5 sample packs of Prodo-X.` → `add_material` (→ Samples Distributed)
4. `Schedule a follow-up next Monday to review lab results.` → `schedule_follow_up`
5. `Save this interaction.` → `save_interaction`

---

## Form fields (left panel)

`HCP Name` · `Interaction Type` · `Date` · `Time` · `Attendees` · `Topics Discussed` ·
`Materials Shared` · `Samples Distributed` · `Observed/Inferred HCP Sentiment`
(positive / neutral / negative) · `Outcomes` · `Follow-up Date` · `Follow-up Actions` ·
plus the dynamic `AI Suggested Follow-ups` list.

---

## Project structure

```
ai-crm-hcp/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + CORS + routers
│   │   ├── config.py          # env settings (Groq key, model, DB URL)
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # HCP, Interaction ORM models
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── agent/
│   │   │   ├── state.py        # LangGraph AgentState + form merge reducer
│   │   │   ├── tools.py        # the 5 tools
│   │   │   └── graph.py        # LLM + ToolNode graph + generate_suggestions
│   │   └── routers/
│   │       ├── chat.py         # POST /api/chat  (runs the agent)
│   │       └── interactions.py # GET /api/interactions, /api/hcps
│   ├── seed.py                 # seed sample HCPs
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── store/              # Redux: formSlice, chatSlice (incl. suggestions)
    │   ├── api/client.js
    │   └── components/         # LogInteractionForm, AIAssistant
    └── package.json
```

---

## Setup & run

### 0. Get a free Groq API key (required)
Sign up at **https://console.groq.com** → API Keys → create key. No credit card needed.

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your key:  GROQ_API_KEY=gsk_...
# MODEL_NAME defaults to llama-3.3-70b-versatile

python seed.py                                        # optional: sample HCPs
uvicorn app.main:app --reload --port 8000
```

Backend runs at http://localhost:8000 (health check: `/api/health`).

**Database:** defaults to SQLite (zero setup). To use Postgres or MySQL, just change
`DATABASE_URL` in `.env`:
- Postgres: `postgresql+psycopg2://user:pass@localhost:5432/hcp_crm`
- MySQL: `mysql+pymysql://user:pass@localhost:3306/hcp_crm` (also `pip install pymysql`)

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` → `http://localhost:8000`.

---

## How it works (data flow)

```
User types in chat
      │
      ▼
Redux thunk sends { message, current form, history } → POST /api/chat
      │
      ▼
FastAPI builds LangGraph state { messages, form } and invokes the graph
      │
      ▼
agent (Groq LLM) ──has tool calls?──► ToolNode runs tool(s)
      ▲                                    │  (each returns a Command with a
      └────────────────────────────────────  field-level form patch + messages)
      │
      ▼ (no more tool calls)
reply + updated form + 3 AI follow-up suggestions returned to frontend
      │
      ▼
Redux setForm(updated) → left panel re-renders with AI-filled fields
                       → AI Suggested Follow-ups render under the form
```

---

## Notes

- **Groq is the only LLM provider used**, as mandated by the assignment (see the model
  note above re: the `gemma2-9b-it` → `llama-3.3-70b-versatile` substitution).
- The form fields remain editable so the screen supports "either a structured form or a
  conversational chat interface," but the intended/demoed path is fully AI-driven.
- Each tool returns only the fields it changed (a patch), so the LLM can call multiple
  tools in a single turn without them clobbering each other's updates.
