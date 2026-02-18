import { useState, useRef } from 'react'
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

  // Tone-based announcement state
  const [toneFile, setToneFile] = useState(null)
  const [toneMyName, setToneMyName] = useState('나')
  const [toneAnalysis, setToneAnalysis] = useState(null)
  const [toneAnnouncement, setToneAnnouncement] = useState('')
  const [toneGroupName, setToneGroupName] = useState('')
  const [toneResponse, setToneResponse] = useState(null)
  const [toneAnalyzing, setToneAnalyzing] = useState(false)
  const [toneGenerating, setToneGenerating] = useState(false)
  const toneFileRef = useRef(null)

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

  // Tone analysis handlers
  const handleToneFileSelect = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setToneFile(file)
    setToneAnalysis(null)
    setToneResponse(null)
    setError('')

    try {
      setToneAnalyzing(true)
      const res = await alibiAPI.analyzeTone(file, toneMyName)
      setToneAnalysis(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '톤 분석에 실패했습니다')
    } finally {
      setToneAnalyzing(false)
    }
  }

  const handleToneAnnounce = async (e) => {
    e.preventDefault()
    setError('')
    setToneResponse(null)

    if (!toneAnalysis) {
      setError('먼저 채팅 파일을 업로드하여 톤을 분석해주세요')
      return
    }

    try {
      setToneGenerating(true)
      const res = await alibiAPI.announceWithTone({
        user_id: 'user',
        announcement: toneAnnouncement,
        tone_analysis: toneAnalysis,
        group_name: toneGroupName,
      })
      setToneResponse(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || '공지 생성에 실패했습니다')
    } finally {
      setToneGenerating(false)
    }
  }

  const resetToneAnalysis = () => {
    setToneFile(null)
    setToneAnalysis(null)
    setToneResponse(null)
    if (toneFileRef.current) toneFileRef.current.value = ''
  }

  return (
    <div className="page">
      <h1 className="page-title">🎭 Alibi Mode</h1>
      <p className="page-subtitle">그룹별 공지 생성 & 알리바이 이미지 생성</p>

      {/* Tab Buttons */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button
          className={`btn ${activeTab === 'announce' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('announce')}
        >
          📢 1:N 공지
        </button>
        <button
          className={`btn ${activeTab === 'tone' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('tone')}
        >
          🎯 톤 맞춤 공지
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

      {/* Tone-based Announcement Tab */}
      {activeTab === 'tone' && (
        <>
          <div className="card">
            <h3 className="card-title">🎯 톤 맞춤 공지 생성</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
              채팅 파일을 분석하여 해당 톡방의 톤에 맞는 공지를 생성해요
            </p>

            {/* File Upload Section */}
            <div className="form-group">
              <label className="form-label">1. 카카오톡 채팅 파일 업로드</label>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                공지를 보낼 채팅방의 대화 내보내기 파일을 업로드하세요
              </p>

              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="대화방에서 나의 이름"
                  value={toneMyName}
                  onChange={(e) => setToneMyName(e.target.value)}
                  style={{ width: '150px' }}
                />
              </div>

              <input
                ref={toneFileRef}
                type="file"
                accept=".txt"
                onChange={handleToneFileSelect}
                style={{
                  width: '100%',
                  padding: '1rem',
                  background: 'rgba(0,0,0,0.3)',
                  border: '2px dashed rgba(255,255,255,0.2)',
                  borderRadius: '8px',
                  color: 'var(--text-light)',
                  cursor: 'pointer',
                }}
              />
            </div>

            {/* Analysis Loading */}
            {toneAnalyzing && (
              <div className="loading" style={{ padding: '1.5rem' }}>
                <div className="spinner"></div>
                <span>톤을 분석하고 있어요...</span>
              </div>
            )}

            {/* Analysis Result */}
            {toneAnalysis && (
              <div style={{
                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%)',
                borderRadius: '12px',
                padding: '1rem',
                marginBottom: '1.25rem',
                border: '1px solid rgba(34, 197, 94, 0.3)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h4 style={{ margin: 0, color: '#22c55e' }}>✅ 톤 분석 완료</h4>
                  <button
                    className="btn btn-secondary"
                    onClick={resetToneAnalysis}
                    style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
                  >
                    다시 분석
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>격식 수준</span>
                    <div style={{ fontWeight: '600' }}>{toneAnalysis.formality_level}</div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>이모지 사용</span>
                    <div style={{ fontWeight: '600' }}>{toneAnalysis.emoji_usage}</div>
                  </div>
                </div>

                {toneAnalysis.common_expressions?.length > 0 && (
                  <div style={{ marginTop: '0.75rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>자주 쓰는 표현</span>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
                      {toneAnalysis.common_expressions.map((expr, i) => (
                        <span key={i} style={{
                          background: 'rgba(255,255,255,0.1)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '8px',
                          fontSize: '0.8rem',
                        }}>
                          {expr}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {toneAnalysis.sentence_endings?.length > 0 && (
                  <div style={{ marginTop: '0.75rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>문장 끝맺음</span>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
                      {toneAnalysis.sentence_endings.map((ending, i) => (
                        <span key={i} style={{
                          background: 'rgba(254, 229, 0, 0.2)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '8px',
                          fontSize: '0.8rem',
                          color: 'var(--primary)',
                        }}>
                          {ending}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{
                  marginTop: '0.75rem',
                  padding: '0.6rem 0.8rem',
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                }}>
                  <strong>추천 스타일:</strong> {toneAnalysis.recommended_style}
                </div>
              </div>
            )}

            {/* Announcement Form (only show if analysis is done) */}
            {toneAnalysis && (
              <form onSubmit={handleToneAnnounce}>
                <div className="form-group">
                  <label className="form-label">2. 그룹/채팅방 이름 (선택)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="예: 동아리 단톡방, 프로젝트팀"
                    value={toneGroupName}
                    onChange={(e) => setToneGroupName(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">3. 공지 내용</label>
                  <textarea
                    className="form-textarea"
                    placeholder="예: 이번 주 토요일 모임이 취소되었습니다"
                    value={toneAnnouncement}
                    onChange={(e) => setToneAnnouncement(e.target.value)}
                    required
                  />
                </div>

                {error && (
                  <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>
                )}

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={toneGenerating}
                >
                  {toneGenerating ? '생성 중...' : '톤 맞춤 공지 생성'}
                </button>
              </form>
            )}
          </div>

          {/* Loading */}
          {toneGenerating && (
            <div className="card">
              <div className="loading">
                <div className="spinner"></div>
                <span>톤에 맞는 공지를 생성하고 있어요...</span>
              </div>
            </div>
          )}

          {/* Result */}
          {toneResponse && (
            <div className="card">
              <h3 className="card-title">✅ 생성된 공지</h3>

              <div className="group-message">
                <div className="group-header">
                  <span className="group-name">
                    {toneResponse.group_name || '톤 맞춤 공지'}
                  </span>
                  <span className="group-tone">
                    {toneResponse.tone_analysis_summary?.formality} / {toneResponse.tone_analysis_summary?.emoji_usage}
                  </span>
                </div>
                <div className="group-text" style={{ fontSize: '1.05rem', lineHeight: '1.7' }}>
                  {toneResponse.generated_message}
                </div>
                <button
                  className="btn btn-secondary copy-btn"
                  onClick={() => copyToClipboard(toneResponse.generated_message)}
                >
                  📋 복사하기
                </button>
              </div>

              {toneResponse.style_notes && (
                <div style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  <strong>적용된 스타일:</strong> {toneResponse.style_notes}
                </div>
              )}

              {toneResponse.alternative_version && (
                <div style={{ marginTop: '1rem' }}>
                  <h4 style={{ marginBottom: '0.5rem', color: 'var(--text-muted)' }}>다른 버전</h4>
                  <div className="group-message">
                    <div className="group-text">{toneResponse.alternative_version}</div>
                    <button
                      className="btn btn-secondary copy-btn"
                      onClick={() => copyToClipboard(toneResponse.alternative_version)}
                    >
                      📋 복사
                    </button>
                  </div>
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
