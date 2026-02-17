import { useState, useEffect } from 'react'
import { reactionAPI } from '../api'

const EMOTIONS = [
  { id: 'happy', label: '기쁨', emoji: '😊', color: '#22c55e' },
  { id: 'sad', label: '슬픔', emoji: '😢', color: '#3b82f6' },
  { id: 'angry', label: '화남', emoji: '😠', color: '#ef4444' },
  { id: 'surprised', label: '놀람', emoji: '😲', color: '#f59e0b' },
  { id: 'love', label: '사랑', emoji: '😍', color: '#ec4899' },
  { id: 'tired', label: '피곤', emoji: '😴', color: '#6b7280' },
  { id: 'confused', label: '혼란', emoji: '😕', color: '#8b5cf6' },
  { id: 'excited', label: '흥분', emoji: '🤩', color: '#f97316' },
  { id: 'grateful', label: '감사', emoji: '🙏', color: '#14b8a6' },
  { id: 'apologetic', label: '미안함', emoji: '😔', color: '#6366f1' },
]

const STYLES = [
  { id: 'cute_character', label: '귀여운 캐릭터', description: '카와이/치비 스타일', icon: '🐱' },
  { id: 'emoji_art', label: '이모지 아트', description: '큰 이모지 스타일', icon: '😀' },
  { id: 'sticker', label: '스티커', description: '메신저 스티커', icon: '🏷️' },
  { id: 'meme', label: '밈 스타일', description: '인터넷 밈', icon: '🖼️' },
  { id: 'minimal', label: '미니멀', description: '심플 라인 아트', icon: '✏️' },
]

