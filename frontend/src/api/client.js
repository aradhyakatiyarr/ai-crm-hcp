export async function postChat(body) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const raw = await res.text()
    let detail = raw
    try {
      const data = JSON.parse(raw)
      detail = data.detail || JSON.stringify(data)
    } catch {
      // raw wasn't JSON, keep as-is
    }
    throw new Error(`Backend ${res.status}: ${detail}`)
  }
  return res.json()
}
