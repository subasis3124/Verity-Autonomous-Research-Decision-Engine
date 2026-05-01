import { NavLink, useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('verity_token');

  const handleLogout = () => {
    localStorage.removeItem('verity_token');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        <span className="brand-icon">⚡</span>
        Verity
      </NavLink>

      <div className="navbar-links">
        {isLoggedIn ? (
          <>
            <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>
              📊 Dashboard
            </NavLink>
            <NavLink to="/submit" className={({ isActive }) => isActive ? 'active' : ''}>
              ✨ New Query
            </NavLink>
            <button onClick={handleLogout} className="btn-logout">
              ↪ Logout
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login" className={({ isActive }) => isActive ? 'active' : ''}>
              Login
            </NavLink>
            <NavLink to="/register" className={({ isActive }) => isActive ? 'active' : ''}>
              Register
            </NavLink>
          </>
        )}
      </div>
    </nav>
  );
}
