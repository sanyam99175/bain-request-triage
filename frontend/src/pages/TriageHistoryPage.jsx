import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchTriageHistory } from '../api/requests'
import PageShell from '../components/PageShell'
import { TriageHistory } from '../components/BriefResult'

function TriageHistoryPage() {
  const { requestId } = useParams()
  const [updates, setUpdates] = useState([])
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    async function loadHistory() {
      try {
        setUpdates(await fetchTriageHistory(requestId))
      } catch (error) {
        setErrorMessage(error.message)
      }
    }

    loadHistory()
  }, [requestId])

  return (
    <PageShell>
      <Link className="back-link" to={`/requests/${requestId}`}>← Request detail</Link>
      <section className="intro reviewer-intro">
        <p className="eyebrow">Reviewer workspace</p>
        <h1>Triage history</h1>
        <p className="intro-copy">Every saved triage decision for request #{requestId}.</p>
      </section>
      {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
      {!errorMessage && <section className="history-page"><TriageHistory updates={updates} showAll /></section>}
    </PageShell>
  )
}

export default TriageHistoryPage
