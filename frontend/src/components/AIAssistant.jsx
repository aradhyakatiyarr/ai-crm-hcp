import { useState, useRef, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { sendMessage } from '../store/chatSlice'

const SUGGESTIONS = [
  'Today I met with Dr. Smith and discussed Prodo-X efficacy. Sentiment was positive and I shared the brochure.',
  'Sorry, the name was actually Dr. John and the sentiment was negative.',
  'Also add 5 sample packs of Prodo-X.',
  'Schedule a follow-up next Monday.',
  'Save this interaction.',
]

export default function AIAssistant() {
  const dispatch = useDispatch()
  const { messages, loading, suggestions, turnCount } = useSelector((s) => s.chat)
  const [input, setInput] = useState('')
  const scrollRef = useRef(null)

  // Progressive reveal: 1 suggestion after the 1st turn, 2 after the 2nd, 3 after the 3rd...
  const revealed = suggestions.slice(0, turnCount)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, loading])

  const submit = () => {
    const text = input.trim()
    if (!text || loading) return
    dispatch(sendMessage(text))
    setInput('')
  }

  return (
    <div className="panel chat-panel">
      <div className="chat-header">
        <div className="chat-title">
          <span className="bot-icon">🤖</span> AI Assistant
        </div>
        <div className="chat-subtitle">Log interaction via chat</div>
      </div>

      <div className="chat-body" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-hint">
            Log interaction details here (e.g., <em>"Met Dr. Smith, discussed Prodo-X efficacy,
            positive sentiment, shared brochure"</em>) or ask for help.
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`msg msg-${m.role}`}>
            <div className="msg-bubble">{m.content}</div>
            {m.actions && m.actions.length > 0 && (
              <div className="msg-actions">
                {m.actions.map((a, j) => (
                  <span className="action-pill" key={j} title={a.detail}>
                    ⚙ {a.tool}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="msg msg-assistant">
            <div className="msg-bubble typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        {revealed.length > 0 && (
          <div className="chat-suggestions">
            <div className="chat-suggestions-title">💡 AI Suggested Follow-ups</div>
            {revealed.map((s, i) => (
              <button
                key={i}
                className="chat-suggestion"
                onClick={() => dispatch(sendMessage(s))}
                disabled={loading}
              >
                + {s}
              </button>
            ))}
          </div>
        )}
      </div>

      {messages.length === 0 && (
        <div className="suggestions">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} className="suggestion" onClick={() => dispatch(sendMessage(s))}>
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="chat-input-row">
        <input
          type="text"
          placeholder="Describe interaction..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          disabled={loading}
        />
        <button className="log-btn" onClick={submit} disabled={loading || !input.trim()}>
          <span className="log-btn-icon">➤</span>
          <span>Log</span>
        </button>
      </div>
    </div>
  )
}
