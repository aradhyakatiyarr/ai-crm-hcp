import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { updateField, removeListItem, addListItem } from '../store/formSlice'
import { sendMessage } from '../store/chatSlice'

const INTERACTION_TYPES = ['Meeting', 'Call', 'Email', 'Conference', 'Virtual']
const SENTIMENTS = [
  { key: 'positive', label: 'Positive', emoji: '🙂' },
  { key: 'neutral', label: 'Neutral', emoji: '😐' },
  { key: 'negative', label: 'Negative', emoji: '🙁' },
]

// A bordered box: title + Search/Add on one row, chips or empty text below.
function ItemBox({ list, title, items, emptyText, addLabel }) {
  const dispatch = useDispatch()
  const [showAdd, setShowAdd] = useState(false)
  const [value, setValue] = useState('')

  const add = () => {
    const v = value.trim()
    if (v) {
      dispatch(addListItem({ list, value: v }))
      setValue('')
      setShowAdd(false)
    }
  }

  return (
    <div className="item-box">
      <div className="item-box-head">
        <span className="item-box-title">{title}</span>
        <button className="search-add" type="button" onClick={() => setShowAdd((v) => !v)}>
          {addLabel}
        </button>
      </div>
      {items.length === 0 ? (
        <div className="item-empty">{emptyText}</div>
      ) : (
        <div className="chips">
          {items.map((m, i) => (
            <span className="item-chip" key={`${m}-${i}`}>
              {m}
              <button
                type="button"
                className="chip-x"
                onClick={() => dispatch(removeListItem({ list, index: i }))}
                aria-label={`Remove ${m}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      {showAdd && (
        <div className="add-row">
          <input
            type="text"
            placeholder="Name..."
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && add()}
          />
          <button type="button" onClick={add}>
            Add
          </button>
        </div>
      )}
    </div>
  )
}

export default function LogInteractionForm() {
  const form = useSelector((s) => s.form)
  const suggestions = useSelector((s) => s.chat.suggestions)
  const dispatch = useDispatch()
  const set = (field) => (e) => dispatch(updateField({ field, value: e.target.value }))

  return (
    <div className="panel form-panel">
      <h2 className="panel-title">Log HCP Interaction</h2>

      <div className="section-label">Interaction Details</div>

      <div className="grid-2">
        <div className="field">
          <label>HCP Name</label>
          <input
            type="text"
            placeholder="Search or select HCP..."
            value={form.hcpName}
            onChange={set('hcpName')}
          />
        </div>
        <div className="field">
          <label>Interaction Type</label>
          <select value={form.interactionType} onChange={set('interactionType')}>
            {INTERACTION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid-2">
        <div className="field">
          <label>Date</label>
          <input type="date" value={form.date} onChange={set('date')} />
        </div>
        <div className="field">
          <label>Time</label>
          <input type="time" value={form.time} onChange={set('time')} />
        </div>
      </div>

      <div className="field">
        <label>Attendees</label>
        <input
          type="text"
          placeholder="Enter names or search..."
          value={form.attendees}
          onChange={set('attendees')}
        />
      </div>

      <div className="field">
        <label>Topics Discussed</label>
        <textarea
          rows={3}
          placeholder="Enter key discussion points..."
          value={form.topicsDiscussed}
          onChange={set('topicsDiscussed')}
        />
      </div>

      <button className="voice-btn" type="button" onClick={(e) => e.preventDefault()}>
        ✨ Summarize from Voice Note (Requires Consent)
      </button>

      <div className="section-label">Materials Shared / Samples Distributed</div>

      <ItemBox
        list="materialsShared"
        title="Materials Shared"
        items={form.materialsShared}
        emptyText="No materials added."
        addLabel="🔍 Search/Add"
      />
      <ItemBox
        list="samplesDistributed"
        title="Samples Distributed"
        items={form.samplesDistributed}
        emptyText="No samples added."
        addLabel="📦 Add Sample"
      />

      <div className="field sentiment-field">
        <label>Observed/Inferred HCP Sentiment</label>
        <div className="sentiment-row">
          {SENTIMENTS.map((s) => (
            <label key={s.key} className="sentiment-opt">
              <input
                type="radio"
                name="sentiment"
                checked={form.sentiment === s.key}
                onChange={() => dispatch(updateField({ field: 'sentiment', value: s.key }))}
              />
              <span className="sentiment-stack">
                <span className="sentiment-emoji">{s.emoji}</span>
                <span>{s.label}</span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="field">
        <label>Outcomes</label>
        <textarea
          rows={2}
          placeholder="Key outcomes or agreements..."
          value={form.outcomes}
          onChange={set('outcomes')}
        />
      </div>

      <div className="field">
        <label>Follow-up Actions</label>
        <textarea
          rows={2}
          placeholder="Enter next steps or tasks..."
          value={form.followUpActions}
          onChange={set('followUpActions')}
        />
      </div>

      {suggestions.length > 0 && (
        <div className="ai-suggestions">
          <div className="ai-suggestions-title">AI Suggested Follow-ups:</div>
          {suggestions.map((s, i) => (
            <button
              key={i}
              type="button"
              className="ai-suggestion"
              onClick={() => dispatch(sendMessage(s))}
            >
              + {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
