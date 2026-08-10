import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { fetchRequest } from '../api/requests'
import BriefResult from '../components/BriefResult'
import PageShell from '../components/PageShell'
import TriageControls from '../components/TriageControls'

function ReviewerDetailPage() {
  const { requestId } = useParams()
  const location = useLocation()
  const [submission, setSubmission] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    async function loadRequest() {
      try {
        setSubmission(await fetchRequest(requestId))
      } catch (error) {
        setErrorMessage(error.message)
      }
    }

    loadRequest()
  }, [requestId])

  return (
    <PageShell>
      <Link className="back-link" to="/">← Reviewer queue</Link>
      <section className="intro reviewer-intro">
        <p className="eyebrow">Reviewer workspace</p>
        <h1>Request #{requestId}</h1>
        <p className="intro-copy">Review the generated brief and decide the next action.</p>
      </section>
      {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
      {location.state?.generationNotice && (
        <p className="notice-message" role="status">{location.state.generationNotice}</p>
      )}
      {!submission && !errorMessage && <p className="loading-message">Loading request…</p>}
      {submission && (
        <>
          <TriageControls
            key={`${submission.id}-${submission.version}`}
            submission={submission}
            onUpdated={setSubmission}
          />
          <BriefResult submission={submission} />
        </>
      )}
    </PageShell>
  )
}

export default ReviewerDetailPage
