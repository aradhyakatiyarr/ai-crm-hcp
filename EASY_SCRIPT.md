# 🎤 Easy Script — Simple Words

## 1. Intro
"Hi, this is my AI CRM project for sales reps. It has a Log Interaction screen.
The rep just talks to an AI assistant, and it fills the form for them. I used
React, FastAPI, LangGraph, and Groq's LLM to build this.

One small thing — the task asked for a model called gemma2-9b-it. But Groq
stopped supporting that model. So I used another Groq model instead, called
llama-3.3-70b-versatile. It's still Groq, just a different model."

## 2. Show the screen
"On the left, you can see the form. On the right, there's the AI Assistant.
I will only type on the right side. I will not touch the form myself. The AI
will fill it for me."

## 3. Show the 5 tools

**Type:** `Today I met with Dr. Smith and discussed Prodo-X efficacy. Sentiment was positive.`

"This is the first tool — Log Interaction. I just typed one sentence."
*(wait for form to fill)*
"See, it filled the name, date, topic, and sentiment by itself."

**Type:** `Sorry, the name was actually Dr. John and the sentiment was negative.`

"Now the second tool — Edit Interaction. I'm fixing a mistake."
*(wait)*
"It only changed the name and sentiment. Everything else stayed the same."

**Type:** `I shared the brochure and left 5 sample packs of Prodo-X.`

"Third tool — Add Material."
*(wait)*
"The brochure went into Materials, and the samples went into a different box for
Samples. It knows the difference."

**Type:** `Schedule a follow-up next Monday to review lab results.`

"Fourth tool — Schedule Follow-up."
*(wait)*
"It turned 'next Monday' into a real date, and added the note."

**Type:** `Save this interaction.`

"Fifth tool — Save Interaction. This saves everything to the database."
*(wait, then open new tab: localhost:8000/api/interactions)*
"And here, I'm opening the database directly. You can see the data really got
saved, not just shown on screen."

## 4. Show the code
"Now let me show the code quickly.

In the backend, I have a file called graph.py. This is where the AI agent lives.
It has the Groq model connected to all 5 tools.

Another file, tools.py, has the actual 5 tools. Each tool only changes the
fields it needs to change, so nothing gets overwritten by mistake.

There's also a file called chat.py. This is the API that connects the frontend
to the AI agent.

On the frontend side, I used Redux to manage the form data and the chat
messages. There are two main parts — the form component and the chat
component.

For the database, I used SQLAlchemy. It uses SQLite by default, but it can also
work with Postgres or MySQL."

## 5. Closing
"So that's my project. An AI agent with 5 tools, using Groq, that fills a form
just from talking to it, and saves everything properly. Thank you for watching."
