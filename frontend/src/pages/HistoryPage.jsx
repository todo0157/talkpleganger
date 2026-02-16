import { useState, useEffect } from 'react'
import { historyAPI, personaAPI } from '../api'

function HistoryPage() {
  const [personas, setPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [totalCount, setTotalCount] = useState(0)
  const LIMIT = 20

  useEffect(() => {
    loadPersonas()
  }, [])

  useEffect(() => {
    if (selectedPersona) {
      loadHistory()
      loadStats()
    }
  }, [selectedPersona, page])

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

  const loadHistory = async () => {
    try {
      setLoading(true)
      const res = await historyAPI.get(selectedPersona, LIMIT, page * LIMIT)
      setHistory(res.data.messages)
      setHasMore(res.data.has_more)
      setTotalCount(res.data.total_count)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const res = await historyAPI.getStats(selectedPersona)
      setStats(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleClearHistory = async () => {
    if (!confirm('모든 대화 기록을 삭제하시겠습니까?')) return
    try {
      await historyAPI.clear(selectedPersona)
      setHistory([])
      setStats(null)
      setTotalCount(0)
      alert('대화 기록이 삭제되었습니다.')
    } catch (err) {
      alert('삭제 실패')
    }
  }

  const handleDeleteMessage = async (messageId) => {
    try {
      await historyAPI.deleteMessage(messageId)
      setHistory(history.filter(m => m.id !== messageId))
      setTotalCount(prev => prev - 1)
    } catch (err) {
      alert('삭제 실패')
    }
  }

  const getEmotionEmoji = (emotion) => {
    const emojiMap = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      anxious: '😰',
      excited: '🤩',
      neutral: '😐',
      confused: '😕',
      grateful: '🙏',
      apologetic: '😔',
      urgent: '⚡',
    }
    return emojiMap[emotion] || '😐'
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="page">
      <h1 className="page-title">📜 대화 히스토리</h1>
      <p className="page-subtitle">AI가 생성한 답장 기록을 확인해요</p>

      {personas.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
            먼저 <a href="/persona" style={{ color: 'var(--primary)' }}>페르소나를 등록</a>해주세요
          </p>
        </div>
      ) : (
        <>
          {/* Persona Selector */}
          <div className="card">
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">페르소나 선택</label>
              <select
                className="form-select"
                value={selectedPersona}
                onChange={(e) => {
                  setSelectedPersona(e.target.value)
                  setPage(0)
                }}
              >
                {personas.map((p) => (
                  <option key={p.user_id} value={p.user_id}>
                    {p.name} ({p.user_id})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Statistics */}
          {stats && stats.total_messages > 0 && (
            <div className="card">
              <h3 className="card-title">📊 통계</h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '1rem',
                textAlign: 'center',
              }}>
                <div style={{
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '12px',
                  padding: '1rem',
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                    {stats.total_messages}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>총 대화</div>
                </div>
                <div style={{
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '12px',
                  padding: '1rem',
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                    {stats.unique_senders}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>상대방 수</div>
                </div>
                <div style={{
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '12px',
                  padding: '1rem',
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                    {Math.round(stats.avg_confidence * 100)}%
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>평균 신뢰도</div>
                </div>
              </div>

              {/* Emotion Distribution */}
              {Object.keys(stats.emotion_distribution || {}).length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    감정 분포
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {Object.entries(stats.emotion_distribution).map(([emotion, count]) => (
                      <span key={emotion} style={{
                        background: 'rgba(255,255,255,0.1)',
                        padding: '0.3rem 0.6rem',
                        borderRadius: '12px',
                        fontSize: '0.8rem',
                      }}>
                        {getEmotionEmoji(emotion)} {count}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Chat History */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 className="card-title" style={{ marginBottom: 0 }}>💬 대화 기록</h3>
              {history.length > 0 && (
                <button
                  className="btn btn-danger"
                  style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                  onClick={handleClearHistory}
                >
                  전체 삭제
                </button>
              )}
            </div>

            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                <span>불러오는 중...</span>
              </div>
            ) : history.length === 0 ? (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>
                대화 기록이 없습니다. Auto 모드에서 답장을 생성해보세요!
              </p>
            ) : (
              <>
                <div style={{ marginBottom: '0.75rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  총 {totalCount}개의 대화
                </div>

                {history.map((msg) => (
                  <div key={msg.id} style={{
                    background: 'rgba(0,0,0,0.2)',
                    borderRadius: '12px',
                    padding: '1rem',
                    marginBottom: '0.75rem',
                  }}>
                    {/* Header */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '0.75rem',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: '600' }}>{msg.sender_name}</span>
                        {msg.emotion && (
                          <span style={{ fontSize: '1.1rem' }}>{getEmotionEmoji(msg.emotion)}</span>
                        )}
                        {msg.confidence_score && (
                          <span className="confidence-badge confidence-high" style={{ fontSize: '0.7rem' }}>
                            {Math.round(msg.confidence_score * 100)}%
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {formatDate(msg.created_at)}
                        </span>
                        <button
                          onClick={() => handleDeleteMessage(msg.id)}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--text-muted)',
                            cursor: 'pointer',
                            padding: '0.25rem',
                            fontSize: '0.9rem',
                          }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>

                    {/* Incoming Message */}
                    <div style={{
                      background: 'rgba(255,255,255,0.05)',
                      borderRadius: '8px',
                      padding: '0.75rem',
                      marginBottom: '0.5rem',
                    }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                        받은 메시지
                      </div>
                      {msg.message_text}
                    </div>

                    {/* Response */}
                    {msg.response_text && (
                      <div style={{
                        background: 'rgba(254, 229, 0, 0.1)',
                        borderRadius: '8px',
                        padding: '0.75rem',
                        borderLeft: '3px solid var(--primary)',
                      }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                          AI 답장
                        </div>
                        {msg.response_text}
                      </div>
                    )}
                  </div>
                ))}

                {/* Pagination */}
                <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
                  <button
                    className="btn btn-secondary"
                    disabled={page === 0}
                    onClick={() => setPage(p => p - 1)}
                  >
                    이전
                  </button>
                  <span style={{ padding: '0.5rem 1rem', color: 'var(--text-muted)' }}>
                    {page + 1} / {Math.ceil(totalCount / LIMIT) || 1}
                  </span>
                  <button
                    className="btn btn-secondary"
                    disabled={!hasMore}
                    onClick={() => setPage(p => p + 1)}
                  >
                    다음
                  </button>
                </div>
              </>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default HistoryPage
