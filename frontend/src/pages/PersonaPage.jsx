import { useState, useEffect, useRef } from 'react'
import { personaAPI } from '../api'

function PersonaPage() {
  const [personas, setPersonas] = useState([])
  const [loading, setLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  const [inputMode, setInputMode] = useState('file') // 'manual' or 'file'
  const fileInputRef = useRef(null)

  // Manual form state
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    chat_examples: [
      { role: 'other', content: '' },
      { role: 'user', content: '' },
      { role: 'other', content: '' },
      { role: 'user', content: '' },
    ],
  })

  // File upload state
  const [fileData, setFileData] = useState({
    user_id: '',
    name: '',
    my_name: '나',
    target_person: '', // For group chat: specific person to focus on
    file: null,
  })
  const [parsedPreview, setParsedPreview] = useState(null)
  const [detectedNames, setDetectedNames] = useState([])
  const [isGroupChat, setIsGroupChat] = useState(false)
  const [participants, setParticipants] = useState({})

  useEffect(() => {
    loadPersonas()
  }, [])

  const loadPersonas = async () => {
    try {
      setLoading(true)
      const res = await personaAPI.list()
      setPersonas(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Manual submission
  const handleManualSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const validExamples = formData.chat_examples.filter(ex => ex.content.trim())
    if (validExamples.length < 3) {
      setError('최소 3개의 대화 예시를 입력해주세요')
      return
    }

    try {
      setCreating(true)
      await personaAPI.create({
        ...formData,
        chat_examples: validExamples,
      })
      await loadPersonas()
      setFormData({
        user_id: '',
        name: '',
        chat_examples: [
          { role: 'other', content: '' },
          { role: 'user', content: '' },
          { role: 'other', content: '' },
          { role: 'user', content: '' },
        ],
      })
    } catch (err) {
      setError(err.response?.data?.detail || '페르소나 생성에 실패했습니다')
    } finally {
      setCreating(false)
    }
  }

  // File upload handling
  const handleFileSelect = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setFileData({ ...fileData, file })
    setError('')
    setParsedPreview(null)
    setIsGroupChat(false)
    setParticipants({})

    try {
      const res = await personaAPI.parseKakao(file, fileData.my_name)
      setParsedPreview(res.data)
      setDetectedNames(res.data.detected_names || [])
      setIsGroupChat(res.data.is_group_chat || false)
      setParticipants(res.data.participants || {})
    } catch (err) {
      setError(err.response?.data?.detail || '파일 파싱에 실패했습니다')
    }
  }

  const handleFileSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!fileData.file) {
      setError('카카오톡 대화 파일을 선택해주세요')
      return
    }

    try {
      setCreating(true)
      await personaAPI.createFromKakao(
        fileData.file,
        fileData.user_id,
        fileData.name,
        fileData.my_name
      )
      await loadPersonas()
      setFileData({ user_id: '', name: '', my_name: '나', target_person: '', file: null })
      setParsedPreview(null)
      setIsGroupChat(false)
      setParticipants({})
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setError(err.response?.data?.detail || '페르소나 생성에 실패했습니다')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (userId) => {
    if (!confirm('정말 삭제하시겠습니까?')) return
    try {
      await personaAPI.delete(userId)
      await loadPersonas()
    } catch (err) {
      alert('삭제 실패')
    }
  }

  const updateChatExample = (index, field, value) => {
    const newExamples = [...formData.chat_examples]
    newExamples[index] = { ...newExamples[index], [field]: value }
    setFormData({ ...formData, chat_examples: newExamples })
  }

  const addChatExample = () => {
    setFormData({
      ...formData,
      chat_examples: [
        ...formData.chat_examples,
        { role: 'other', content: '' },
        { role: 'user', content: '' },
      ],
    })
  }

  return (
    <div className="page">
      <h1 className="page-title">페르소나 설정</h1>
      <p className="page-subtitle">내 말투를 AI에게 학습시켜요</p>

      {/* Create Form */}
      <div className="card">
        <h3 className="card-title">✨ 새 페르소나 만들기</h3>

        {/* Input Mode Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <button
            type="button"
            className={`btn ${inputMode === 'file' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setInputMode('file')}
          >
            📁 카톡 파일 업로드
          </button>
          <button
            type="button"
            className={`btn ${inputMode === 'manual' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setInputMode('manual')}
          >
            ✏️ 직접 입력
          </button>
        </div>

        {/* File Upload Mode */}
        {inputMode === 'file' && (
          <form onSubmit={handleFileSubmit}>
            <div className="card" style={{ background: 'rgba(254, 229, 0, 0.1)', border: '1px dashed var(--primary)' }}>
              <h4 style={{ marginBottom: '0.75rem' }}>📱 카카오톡 대화 내보내기 방법</h4>
              <ol style={{ paddingLeft: '1.5rem', color: 'var(--text-muted)', lineHeight: '1.8', fontSize: '0.9rem' }}>
                <li>카카오톡 대화방 열기</li>
                <li>우측 상단 <strong>≡</strong> 메뉴 클릭</li>
                <li><strong>대화 내보내기</strong> 선택</li>
                <li><strong>텍스트로 저장</strong> 선택</li>
              </ol>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
              <div className="form-group">
                <label className="form-label">사용자 ID</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: user_123"
                  value={fileData.user_id}
                  onChange={(e) => setFileData({ ...fileData, user_id: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">이름</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: 홍길동"
                  value={fileData.name}
                  onChange={(e) => setFileData({ ...fileData, name: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">대화방에서 나의 이름</label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['나', ...detectedNames].map((name) => (
                  <button
                    key={name}
                    type="button"
                    className={`btn ${fileData.my_name === name ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '0.4rem 0.8rem', fontSize: '0.9rem' }}
                    onClick={() => setFileData({ ...fileData, my_name: name })}
                  >
                    {name}
                  </button>
                ))}
                <input
                  type="text"
                  className="form-input"
                  style={{ width: '150px' }}
                  placeholder="직접 입력"
                  value={!['나', ...detectedNames].includes(fileData.my_name) ? fileData.my_name : ''}
                  onChange={(e) => setFileData({ ...fileData, my_name: e.target.value })}
                />
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                카카오톡에서 표시되는 내 이름을 선택하세요
              </p>
            </div>

            <div className="form-group">
              <label className="form-label">카카오톡 대화 파일 (.txt)</label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt"
                onChange={handleFileSelect}
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

            {/* Preview */}
            {parsedPreview && (
              <div className="response-box" style={{ marginBottom: '1rem' }}>
                <div className="response-header">
                  <span className="response-label">파싱 결과 미리보기</span>
                  <span className="confidence-badge confidence-high">
                    {parsedPreview.total_messages}개 메시지
                  </span>
                  {isGroupChat && (
                    <span className="confidence-badge confidence-medium" style={{ marginLeft: '0.5rem' }}>
                      👥 그룹채팅 ({Object.keys(participants).length}명)
                    </span>
                  )}
                </div>

                {/* Group Chat Participants */}
                {isGroupChat && Object.keys(participants).length > 0 && (
                  <div style={{
                    background: 'rgba(254, 229, 0, 0.1)',
                    borderRadius: '8px',
                    padding: '0.75rem',
                    marginTop: '0.75rem',
                    marginBottom: '0.75rem'
                  }}>
                    <p style={{ fontSize: '0.9rem', marginBottom: '0.5rem', fontWeight: '500' }}>
                      👥 참여자 목록
                    </p>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      {Object.entries(participants).map(([name, count]) => (
                        <button
                          key={name}
                          type="button"
                          className={`btn ${fileData.target_person === name ? 'btn-primary' : 'btn-secondary'}`}
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.85rem' }}
                          onClick={() => setFileData({
                            ...fileData,
                            target_person: fileData.target_person === name ? '' : name
                          })}
                        >
                          {name} ({count})
                        </button>
                      ))}
                    </div>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                      {fileData.target_person
                        ? `"${fileData.target_person}"님과의 대화만 학습합니다`
                        : '특정 상대를 선택하면 그 사람과의 대화만 학습합니다'}
                    </p>
                  </div>
                )}

                <div style={{ maxHeight: '200px', overflowY: 'auto', marginTop: '0.5rem' }}>
                  {parsedPreview.chat_examples?.slice(0, 10).map((ex, i) => (
                    <div key={i} className="chat-example" style={{ marginBottom: '0.25rem' }}>
                      <span
                        className="chat-role"
                        style={{
                          background: ex.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.2)',
                          color: ex.role === 'user' ? 'var(--secondary)' : 'var(--text-light)',
                        }}
                      >
                        {ex.role === 'user' ? '나' : '상대'}
                      </span>
                      <span className="chat-content">{ex.content}</span>
                    </div>
                  ))}
                  {parsedPreview.chat_examples?.length > 10 && (
                    <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '0.5rem' }}>
                      ... 외 {parsedPreview.chat_examples.length - 10}개 더
                    </p>
                  )}
                </div>
              </div>
            )}

            {error && (
              <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={creating || !parsedPreview}
            >
              {creating ? '생성 중...' : '페르소나 생성'}
            </button>
          </form>
        )}

        {/* Manual Input Mode */}
        {inputMode === 'manual' && (
          <form onSubmit={handleManualSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">사용자 ID</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: user_123"
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">이름</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="예: 홍길동"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">대화 예시 (최소 3개)</label>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                실제 카카오톡 대화처럼 입력해주세요. AI가 말투를 학습합니다.
              </p>

              <div className="chat-examples">
                {formData.chat_examples.map((example, index) => (
                  <div key={index} className="chat-example">
                    <select
                      className="chat-role"
                      value={example.role}
                      onChange={(e) => updateChatExample(index, 'role', e.target.value)}
                      style={{
                        background: example.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.2)',
                        color: example.role === 'user' ? 'var(--secondary)' : 'var(--text-light)',
                        border: 'none',
                        cursor: 'pointer',
                      }}
                    >
                      <option value="other">상대</option>
                      <option value="user">나</option>
                    </select>
                    <input
                      type="text"
                      className="form-input"
                      placeholder={example.role === 'user' ? '내가 보낸 메시지...' : '상대방이 보낸 메시지...'}
                      value={example.content}
                      onChange={(e) => updateChatExample(index, 'content', e.target.value)}
                    />
                  </div>
                ))}
              </div>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={addChatExample}
                style={{ marginTop: '0.5rem' }}
              >
                + 대화 추가
              </button>
            </div>

            {error && (
              <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={creating}
            >
              {creating ? '생성 중...' : '페르소나 생성'}
            </button>
          </form>
        )}
      </div>

      {/* Persona List */}
      <div className="card">
        <h3 className="card-title">📋 등록된 페르소나</h3>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <span>불러오는 중...</span>
          </div>
        ) : personas.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
            등록된 페르소나가 없습니다
          </p>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {personas.map((persona) => (
              <div
                key={persona.user_id}
                style={{
                  background: 'rgba(0,0,0,0.2)',
                  borderRadius: '12px',
                  padding: '1rem',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h4 style={{ marginBottom: '0.5rem' }}>
                      {persona.name}
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginLeft: '0.5rem' }}>
                        ({persona.user_id})
                      </span>
                    </h4>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span className="confidence-badge confidence-high">톤: {persona.tone}</span>
                      <span className="confidence-badge confidence-medium">높임말: {persona.honorific_level}</span>
                      <span className="confidence-badge confidence-low">이모지: {persona.emoji_usage}</span>
                    </div>
                  </div>
                  <button
                    className="btn btn-danger"
                    style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                    onClick={() => handleDelete(persona.user_id)}
                  >
                    삭제
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default PersonaPage
