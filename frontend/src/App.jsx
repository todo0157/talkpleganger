import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import Home from './pages/Home'
import PersonaPage from './pages/PersonaPage'
import AutoMode from './pages/AutoMode'
import AssistMode from './pages/AssistMode'
import AlibiMode from './pages/AlibiMode'
import HistoryPage from './pages/HistoryPage'
import FollowUpMode from './pages/FollowUpMode'
import ReactionImagePage from './pages/ReactionImagePage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <span className="brand-icon">💬</span>
            <span className="brand-text">톡플갱어</span>
          </div>
          <div className="nav-links">
            <NavLink to="/" end>홈</NavLink>
            <NavLink to="/persona">페르소나</NavLink>
            <NavLink to="/auto">Auto</NavLink>
            <NavLink to="/assist">Assist</NavLink>
            <NavLink to="/followup">읽씹</NavLink>
            <NavLink to="/reaction">이미지</NavLink>
            <NavLink to="/alibi">Alibi</NavLink>
            <NavLink to="/history">히스토리</NavLink>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/persona" element={<PersonaPage />} />
            <Route path="/auto" element={<AutoMode />} />
            <Route path="/assist" element={<AssistMode />} />
            <Route path="/followup" element={<FollowUpMode />} />
            <Route path="/reaction" element={<ReactionImagePage />} />
            <Route path="/alibi" element={<AlibiMode />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </main>

        {/* Mobile Bottom Navigation */}
        <nav className="mobile-nav">
          <NavLink to="/" end>
            <span>🏠</span>
            <span>홈</span>
          </NavLink>
          <NavLink to="/auto">
            <span>🤖</span>
            <span>Auto</span>
          </NavLink>
          <NavLink to="/followup">
            <span>💬</span>
            <span>읽씹</span>
          </NavLink>
          <NavLink to="/reaction">
            <span>🎨</span>
            <span>이미지</span>
          </NavLink>
          <NavLink to="/history">
            <span>📜</span>
            <span>기록</span>
          </NavLink>
        </nav>
      </div>
    </Router>
  )
}

export default App
