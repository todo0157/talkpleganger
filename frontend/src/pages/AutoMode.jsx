import { useState, useEffect } from 'react'
import { autoAPI, personaAPI } from '../api'

// 카테고리 정의
const CATEGORIES = {
  all: { label: '전체', icon: '📋', color: '#fff' },
  work: { label: '회사', icon: '💼', color: '#3b82f6' },
  friend: { label: '친구', icon: '👋', color: '#22c55e' },
  family: { label: '가족', icon: '🏠', color: '#f97316' },
  partner: { label: '연인', icon: '💕', color: '#ec4899' },
  formal: { label: '격식', icon: '🎩', color: '#6366f1' },
  casual: { label: '캐주얼', icon: '😎', color: '#14b8a6' },
  other: { label: '기타', icon: '📝', color: '#64748b' },
}

function AutoMode() {
  const [personas, setPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [senderName, setSenderName] = useState('')
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadPersonas()
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
      const res = await autoAPI.respond({
        user_id: selectedPersona,
        incoming_message: {
          sender_id: `sender_${senderName}`,
          sender_name: senderName,
          message_text: message,
        },
      })
      setResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '응답 생성에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('클립보드에 복사되었습니다!')
  }

  const getConfidenceClass = (score) => {
    if (score >= 0.8) return 'confidence-high'
    if (score >= 0.5) return 'confidence-medium'
    return 'confidence-low'
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

  const getEmotionLabel = (emotion) => {
    const labelMap = {
      happy: '기쁨',
      sad: '슬픔',
      angry: '화남',
      anxious: '불안',
      excited: '흥분',
      neutral: '중립',
      confused: '혼란',
      grateful: '감사',
      apologetic: '미안함',
      urgent: '긴급',
    }
    return labelMap[emotion] || '중립'
  }

  const getEmotionColor = (emotion) => {
    const colorMap = {
      happy: '#22c55e',
      sad: '#3b82f6',
      angry: '#ef4444',
      anxious: '#f59e0b',
      excited: '#ec4899',
      neutral: '#9ca3af',
      confused: '#8b5cf6',
      grateful: '#14b8a6',
      apologetic: '#6b7280',
      urgent: '#f97316',
    }
    return colorMap[emotion] || '#9ca3af'
  }

  return (
    <div className="page">
      <h1 className="page-title">🤖 Auto Mode</h1>
      <p className="page-subtitle">내 말투 그대로 자동 답장을 생성해요</p>

      {personas.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
            먼저 <a href="/persona" style={{ color: 'var(--primary)' }}>페르소나를 등록</a>해주세요
          </p>
        </div>
      ) : (
        <>
          {/* Quick Persona Switching */}
          <div className="card">
            <h3 className="card-title">🎭 페르소나 선택</h3>

            {/* Category Filter */}
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
              {Object.entries(CATEGORIES).map(([key, { label, icon, color }]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setSelectedCategory(key)}
                  style={{
                    padding: '0.4rem 0.8rem',
                    borderRadius: '16px',
                    border: selectedCategory === key ? `2px solid ${color}` : '2px solid transparent',
                    background: selectedCategory === key ? `${color}20` : 'rgba(255,255,255,0.1)',
                    color: selectedCategory === key ? color : 'var(--text-muted)',
                    cursor: 'pointer',
                    fontSize: '0.85rem',
                    transition: 'all 0.2s',
                  }}
                >
                  {icon} {label}
                </button>
              ))}
            </div>

            {/* Persona Cards */}
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {personas
                .filter(p => selectedCategory === 'all' || p.category === selectedCategory)
                .map((p) => {
                  const cat = CATEGORIES[p.category] || CATEGORIES.other
                  const isSelected = selectedPersona === p.user_id
                  return (
                    <button
                      key={p.user_id}
                      type="button"
                      onClick={() => setSelectedPersona(p.user_id)}
                      style={{
                        padding: '0.75rem 1rem',
                        borderRadius: '12px',
                        border: isSelected ? `2px solid ${cat.color}` : '2px solid transparent',
                        background: isSelected ? `${cat.color}25` : 'rgba(0,0,0,0.2)',
                        color: 'var(--text-light)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        transition: 'all 0.2s',
                        minWidth: '120px',
                      }}
                    >
                      <span style={{ fontSize: '1.25rem' }}>{p.icon || cat.icon}</span>
                      <div style={{ textAlign: 'left' }}>
                        <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{p.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {cat.label}
                        </div>
                      </div>
                      {isSelected && (
                        <span style={{ marginLeft: 'auto', color: cat.color }}>✓</span>
                      )}
                    </button>
                  )
                })}
            </div>

            {personas.filter(p => selectedCategory === 'all' || p.category === selectedCategory).length === 0 && (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1rem' }}>
                이 카테고리에 페르소나가 없습니다
              </p>
            )}
          </div>

          <div className="card">
            <h3 className="card-title">💬 메시지 입력</h3>

            <form onSubmit={handleSubmit}>

              <div className="form-group">
                <label className="form-label">보낸 사람 이름</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: 김철수"
                  value={senderName}
                  onChange={(e) => setSenderName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">받은 메시지</label>
                <textarea
                  className="form-textarea"
                  placeholder="상대방이 보낸 메시지를 입력하세요..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  required
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
                {loading ? '생성 중...' : '답장 생성하기'}
              </button>
            </form>
          </div>

          {loading && (
            <div className="card">
              <div className="loading">
                <div className="spinner"></div>
                <span>AI가 답장을 생성하고 있어요...</span>
              </div>
            </div>
          )}

          {response && (
            <div className="card">
              <h3 className="card-title">✅ 생성된 답장</h3>

              {/* Emotion Analysis Section */}
              {response.emotion_analysis && (
                <div style={{
                  background: `linear-gradient(135deg, ${getEmotionColor(response.emotion_analysis.primary_emotion)}15 0%, ${getEmotionColor(response.emotion_analysis.primary_emotion)}05 100%)`,
                  borderRadius: '12px',
                  padding: '1rem',
                  marginBottom: '1rem',
                  border: `1px solid ${getEmotionColor(response.emotion_analysis.primary_emotion)}30`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '2rem' }}>
                      {getEmotionEmoji(response.emotion_analysis.primary_emotion)}
                    </span>
                    <div>
                      <div style={{ fontWeight: '700', fontSize: '1rem' }}>
                        감정 분석: {getEmotionLabel(response.emotion_analysis.primary_emotion)}
                      </div>
                      <div style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-muted)',
                        marginTop: '0.25rem'
                      }}>
                        강도: {Math.round(response.emotion_analysis.emotion_intensity * 100)}%
                      </div>
                    </div>
                  </div>

                  {response.emotion_analysis.emotion_keywords?.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                      {response.emotion_analysis.emotion_keywords.map((keyword, i) => (
                        <span key={i} style={{
                          background: 'rgba(255,255,255,0.1)',
                          padding: '0.25rem 0.6rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                        }}>
                          {keyword}
                        </span>
                      ))}
                    </div>
                  )}

                  <div style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-light)',
                    background: 'rgba(0,0,0,0.2)',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '8px',
                  }}>
                    <strong>톤 조절:</strong> {response.emotion_analysis.tone_adjustment}
                  </div>
                </div>
              )}

              <div className="response-box">
                <div className="response-header">
                  <span className="response-label">추천 답장</span>
                  <span className={`confidence-badge ${getConfidenceClass(response.confidence_score)}`}>
                    신뢰도: {Math.round(response.confidence_score * 100)}%
                  </span>
                </div>
                <div className="response-text">{response.answer}</div>
                <button
                  className="btn btn-secondary copy-btn"
                  onClick={() => copyToClipboard(response.answer)}
                >
                  📋 복사하기
                </button>
              </div>

              {response.detected_intent && (
                <div style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>
                  <strong>감지된 의도:</strong> {response.detected_intent}
                </div>
              )}

              {response.suggested_alternatives?.length > 0 && (
                <div style={{ marginTop: '1.5rem' }}>
                  <h4 style={{ marginBottom: '0.75rem', color: 'var(--text-muted)' }}>
                    대안 답장
                  </h4>
                  {response.suggested_alternatives.map((alt, i) => (
                    <div key={i} className="response-box" style={{ marginTop: '0.5rem' }}>
                      <div className="response-text" style={{ background: 'rgba(255,255,255,0.05)' }}>
                        {alt}
                      </div>
                      <button
                        className="btn btn-secondary copy-btn"
                        onClick={() => copyToClipboard(alt)}
                      >
                        📋 복사
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AutoMode