function ReactionImagePage() {
  const [selectedEmotion, setSelectedEmotion] = useState('happy')
  const [selectedStyle, setSelectedStyle] = useState('cute_character')
  const [messageContext, setMessageContext] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])

  const handleGenerate = async () => {
    setError('')

    try {
      setLoading(true)
      const res = await reactionAPI.generate({
        user_id: 'reaction_user',
        emotion: selectedEmotion,
        style: selectedStyle,
        message_context: messageContext || null,
      })
      setResponse(res.data)

      // Add to history
      setHistory((prev) => [
        { ...res.data, timestamp: new Date().toLocaleTimeString() },
        ...prev.slice(0, 9), // Keep last 10
      ])
    } catch (err) {
      setError(err.response?.data?.detail || '이미지 생성에 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const downloadImage = async (url) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `reaction_${selectedEmotion}_${Date.now()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch (err) {
      // Fallback: open in new tab
      window.open(url, '_blank')
    }
  }

  const getSelectedEmotionInfo = () => {
    return EMOTIONS.find((e) => e.id === selectedEmotion)
  }

  return (
    <div className="page">
      <h1 className="page-title">🎨 이미지 답장</h1>
      <p className="page-subtitle">감정에 맞는 리액션 이미지를 생성해요</p>

      <div className="card">
        <h3 className="card-title">😊 감정 선택</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
          gap: '0.75rem',
        }}>
          {EMOTIONS.map((emotion) => (
            <button
              key={emotion.id}
              onClick={() => setSelectedEmotion(emotion.id)}
              style={{
                padding: '1rem 0.5rem',
                borderRadius: '12px',
                border: selectedEmotion === emotion.id
                  ? `2px solid ${emotion.color}`
                  : '2px solid transparent',
                background: selectedEmotion === emotion.id
                  ? `${emotion.color}20`
                  : 'rgba(255,255,255,0.05)',
                color: 'var(--text-light)',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.5rem',
                transition: 'all 0.2s',
              }}
            >
              <span style={{ fontSize: '2rem' }}>{emotion.emoji}</span>
              <span style={{ fontSize: '0.85rem', fontWeight: '500' }}>{emotion.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">🎭 스타일 선택</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {STYLES.map((style) => (
            <button
              key={style.id}
              onClick={() => setSelectedStyle(style.id)}
              style={{
                padding: '1rem',
                borderRadius: '12px',
                border: selectedStyle === style.id
                  ? '2px solid var(--primary)'
                  : '2px solid transparent',
                background: selectedStyle === style.id
                  ? 'rgba(59, 130, 246, 0.15)'
                  : 'rgba(255,255,255,0.05)',
                color: 'var(--text-light)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                textAlign: 'left',
                transition: 'all 0.2s',
              }}
            >
              <span style={{ fontSize: '1.5rem' }}>{style.icon}</span>
              <div>
                <div style={{ fontWeight: '600' }}>{style.label}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {style.description}
                </div>
              </div>
              {selectedStyle === style.id && (
                <span style={{ marginLeft: 'auto', color: 'var(--primary)' }}>✓</span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">💬 맥락 (선택)</h3>
        <input
          type="text"
          className="form-input"
          placeholder="예: 생일 축하받았을 때, 시험 끝났을 때..."
          value={messageContext}
          onChange={(e) => setMessageContext(e.target.value)}
        />
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          맥락을 입력하면 더 상황에 맞는 이미지가 생성돼요
        </p>
      </div>

      {error && (
        <div className="card" style={{ borderColor: 'var(--danger)' }}>
          <p style={{ color: 'var(--danger)', margin: 0 }}>{error}</p>
        </div>
      )}

      <button
        className="btn btn-primary"
        onClick={handleGenerate}
        disabled={loading}
        style={{ width: '100%', marginBottom: '1.5rem' }}
      >
        {loading ? (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
            <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
            이미지 생성 중...
          </span>
        ) : (
          `🎨 ${getSelectedEmotionInfo()?.emoji} ${getSelectedEmotionInfo()?.label} 이미지 생성하기`
        )}
      </button>

      {response && (
        <div className="card">
          <h3 className="card-title">✅ 생성된 이미지</h3>

          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '1rem',
          }}>
            <img
              src={response.image_url}
              alt={`${response.emotion} reaction`}
              style={{
                maxWidth: '100%',
                maxHeight: '400px',
                borderRadius: '16px',
                boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
              }}
            />
          </div>

          <div style={{
            display: 'flex',
            gap: '0.75rem',
            justifyContent: 'center',
            marginBottom: '1rem',
          }}>
            <button
              className="btn btn-primary"
              onClick={() => downloadImage(response.image_url)}
            >
              💾 다운로드
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => window.open(response.image_url, '_blank')}
            >
              🔗 새 탭에서 열기
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleGenerate}
              disabled={loading}
            >
              🔄 다시 생성
            </button>
          </div>

          <div style={{
            background: 'rgba(255,255,255,0.05)',
            borderRadius: '12px',
            padding: '1rem',
          }}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
              <span style={{
                padding: '0.3rem 0.6rem',
                background: `${getSelectedEmotionInfo()?.color}25`,
                color: getSelectedEmotionInfo()?.color,
                borderRadius: '6px',
                fontSize: '0.8rem',
              }}>
                {getSelectedEmotionInfo()?.emoji} {response.emotion}
              </span>
              <span style={{
                padding: '0.3rem 0.6rem',
                background: 'rgba(59, 130, 246, 0.2)',
                color: '#3b82f6',
                borderRadius: '6px',
                fontSize: '0.8rem',
              }}>
                🎭 {response.style}
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>
              <strong>추천 사용:</strong> {response.suggested_usage}
            </div>
          </div>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="card">
          <h3 className="card-title">📜 최근 생성 기록</h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
            gap: '0.75rem',
          }}>
            {history.map((item, i) => (
              <div
                key={i}
                onClick={() => setResponse(item)}
                style={{
                  cursor: 'pointer',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  border: response?.image_url === item.image_url
                    ? '2px solid var(--primary)'
                    : '2px solid transparent',
                }}
              >
                <img
                  src={item.image_url}
                  alt={item.emotion}
                  style={{
                    width: '100%',
                    aspectRatio: '1',
                    objectFit: 'cover',
                  }}
                />
                <div style={{
                  background: 'rgba(0,0,0,0.6)',
                  padding: '0.25rem',
                  fontSize: '0.7rem',
                  textAlign: 'center',
                }}>
                  {EMOTIONS.find((e) => e.id === item.emotion)?.emoji}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReactionImagePage
