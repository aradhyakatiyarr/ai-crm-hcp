import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { postChat } from '../api/client'
import { setForm } from './formSlice'

// Send a message to the LangGraph agent. The current form is sent along so the
// agent's tools can patch it; the updated form comes back and we store it.
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (text, { getState, dispatch }) => {
    const state = getState()
    const form = state.form
    // history = everything EXCEPT the just-added user message (last item).
    const history = state.chat.messages
      .slice(0, -1)
      .map((m) => ({ role: m.role, content: m.content }))

    const res = await postChat({ message: text, form, history })
    dispatch(setForm(res.form))
    return res
  },
)

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    loading: false,
    error: null,
    suggestions: [],
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state, action) => {
        state.loading = true
        state.error = null
        state.messages.push({ role: 'user', content: action.meta.arg })
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false
        state.suggestions = action.payload.suggestions || []
        state.messages.push({
          role: 'assistant',
          content: action.payload.reply,
          actions: action.payload.actions || [],
        })
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
        state.messages.push({
          role: 'assistant',
          content: '⚠️ ' + (action.error.message || 'Could not reach the AI backend.'),
        })
      })
  },
})

export default chatSlice.reducer
