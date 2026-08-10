function TriageBadge({ type, value }) {
  const label = value.replace('_', ' ')
  const displayValue = type === 'priority' ? `${label} priority` : label

  return <span className={`triage-badge ${type}-${value}`}>{displayValue}</span>
}

export default TriageBadge
