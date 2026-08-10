import { Link } from 'react-router-dom'
import TriageBadge from './TriageBadge'

function BriefResult({ submission }) {
  const { brief } = submission

  return (
    <section className="brief-result" aria-labelledby="brief-title">
      <div className="result-heading">
        <div>
          <p className="eyebrow">Generated brief</p>
          <h2 id="brief-title">Ready for review</h2>
        </div>
        <div className="triage-labels" aria-label="Current triage status">
          <TriageBadge type="status" value={submission.status} />
          <TriageBadge type="priority" value={submission.priority} />
        </div>
      </div>
      <BriefSection title="Problem summary"><p>{brief.problem_summary}</p></BriefSection>
      <BriefSection title="Likely users" items={brief.likely_users} />
      <BriefSection title="Recommended solution type"><p>{brief.recommended_solution_type}</p></BriefSection>
      <BriefSection title="Clarifying questions" items={brief.clarifying_questions} />
      <BriefSection title="Risks" items={brief.risks} />
      <BriefSection title="Suggested next action" highlighted><p>{brief.suggested_next_action}</p></BriefSection>
      <TriageHistory requestId={submission.id} updates={submission.triage_updates} />
    </section>
  )
}

function BriefSection({ title, items, children, highlighted = false }) {
  return (
    <div className={`brief-section${highlighted ? ' next-action' : ''}`}>
      <h3>{title}</h3>
      {items ? <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul> : children}
    </div>
  )
}

function TriageHistory({ requestId, updates, showAll = false }) {
  const updatesToShow = showAll ? updates : [...updates].slice(-3).reverse()

  return (
    <section className="triage-history" aria-labelledby="history-title">
      <h3 id="history-title">Triage history</h3>
      {updatesToShow.length === 0 ? (
        <p>No reviewer updates yet.</p>
      ) : (
        <ul>
          {updatesToShow.map((update) => (
            <li key={update.id}>
              <div className="history-update">
                <div className="history-badges">
                  <TriageBadge type="status" value={update.status} />
                  <TriageBadge type="priority" value={update.priority} />
                </div>
                {update.notes && <p className="history-note">{update.notes}</p>}
              </div>
              <span>{new Date(update.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      )}
      {!showAll && updates.length > 3 && (
        <Link className="history-link" to={`/requests/${requestId}/history`}>
          View complete history →
        </Link>
      )}
    </section>
  )
}

export { TriageHistory }
export default BriefResult
