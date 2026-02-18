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
  // Context Memory Settings
  const [autoFetchContext, setAutoFetchContext] = useState(true)
  const [contextWindowSize, setContextWindowSize] = useState(10)
  // Timing Settings
  const [includeTiming, setIncludeTiming] = useState(true)
  // Manual Edit Mode
  const [isEditMode, setIsEditMode] = useState(false)
  const [editedAnswer, setEditedAnswer] = useState('')
  const [editHistory, setEditHistory] = useState([]) // 수정 이력 저장

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
        auto_fetch_context: autoFetchContext,
        context_window_size: contextWindowSize,
        include_timing: includeTiming,
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

  // Manual Edit Mode Functions
  const enterEditMode = () => {
    setIsEditMode(true)
    setEditedAnswer(response?.answer || '')
  }

  const exitEditMode = () => {
    setIsEditMode(false)
  }

  const saveEditedAnswer = () => {
    if (response && editedAnswer.trim()) {
      // 이력에 원본 저장
      setEditHistory(prev => [...prev, response.answer])
      // 응답 업데이트
      setResponse({
        ...response,
        answer: editedAnswer.trim(),
        isEdited: true,
      })
      setIsEditMode(false)
    }
  }

  const revertToOriginal = () => {
    if (editHistory.length > 0) {
      const lastOriginal = editHistory[editHistory.length - 1]
      setEditedAnswer(lastOriginal)
      setResponse({
        ...response,
        answer: lastOriginal,
        isEdited: false,
      })
      setEditHistory(prev => prev.slice(0, -1))
    }
  }

  const regenerateResponse = async () => {
    if (!selectedPersona || !message) return
    setIsEditMode(false)
    setEditHistory([])
    await handleSubmit({ preventDefault: () => {} })
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

              {/* Context & Timing Settings - Desktop Only */}
              <div className="desktop-settings" style={{
                background: 'rgba(255,255,255,0.05)',
                borderRadius: '12px',
                padding: '1rem',
                marginBottom: '1rem',
              }}>
                <div style={{ fontSize: '0.9rem', fontWeight: '600', marginBottom: '0.75rem' }}>
                  🛠️ 고급 설정
                </div>

                {/* Context Memory Toggle */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={autoFetchContext}
                      onChange={(e) => setAutoFetchContext(e.target.checked)}
                      style={{ width: '18px', height: '18px' }}
                    />
                    <span style={{ fontSize: '0.85rem' }}>🧠 대화 맥락 자동 기억</span>
                  </label>
                  {autoFetchContext && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="range"
                        min="5"
                        max="20"
                        value={contextWindowSize}
                        onChange={(e) => setContextWindowSize(parseInt(e.target.value))}
                        style={{ width: '80px' }}
                      />
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        최근 {contextWindowSize}개
                      </span>
                    </div>
                  )}
                </div>

                {/* Timing Recommendation Toggle */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={includeTiming}
                      onChange={(e) => setIncludeTiming(e.target.checked)}
                      style={{ width: '18px', height: '18px' }}
                    />
                    <span style={{ fontSize: '0.85rem' }}>⏱️ 답장 타이밍 추천</span>
                  </label>
                </div>
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
                  <span className="response-label">
                    {response.isEdited ? '✏️ 수정된 답장' : '추천 답장'}
                  </span>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className={`confidence-badge ${getConfidenceClass(response.confidence_score)}`}>
                      신뢰도: {Math.round(response.confidence_score * 100)}%
                    </span>
                    {/* Auto/Manual Mode Toggle */}
                    <button
                      onClick={() => isEditMode ? exitEditMode() : enterEditMode()}
                      style={{
                        padding: '0.3rem 0.6rem',
                        borderRadius: '6px',
                        border: isEditMode ? '1px solid var(--primary)' : '1px solid var(--border)',
                        background: isEditMode ? 'rgba(254, 229, 0, 0.2)' : 'rgba(255,255,255,0.1)',
                        color: isEditMode ? 'var(--primary)' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                      }}
                    >
                      {isEditMode ? '🔒 자동' : '✏️ 수동'}
                    </button>
                  </div>
                </div>

                {/* Edit Mode */}
                {isEditMode ? (
                  <div style={{ marginTop: '0.75rem' }}>
                    <textarea
                      value={editedAnswer}
                      onChange={(e) => setEditedAnswer(e.target.value)}
                      style={{
                        width: '100%',
                        minHeight: '120px',
                        padding: '1rem',
                        background: 'rgba(0,0,0,0.3)',
                        border: '2px solid var(--primary)',
                        borderRadius: '10px',
                        color: 'var(--text-light)',
                        fontSize: '1rem',
                        lineHeight: '1.7',
                        resize: 'vertical',
                      }}
                      placeholder="답장을 직접 수정하세요..."
                    />
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                      <button
                        className="btn btn-primary"
                        onClick={saveEditedAnswer}
                        disabled={!editedAnswer.trim()}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                      >
                        💾 저장
                      </button>
                      <button
                        className="btn btn-secondary"
                        onClick={exitEditMode}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                      >
                        ❌ 취소
                      </button>
                      <button
                        className="btn btn-secondary"
                        onClick={regenerateResponse}
                        style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                      >
                        🔄 재생성
                      </button>
                      {editHistory.length > 0 && (
                        <button
                          className="btn btn-secondary"
                          onClick={revertToOriginal}
                          style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                        >
                          ↩️ 원본 복원
                        </button>
                      )}
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="response-text">{response.answer}</div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                      <button
                        className="btn btn-secondary copy-btn"
                        onClick={() => copyToClipboard(response.answer)}
                      >
                        📋 복사하기
                      </button>
                      <button
                        className="btn btn-secondary copy-btn"
                        onClick={enterEditMode}
                      >
                        ✏️ 수정하기
                      </button>
                      <button
                        className="btn btn-secondary copy-btn"
                        onClick={regenerateResponse}
                      >
                        🔄 재생성
                      </button>
                    </div>
                  </>
                )}
              </div>

              {/* Timing Recommendation */}
              {response.timing_recommendation && (
                <div style={{
                  background: 'linear-gradient(135deg, #3b82f615 0%, #3b82f605 100%)',
                  borderRadius: '12px',
                  padding: '1rem',
                  marginTop: '1rem',
                  border: '1px solid #3b82f630',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '1.5rem' }}>⏱️</span>
                    <div>
                      <div style={{ fontWeight: '700', fontSize: '1rem' }}>
                        답장 타이밍: {response.timing_recommendation.recommended_wait_minutes}분 후
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        자연스러운 범위: {response.timing_recommendation.natural_range}
                      </div>
                    </div>
                  </div>
                  <div style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-light)',
                    background: 'rgba(0,0,0,0.2)',
                    padding: '0.6rem 0.8rem',
                    borderRadius: '8px',
                  }}>
                    {response.timing_recommendation.reason}
                  </div>
                </div>
              )}

              {/* Context Info */}
              {response.context_used > 0 && (
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginTop: '1rem',
                  padding: '0.4rem 0.8rem',
                  background: 'rgba(34, 197, 94, 0.15)',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  color: '#22c55e',
                }}>
                  🧠 최근 {response.context_used}개 대화 맥락 활용
                </div>
              )}

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

      {/* Mobile Settings Bar - Fixed at Bottom */}
      {personas.length > 0 && (
        <div className="mobile-settings-bar">
          <button
            className={`mobile-setting-toggle ${autoFetchContext ? 'active' : ''}`}
            onClick={() => setAutoFetchContext(!autoFetchContext)}
          >
            🧠 맥락 {autoFetchContext ? 'ON' : 'OFF'}
          </button>
          <button
            className={`mobile-setting-toggle ${includeTiming ? 'active' : ''}`}
            onClick={() => setIncludeTiming(!includeTiming)}
          >
            ⏱️ 타이밍 {includeTiming ? 'ON' : 'OFF'}
          </button>
          {autoFetchContext && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.4rem 0.6rem',
              background: 'rgba(255,255,255,0.05)',
              borderRadius: '12px',
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
            }}>
              <span>{contextWindowSize}</span>
              <input
                type="range"
                min="5"
                max="20"
                value={contextWindowSize}
                onChange={(e) => setContextWindowSize(parseInt(e.target.value))}
                style={{ width: '50px', height: '4px' }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AutoMode
