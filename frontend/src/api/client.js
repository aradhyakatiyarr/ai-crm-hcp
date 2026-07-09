export async function postChat(body) {
  // Safety timeout so the chat never spins "loading forever" — abort after 45s.
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 45000)

  let res
  try {
    res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    })
  } catch (err) {
    clearTimeout(timer)
    if (err.name === 'AbortError') {
      throw new Error('Request timed out after 45s. Please try again.')
    }
    throw err
  }
  clearTimeout(timer)

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
