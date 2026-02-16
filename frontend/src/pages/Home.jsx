import { Link } from 'react-router-dom'

function Home() {
  return (
    <div className="page">
      {/* Hero Section */}
      <div className="home-hero">
        <span className="brand-icon">💬</span>
        <h1>톡플갱어</h1>
        <p>내 말투를 배우는 AI 카카오톡 비서</p>
      </div>

      {/* Feature Cards */}
      <div className="home-grid">
        <Link to="/persona" className="feature-card">
          <div className="feature-icon">👤</div>
          <div className="feature-content">
            <h3 className="feature-title">페르소나 설정</h3>
            <p className="feature-desc">내 말투와 대화 스타일을 AI에게 학습시켜요</p>
          </div>
          <span className="feature-arrow">›</span>
        </Link>

        <Link to="/auto" className="feature-card">
          <div className="feature-icon">🤖</div>
          <div className="feature-content">
            <h3 className="feature-title">Auto Mode</h3>
            <p className="feature-desc">내 말투 그대로 자동 답장을 생성해요</p>
          </div>
          <span className="feature-arrow">›</span>
        </Link>

        <Link to="/assist" className="feature-card">
          <div className="feature-icon">💡</div>
          <div className="feature-content">
            <h3 className="feature-title">Assist Mode</h3>
            <p className="feature-desc">상사, 교수님께 보낼 완벽한 멘트를 추천받아요</p>
          </div>
          <span className="feature-arrow">›</span>
        </Link>

        <Link to="/alibi" className="feature-card">
          <div className="feature-icon">📢</div>
          <div className="feature-content">
            <h3 className="feature-title">Alibi Mode</h3>
            <p className="feature-desc">그룹별 공지 생성 & 알리바이 이미지까지</p>
          </div>
          <span className="feature-arrow">›</span>
        </Link>
      </div>

      {/* Quick Start Guide */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h3 className="card-title">🚀 빠른 시작</h3>
        <ol style={{ paddingLeft: '1.25rem', color: 'var(--text-muted)', lineHeight: '2.2', fontSize: '0.95rem' }}>
          <li><strong style={{ color: 'var(--text-light)' }}>페르소나 설정</strong>에서 카톡 대화를 업로드하세요</li>
          <li>원하는 모드를 선택해서 AI 응답을 생성하세요</li>
          <li>생성된 메시지를 복사해서 카카오톡에 붙여넣기!</li>
        </ol>
      </div>
    </div>
  )
}

export default Home
