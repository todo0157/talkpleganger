import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import Home from './pages/Home'
import PersonaPage from './pages/PersonaPage'
import AutoMode from './pages/AutoMode'
import AssistMode from './pages/AssistMode'
import AlibiMode from './pages/AlibiMode'
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
            <NavLink to="/alibi">Alibi</NavLink>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/persona" element={<PersonaPage />} />
            <Route path="/auto" element={<AutoMode />} />
            <Route path="/assist" element={<AssistMode />} />
            <Route path="/alibi" element={<AlibiMode />} />
          </Routes>
        </main>

        {/* Mobile Bottom Navigation */}
        <nav className="mobile-nav">
          <NavLink to="/" end>
            <span>🏠</span>
            <span>홈</span>
          </NavLink>
          <NavLink to="/persona">
            <span>👤</span>
            <span>페르소나</span>
          </NavLink>
          <NavLink to="/auto">
            <span>🤖</span>
            <span>Auto</span>
          </NavLink>
          <NavLink to="/assist">
            <span>💡</span>
            <span>Assist</span>
          </NavLink>
          <NavLink to="/alibi">
            <span>📢</span>
            <span>Alibi</span>
          </NavLink>
        </nav>
      </div>
    </Router>
  )
}

export default App
