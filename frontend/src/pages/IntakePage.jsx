import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { createRequest } from '../api/requests'
import PageShell from '../components/PageShell'

function IntakePage() {
  const [rawRequest, setRawRequest] = useState('')
  const [generationMode, setGenerationMode] = useState('mock')
  const [errorMessage, setErrorMessage] = useState('')
  const [similarityWarning, setSimilarityWarning] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const submittedMessage = location.state?.successMessage
    if (!submittedMessage) return undefined

    const timeoutId = window.setTimeout(() => {
      setSuccessMessage(submittedMessage)
      navigate(location.pathname, { replace: true, state: null })
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [location.pathname, location.state, navigate])

  useEffect(() => {
    if (!successMessage) return undefined

    const timeoutId = window.setTimeout(() => setSuccessMessage(''), 5000)
    return () => window.clearTimeout(timeoutId)
  }, [successMessage])

  async function submitRequest(allowSimilar = false) {
    setErrorMessage('')
    setSimilarityWarning(false)
    setIsSubmitting(true)

    try {
      const submission = await createRequest(rawRequest, generationMode, allowSimilar)
      navigate('/', {
        state: {
          generationNotice: submission.generation_notice,
          successMessage: `Request #${submission.id} was submitted for reviewer triage.`,
        },
      })
    } catch (error) {
      if (error.code === 'similar_request') {
        setSimilarityWarning(true)
      } else {
        setErrorMessage(error.message)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    submitRequest()
  }

  return (
    <PageShell>
      <section className="intro" aria-labelledby="page-title">
        <p className="eyebrow">Business request intake</p>
        <h1 id="page-title">Turn a request into a review-ready brief.</h1>
        <p className="intro-copy">
          Share the business need in your own words. The triage service will create a
          structured brief for a reviewer.
        </p>
        {successMessage && (
          <p className="success-message" role="status">
            Request submitted successfully. A reviewer will review it soon.
          </p>
        )}
      </section>
      <section className="workspace" aria-label="Request brief generator">
        <form className="request-form" onSubmit={handleSubmit}>
          {similarityWarning && (
            <div className="similarity-warning" role="alert">
              <p>A potentially similar request exists. Submit this request only if it covers different work.</p>
              <button type="button" onClick={() => submitRequest(true)} disabled={isSubmitting}>
                Submit anyway
              </button>
            </div>
          )}
          {errorMessage && <p className="error-message" role="alert">{errorMessage}</p>}
          <label htmlFor="raw-request">What would you like the team to help with?</label>
          <textarea
            id="raw-request"
            name="rawRequest"
            value={rawRequest}
            onChange={(event) => setRawRequest(event.target.value)}
            placeholder="For example: We need a clearer way to prioritize internal software requests."
            rows="8"
            required
            disabled={isSubmitting}
          />
          <label className="generation-mode" htmlFor="generation-mode">
            Brief generation method
            <select
              id="generation-mode"
              value={generationMode}
              onChange={(event) => setGenerationMode(event.target.value)}
              disabled={isSubmitting}
            >
              <option value="mock">Mock service (default)</option>
              <option value="ai">AI service</option>
            </select>
          </label>
          <div className="form-footer">
            <p>Your request is saved with the generated brief.</p>
            <button type="submit" disabled={isSubmitting || !rawRequest.trim()}>
              {isSubmitting ? 'Generating brief…' : 'Generate brief'}
            </button>
          </div>
        </form>
      </section>
      <Link className="queue-link" to="/">← Back to requestor home</Link>
    </PageShell>
  )
}

export default IntakePage
