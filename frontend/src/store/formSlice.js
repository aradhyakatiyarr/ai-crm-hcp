import { createSlice } from '@reduxjs/toolkit'

export const initialForm = {
  hcpName: '',
  interactionType: 'Meeting',
  date: '',
  time: '',
  attendees: '',
  topicsDiscussed: '',
  materialsShared: [],
  samplesDistributed: [],
  sentiment: '',
  outcomes: '',
  followUpDate: '',
  followUpActions: '',
}

const formSlice = createSlice({
  name: 'form',
  initialState: initialForm,
  reducers: {
    // Replace the form with the server-returned state (after the AI runs tools).
    setForm: (state, action) => ({ ...state, ...action.payload }),
    // Manual edits (kept available so the form still works both ways).
    updateField: (state, action) => {
      state[action.payload.field] = action.payload.value
    },
    // payload: { list: 'materialsShared' | 'samplesDistributed', index }
    removeListItem: (state, action) => {
      const { list, index } = action.payload
      state[list] = state[list].filter((_, i) => i !== index)
    },
    // payload: { list, value }
    addListItem: (state, action) => {
      const { list, value } = action.payload
      if (value && !state[list].includes(value)) state[list].push(value)
    },
    resetForm: () => initialForm,
  },
})

export const { setForm, updateField, removeListItem, addListItem, resetForm } = formSlice.actions
export default formSlice.reducer
