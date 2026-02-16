import { useState, useEffect } from 'react'
import { assistAPI, personaAPI } from '../api'

function AssistMode() {
  const [personas, setPersonas] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [formData, setFormData] = useState({
    relationship: 'boss',
    age_group: '40s',
    personality: '',
    situation: '',
    goal: '',
  })
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const relationships = [
    { value: 'boss', label: '상사' },
    { value: 'colleague', label: '동료' },
    { value: 'client', label: '고객/클라이언트' },
    { value: 'professor', label: '교수님' },
    { value: 'parent', label: '부모님' },
    { value: 'friend', label: '친구' },
    { value: 'partner', label: '연인' },
    { value: 'acquaintance', label: '지인' },
  ]

  const ageGroups = ['20s', '30s', '40s', '50s', '60s+']

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

    try {
      setLoading(true)
      const res = await assistAPI.suggest({
        user_id: selectedPersona || 'guest',
        recipient: {
          relationship: formData.relationship,
          age_group: formData.age_group,
          personality: formData.personality || null,
        },
        situation: formData.situation,
        goal: formData.goal,
        variation_styles: ['polite', 'logical', 'soft'],
      })
      setResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '멘트 생성에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('클립보드에 복사되었습니다!')
  }

  const getStyleLabel = (style) => {
    const labels = {
      polite: '공손한 버전',
      logical: '논리적인 버전',
      soft: '부드러운 버전',
      humorous: '유머러스한 버전',
    }
    return labels[style] || style
  }

  return (
    <div className="page">
      <h1 className="page-title">💡 Assist Mode</h1>
      <p className="page-subtitle">상사, 교수님께 보낼 완벽한 멘트를 추천받아요</p>

      <div className="card">
        <h3 className="card-title">📝 상황 입력</h3>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">상대방과의 관계</label>
              <select
                className="form-select"
                value={formData.relationship}
                onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
              >
                {relationships.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">상대방 나이대</label>
              <select
                className="form-select"
                value={formData.age_group}
                onChange={(e) => setFormData({ ...formData, age_group: e.target.value })}
              >
                {ageGroups.map((age) => (
                  <option key={age} value={age}>{age}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">상대방 성격/특징 (선택)</label>
            <input
              type="text"
              className="form-input"
              placeholder="예: 꼼꼼하고 업무 중심적, 유머를 좋아함"
              value={formData.personality}
              onChange={(e) => setFormData({ ...formData, personality: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">현재 상황</label>
            <textarea
              className="form-textarea"
              placeholder="예: 다음 주 금요일에 개인 사유로 휴가를 쓰고 싶은 상황"
              value={formData.situation}
              onChange={(e) => setFormData({ ...formData, situation: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">달성하고 싶은 목표</label>
            <input
              type="text"
              className="form-input"
              placeholder="예: 휴가 승인을 받고 싶습니다"
              value={formData.goal}
              onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
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
            {loading ? '생성 중...' : '멘트 추천받기'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="card">
          <div className="loading">
            <div className="spinner"></div>
            <span>AI가 최적의 멘트를 고민하고 있어요...</span>
          </div>
        </div>
      )}

      {response && (
        <div className="card">
          <h3 className="card-title">✅ 추천 멘트</h3>

          <div className="response-box" style={{ marginBottom: '1.5rem' }}>
            <div className="response-label">상황 분석</div>
            <p style={{ marginTop: '0.5rem' }}>{response.situation_analysis}</p>
          </div>

          <div className="response-box" style={{ marginBottom: '1.5rem' }}>
            <div className="response-label">권장 접근 방식</div>
            <p style={{ marginTop: '0.5rem' }}>{response.recommended_approach}</p>
          </div>

          <h4 style={{ marginBottom: '1rem' }}>메시지 변형</h4>
          <div className="variations-grid">
            {response.variations?.map((variation, i) => (
              <div key={i} className="variation-card">
                <div className="variation-header">
                  <span className="variation-style">{getStyleLabel(variation.style)}</span>
                  <span className={`risk-badge risk-${variation.risk_level}`}>
                    위험도: {variation.risk_level}
                  </span>
                </div>
                <div className="variation-message">{variation.message}</div>
                <div className="variation-tone">{variation.tone_description}</div>
                <button
                  className="btn btn-secondary copy-btn"
                  onClick={() => copyToClipboard(variation.message)}
                >
                  📋 복사하기
                </button>
              </div>
            ))}
          </div>

          {response.tips?.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.75rem' }}>커뮤니케이션 팁</h4>
              <ul className="tips-list">
                {response.tips.map((tip, i) => (
                  <li key={i}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AssistMode
