import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-indigo-700 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">

        <div className="flex items-center gap-6">
          <Link to="/" className="text-xl font-bold tracking-tight">
            CMS
          </Link>
          <Link to="/courses" className="text-sm hover:text-indigo-200 transition">
            Courses
          </Link>
          <Link to="/reports" className="text-sm hover:text-indigo-200 transition">
            Reports
          </Link>
          {user?.role === 'admin' && (
            <Link to="/admin" className="text-sm hover:text-indigo-200 transition">
              Admin
            </Link>
          )}
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-indigo-200">
            {user?.name} &middot;
            <span className="ml-1 capitalize font-medium text-white">{user?.role}</span>
          </span>
          <button
            onClick={handleLogout}
            className="text-sm bg-indigo-800 hover:bg-indigo-900 px-3 py-1 rounded transition"
          >
            Logout
          </button>
        </div>

      </div>
    </nav>
  )
}
