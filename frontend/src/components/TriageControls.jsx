import { useState } from 'react'
import { updateTriage } from '../api/requests'

function TriageControls({ submission, onUpdated }) {
  const [status, setStatus] = useState(submission.status)
  const [priority, setPriority] = useState(submission.priority)
  const [notes, setNotes] = useState(submission.notes ?? '')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setIsSaving(true)

    try {
      onUpdated(await updateTriage(submission.id, status, priority, notes, submission.version))
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <form className="triage-form" onSubmit={handleSubmit}>
      <div>
        <p className="eyebrow">Reviewer triage</p>
        <h2>Set triage details</h2>
      </div>
      <label>
        Status
        <select value={status} onChange={(event) => setStatus(event.target.value)} disabled={isSaving}>
          <option value="new">New</option>
          <option value="in_review">In review</option>
          <option value="approved">Approved</option>
          <option value="deferred">Deferred</option>
          <option value="completed">Completed</option>
        </select>
      </label>
      <label>
        Priority
        <select value={priority} onChange={(event) => setPriority(event.target.value)} disabled={isSaving}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </label>
      <label className="triage-notes">
        Reviewer notes
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="Add context for the next reviewer."
          rows="3"
          maxLength="5000"
          disabled={isSaving}
        />
      </label>
      <button type="submit" disabled={isSaving}>
        {isSaving ? 'Saving…' : 'Save triage'}
      </button>
      {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
    </form>
  )
}

export default TriageControls
