import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchRequests } from '../api/requests'
import PageShell from '../components/PageShell'
import TriageBadge from '../components/TriageBadge'

function ReviewerQueuePage() {
  const [requests, setRequests] = useState([])
  const [nextCursor, setNextCursor] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadRequests() {
      try {
        const page = await fetchRequests()
        setRequests(page.items)
        setNextCursor(page.next_cursor)
      } catch (error) {
        setErrorMessage(error.message)
      } finally {
        setIsLoading(false)
      }
    }

    loadRequests()
  }, [])

  async function loadMoreRequests() {
    setIsLoading(true)
    try {
      const page = await fetchRequests(nextCursor)
      setRequests((currentRequests) => [...currentRequests, ...page.items])
      setNextCursor(page.next_cursor)
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <PageShell>
      <div className="page-actions">
        <span className="back-link">Reviewer queue</span>
      </div>
      <section className="intro reviewer-intro" aria-labelledby="queue-title">
        <p className="eyebrow">Reviewer workspace</p>
        <h1 id="queue-title">Request queue</h1>
        <p className="intro-copy">Review the newest requests and open one to assess its brief.</p>
      </section>
      {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
      {isLoading && <p className="loading-message">Loading requests…</p>}
      {!isLoading && !errorMessage && requests.length === 0 && (
        <p className="empty-message">No requests are ready for review yet.</p>
      )}
      {!isLoading && requests.length > 0 && (
        <>
          <section className="queue-list" aria-label="Business requests">
            {requests.map((request) => (
              <Link className="queue-row" to={`/requests/${request.id}`} key={request.id}>
                <div>
                  <p className="queue-request">{request.raw_request}</p>
                  <p className="queue-action">Next: {request.suggested_next_action}</p>
                </div>
                <div className="queue-meta">
                  <TriageBadge type="status" value={request.status} />
                  <TriageBadge type="priority" value={request.priority} />
                  <span className="owner-badge">{request.owner ?? 'Unassigned'}</span>
                </div>
              </Link>
            ))}
          </section>
          {nextCursor && (
            <button className="load-more-button" type="button" onClick={loadMoreRequests}>
              Load more requests
            </button>
          )}
        </>
      )}
    </PageShell>
  )
}

export default ReviewerQueuePage
