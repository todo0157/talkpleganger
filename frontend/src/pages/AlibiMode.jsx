import { useState } from 'react'
import { alibiAPI } from '../api'

function AlibiMode() {
  const [activeTab, setActiveTab] = useState('announce')

  // Announce state
  const [announcement, setAnnouncement] = useState('')
  const [selectedGroups, setSelectedGroups] = useState(['work', 'friends', 'family'])
  const [announceResponse, setAnnounceResponse] = useState(null)
  const [announceLoading, setAnnounceLoading] = useState(false)

  // Image state
  const [imageSituation, setImageSituation] = useState('')
  const [imageStyle, setImageStyle] = useState('realistic')
  const [imageDetails, setImageDetails] = useState('')
  const [imageResponse, setImageResponse] = useState(null)
  const [imageLoading, setImageLoading] = useState(false)

  const [error, setError] = useState('')

  const groups = [
    { id: 'work', label: '직장 동료', tone: 'formal' },
    { id: 'friends', label: '친구들', tone: 'casual' },
    { id: 'family', label: '가족', tone: 'polite' },
  ]

  const handleAnnounce = async (e) => {
    e.preventDefault()
    setError('')
    setAnnounceResponse(null)

    if (selectedGroups.length === 0) {
      setError('최소 한 개의 그룹을 선택해주세요')
      return
    }

    try {
      setAnnounceLoading(true)
      const res = await alibiAPI.announce({
        user_id: 'user',
        announcement,
        groups: groups
          .filter(g => selectedGroups.includes(g.id))
          .map(g => ({
            group_id: g.id,
            group_name: g.label,
            tone: g.tone,
          })),
      })
      setAnnounceResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '공지 생성에 실패했습니다')
    } finally {
      setAnnounceLoading(false)
    }
  }

  const handleImageGenerate = async (e) => {
    e.preventDefault()
    setError('')
    setImageResponse(null)

    try {
      setImageLoading(true)
      const res = await alibiAPI.generateImage({
        user_id: 'user',
        situation: imageSituation,
        style: imageStyle,
        additional_details: imageDetails || null,
      })
      setImageResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '이미지 생성에 실패했습니다')
    } finally {
      setImageLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('클립보드에 복사되었습니다!')
  }

  const toggleGroup = (groupId) => {
    if (selectedGroups.includes(groupId)) {
      setSelectedGroups(selectedGroups.filter(g => g !== groupId))
    } else {
      setSelectedGroups([...selectedGroups, groupId])
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">🎭 Alibi Mode</h1>
      <p className="page-subtitle">그룹별 공지 생성 & 알리바이 이미지 생성</p>

      {/* Tab Buttons */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <button
          className={`btn ${activeTab === 'announce' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('announce')}
        >
          📢 1:N 공지
        </button>
        <button
          className={`btn ${activeTab === 'image' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('image')}
        >
          🖼️ 알리바이 이미지
        </button>
      </div>

      {/* Announce Tab */}
      {activeTab === 'announce' && (
        <>
          <div className="card">
            <h3 className="card-title">📢 그룹별 공지 생성</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
              하나의 공지를 여러 그룹에 맞는 톤으로 변환해요
            </p>

            <form onSubmit={handleAnnounce}>
              <div className="form-group">
                <label className="form-label">공지 내용</label>
                <textarea
                  className="form-textarea"
                  placeholder="예: 이번 주 토요일 저녁에 약속이 생겨서 참석이 어려울 것 같습니다"
                  value={announcement}
                  onChange={(e) => setAnnouncement(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">대상 그룹 선택</label>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {groups.map((group) => (
                    <button
                      key={group.id}
                      type="button"
                      className={`btn ${selectedGroups.includes(group.id) ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => toggleGroup(group.id)}
                      style={{ padding: '0.5rem 1rem' }}
                    >
                      {group.label}
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>
              )}

              <button
                type="submit"
                className="btn btn-primary"
                disabled={announceLoading}
              >
                {announceLoading ? '생성 중...' : '공지 생성하기'}
              </button>
            </form>
          </div>

          {announceLoading && (
            <div className="card">
              <div className="loading">
                <div className="spinner"></div>
                <span>그룹별 메시지를 생성하고 있어요...</span>
              </div>
            </div>
          )}

          {announceResponse && (
            <div className="card">
              <h3 className="card-title">✅ 생성된 메시지</h3>

              {announceResponse.group_messages?.map((gm, i) => (
                <div key={i} className="group-message">
                  <div className="group-header">
                    <span className="group-name">{gm.group_name}</span>
                    <span className="group-tone">톤: {gm.tone_used}</span>
                  </div>
                  <div className="group-text">{gm.message}</div>
                  <button
                    className="btn btn-secondary copy-btn"
                    onClick={() => copyToClipboard(gm.message)}
                  >
                    📋 복사하기
                  </button>
                </div>
              ))}

              {announceResponse.delivery_order_suggestion?.length > 0 && (
                <div style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>
                  <strong>권장 전송 순서:</strong>{' '}
                  {announceResponse.delivery_order_suggestion.join(' → ')}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Image Tab */}
      {activeTab === 'image' && (
        <>
          <div className="card">
            <h3 className="card-title">🖼️ 알리바이 이미지 생성</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
              DALL-E 3로 상황에 맞는 이미지를 생성해요
            </p>

            <form onSubmit={handleImageGenerate}>
              <div className="form-group">
                <label className="form-label">상황 설명</label>
                <textarea
                  className="form-textarea"
                  placeholder="예: 조용한 카페에서 노트북으로 작업 중인 모습"
                  value={imageSituation}
                  onChange={(e) => setImageSituation(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">이미지 스타일</label>
                <select
                  className="form-select"
                  value={imageStyle}
                  onChange={(e) => setImageStyle(e.target.value)}
                >
                  <option value="realistic">사실적 (Realistic)</option>
                  <option value="artistic">예술적 (Artistic)</option>
                  <option value="minimal">미니멀 (Minimal)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">추가 디테일 (선택)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: 창가 자리, 아메리카노 한 잔, 자연광"
                  value={imageDetails}
                  onChange={(e) => setImageDetails(e.target.value)}
                />
              </div>

              {error && (
                <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>
              )}

              <button
                type="submit"
                className="btn btn-primary"
                disabled={imageLoading}
              >
                {imageLoading ? '생성 중...' : '이미지 생성하기'}
              </button>
            </form>
          </div>

          {imageLoading && (
            <div className="card">
              <div className="loading">
                <div className="spinner"></div>
                <span>DALL-E가 이미지를 생성하고 있어요... (약 10-20초)</span>
              </div>
            </div>
          )}

          {imageResponse && (
            <div className="card">
              <h3 className="card-title">✅ 생성된 이미지</h3>

              <img
                src={imageResponse.image_url}
                alt="Generated alibi"
                className="alibi-image"
              />

              <div style={{ marginTop: '1rem' }}>
                <strong>상황:</strong> {imageResponse.situation}
              </div>

              {imageResponse.usage_tips?.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>사용 팁:</strong>
                  <ul className="tips-list">
                    {imageResponse.usage_tips.map((tip, i) => (
                      <li key={i}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}

              <a
                href={imageResponse.image_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
                style={{ display: 'inline-block', marginTop: '1rem' }}
              >
                🔗 이미지 새 탭에서 열기
              </a>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default AlibiMode
