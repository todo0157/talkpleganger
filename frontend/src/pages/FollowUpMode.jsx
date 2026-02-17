import { useState, useEffect } from 'react'
import { followupAPI, personaAPI } from '../api'

const RELATIONSHIPS = [
  { id: 'boss', label: '상사', icon: '👔' },
  { id: 'colleague', label: '동료', icon: '👥' },
  { id: 'client', label: '거래처', icon: '💼' },
  { id: 'professor', label: '교수님', icon: '📚' },
  { id: 'friend', label: '친구', icon: '👋' },
  { id: 'partner', label: '연인', icon: '💕' },
  { id: 'family', label: '가족', icon: '🏠' },
  { id: 'acquaintance', label: '지인', icon: '🤝' },
]

const STRATEGY_INFO = {
  gentle_reminder: { label: '부드러운 리마인더', color: '#22c55e', icon: '💡' },
  casual_check: { label: '가벼운 안부', color: '#3b82f6', icon: '👋' },
  conversation_starter: { label: '새 화제 전환', color: '#f59e0b', icon: '💬' },
  topic_change: { label: '주제 변경', color: '#8b5cf6', icon: '🔄' },
  reconnect: { label: '다시 연결', color: '#ec4899', icon: '🔗' },
}

function FollowUpMode() {
  const [personas, setPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [lastMessage, setLastMessage] = useState('')
  const [hoursElapsed, setHoursElapsed] = useState(2)
  const [relationship, setRelationship] = useState('friend')
  const [originalIntent, setOriginalIntent] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [strategies, setStrategies] = useState([])

  useEffect(() => {
    loadPersonas()
    loadStrategies()
  }, [])

  const loadPersonas = async () => {
    try {
      const res = await personaAPI.list()
      setPersonas(res.data)
      if (res.data.length > 0) {
        setSelectedPersona(res.data[0].user_id)
      }
    } catch (err) {
      console.error(err)
    }
  }

  const loadStrategies = async () => {
    try {
      const res = await followupAPI.getStrategies()
      setStrategies(res.data.strategies)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setResponse(null)

    if (!selectedPersona) {
      setError('페르소나를 먼저 선택해주세요')
      return
    }

    try {
      setLoading(true)
      const res = await followupAPI.suggest({
        user_id: selectedPersona,
        last_message_text: lastMessage,
        hours_elapsed: hoursElapsed,
        recipient_relationship: relationship,
        original_intent: originalIntent || null,
      })
      setResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '후속 메시지 생성에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('클립보드에 복사되었습니다!')
  }

  const getRiskColor = (risk) => {
    if (risk === 'low') return '#22c55e'
    if (risk === 'medium') return '#f59e0b'
    return '#ef4444'
  }

  const getTimeLabel = (hours) => {
    if (hours < 1) return `${Math.round(hours * 60)}분`
    if (hours < 24) return `${hours}시간`
    return `${Math.round(hours / 24)}일`
  }

  return (
    <div className="page">
      <h1 className="page-title">💬 읽씹 대응</h1>
      <p className="page-subtitle">답장이 없을 때 자연스러운 후속 메시지를 생성해요</p>

      {personas.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
            먼저 <a href="/persona" style={{ color: 'var(--primary)' }}>페르소나를 등록</a>해주세요
          </p>
        </div>
      ) : (
        <>
          <div className="card">
            <h3 className="card-title">🎭 페르소나 선택</h3>
            <select
              className="form-input"
              value={selectedPersona}
              onChange={(e) => setSelectedPersona(e.target.value)}
            >
              {personas.map((p) => (
                <option key={p.user_id} value={p.user_id}>
                  {p.icon || '👤'} {p.name}
                </option>
              ))}
            </select>
          </div>

          <div className="card">
            <h3 className="card-title">📝 상황 입력</h3>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">마지막으로 보낸 메시지</label>
                <textarea
                  className="form-textarea"
                  placeholder="내가 마지막으로 보낸 메시지를 입력하세요..."
                  value={lastMessage}
                  onChange={(e) => setLastMessage(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">경과 시간</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <input
                    type="range"
                    min="0.5"
                    max="48"
                    step="0.5"
                    value={hoursElapsed}
                    onChange={(e) => setHoursElapsed(parseFloat(e.target.value))}
                    style={{ flex: 1 }}
                  />
                  <span style={{
                    minWidth: '80px',
                    padding: '0.5rem 0.75rem',
                    background: 'rgba(59, 130, 246, 0.2)',
                    borderRadius: '8px',
                    textAlign: 'center',
                    fontWeight: '600',
                  }}>
                    {getTimeLabel(hoursElapsed)}
                  </span>
                </div>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  marginTop: '0.25rem',
                }}>
                  <span>30분</span>
                  <span>48시간</span>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">상대방과의 관계</label>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {RELATIONSHIPS.map((rel) => (
                    <button
                      key={rel.id}
                      type="button"
                      onClick={() => setRelationship(rel.id)}
                      style={{
                        padding: '0.5rem 0.75rem',
                        borderRadius: '8px',
                        border: relationship === rel.id
                          ? '2px solid var(--primary)'
                          : '2px solid transparent',
                        background: relationship === rel.id
                          ? 'rgba(59, 130, 246, 0.2)'
                          : 'rgba(255, 255, 255, 0.1)',
                        color: 'var(--text-light)',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                      }}
                    >
                      {rel.icon} {rel.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">원래 대화 의도 (선택)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: 약속 잡기, 부탁하기, 안부 묻기..."
                  value={originalIntent}
                  onChange={(e) => setOriginalIntent(e.target.value)}
                />
              </div>

              {error && (
                <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>
              )}

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? '생성 중...' : '후속 메시지 생성하기'}
              </button>
            </form>
          </div>

          {/* Strategy Guide */}
          <div className="card">
            <h3 className="card-title">📖 전략 가이드</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {strategies.map((s) => (
                <div
                  key={s.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.75rem',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '8px',
                  }}
                >
                  <span style={{ fontSize: '1.25rem' }}>
                    {STRATEGY_INFO[s.id]?.icon || '💬'}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>
                      {s.label}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {s.hours} | {s.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {loading && (
            <div className="card">
              <div className="loading">
                <div className="spinner"></div>
                <span>AI가 후속 메시지를 생성하고 있어요...</span>
              </div>
            </div>
          )}

          {response && (
            <div className="card">
              <h3 className="card-title">✅ 추천 후속 메시지</h3>

              {/* Recommended Strategy */}
              <div style={{
                background: `linear-gradient(135deg, ${STRATEGY_INFO[response.recommended_strategy]?.color || '#3b82f6'}20 0%, transparent 100%)`,
                borderRadius: '12px',
                padding: '1rem',
                marginBottom: '1rem',
                border: `1px solid ${STRATEGY_INFO[response.recommended_strategy]?.color || '#3b82f6'}40`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '1.5rem' }}>
                    {STRATEGY_INFO[response.recommended_strategy]?.icon || '💬'}
                  </span>
                  <div>
                    <div style={{ fontWeight: '700' }}>
                      추천 전략: {STRATEGY_INFO[response.recommended_strategy]?.label || response.recommended_strategy}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      경과 시간: {getTimeLabel(response.elapsed_hours)}
                    </div>
                  </div>
                </div>
                <div style={{
                  fontSize: '0.9rem',
                  color: 'var(--text-light)',
                  background: 'rgba(0,0,0,0.2)',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '8px',
                }}>
                  {response.strategy_explanation}
                </div>
              </div>

              {/* Wait More Warning */}
              {response.should_wait_more && (
                <div style={{
                  background: 'rgba(245, 158, 11, 0.15)',
                  border: '1px solid rgba(245, 158, 11, 0.4)',
                  borderRadius: '8px',
                  padding: '0.75rem 1rem',
                  marginBottom: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                }}>
                  <span style={{ fontSize: '1.25rem' }}>⏳</span>
                  <div>
                    <div style={{ fontWeight: '600', color: '#f59e0b' }}>조금 더 기다려보세요</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {response.recommended_additional_wait_hours
                        ? `약 ${getTimeLabel(response.recommended_additional_wait_hours)} 더 기다린 후 연락하는 것이 좋아요`
                        : '지금 연락하면 부담스러울 수 있어요'}
                    </div>
                  </div>
                </div>
              )}

              {/* Suggestions */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {response.suggestions.map((suggestion, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'rgba(255,255,255,0.05)',
                      borderRadius: '12px',
                      padding: '1rem',
                      border: '1px solid rgba(255,255,255,0.1)',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        background: `${STRATEGY_INFO[suggestion.strategy]?.color || '#3b82f6'}25`,
                        color: STRATEGY_INFO[suggestion.strategy]?.color || '#3b82f6',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                      }}>
                        {STRATEGY_INFO[suggestion.strategy]?.label || suggestion.strategy}
                      </span>
                      <span style={{
                        padding: '0.2rem 0.4rem',
                        background: `${getRiskColor(suggestion.risk_level)}20`,
                        color: getRiskColor(suggestion.risk_level),
                        borderRadius: '4px',
                        fontSize: '0.7rem',
                      }}>
                        위험도: {suggestion.risk_level}
                      </span>
                    </div>

                    <div style={{
                      fontSize: '1rem',
                      fontWeight: '500',
                      marginBottom: '0.5rem',
                      lineHeight: '1.5',
                    }}>
                      "{suggestion.message}"
                    </div>

                    <div style={{
                      fontSize: '0.8rem',
                      color: 'var(--text-muted)',
                      marginBottom: '0.75rem',
                    }}>
                      {suggestion.tone_description} | {suggestion.recommended_for}
                    </div>

                    <button
                      className="btn btn-secondary"
                      onClick={() => copyToClipboard(suggestion.message)}
                      style={{ fontSize: '0.85rem', padding: '0.4rem 0.8rem' }}
                    >
                      📋 복사
                    </button>
                  </div>
                ))}
              </div>

              {/* Tips */}
              {response.tips?.length > 0 && (
                <div style={{ marginTop: '1.5rem' }}>
                  <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-muted)' }}>
                    💡 팁
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', color: 'var(--text-light)' }}>
                    {response.tips.map((tip, i) => (
                      <li key={i} style={{ marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default FollowUpMode
