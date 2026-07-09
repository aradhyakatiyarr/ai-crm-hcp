import LogInteractionForm from './components/LogInteractionForm'
import AIAssistant from './components/AIAssistant'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">✦</span> AI-First CRM
          <span className="brand-sub">HCP Module</span>
        </div>
        <div className="app-header-hint">Log Interaction Screen</div>
      </header>

      <main className="split">
        <LogInteractionForm />
        <AIAssistant />
      </main>
    </div>
  )
}
