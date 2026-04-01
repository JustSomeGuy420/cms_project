import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getCoursesForStudent, getCoursesForLecturer, getCourses } from '../api'

export default function Dashboard() {
  const { user } = useAuth()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetch = async () => {
      try {
        if (user.role === 'student') {
          const { data } = await getCoursesForStudent(user.acc_id)
          setCourses(data)
        } else if (user.role === 'lecturer') {
          const { data } = await getCoursesForLecturer(user.acc_id)
          setCourses(data)
        } else {
          const { data } = await getCourses()
          setCourses(data.slice(0, 6))
        }
      } catch (_) {}
      setLoading(false)
    }
    fetch()
  }, [user])

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back 👋
        </h1>
        <p className="text-gray-500 mt-1 capitalize">
          Logged in as <span className="font-medium text-indigo-600">{user.role}</span>
        </p>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
        <Link to="/courses" className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition text-center">
          <div className="text-2xl mb-1">📚</div>
          <div className="text-sm font-medium text-gray-700">All Courses</div>
        </Link>
        <Link to="/reports" className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition text-center">
          <div className="text-2xl mb-1">📊</div>
          <div className="text-sm font-medium text-gray-700">Reports</div>
        </Link>
        {user.role === 'admin' && (
          <Link to="/admin" className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition text-center">
            <div className="text-2xl mb-1">⚙️</div>
            <div className="text-sm font-medium text-gray-700">Admin Panel</div>
          </Link>
        )}
      </div>

      {/* My courses */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          {user.role === 'admin' ? 'All Courses' : 'My Courses'}
        </h2>

        {loading ? (
          <p className="text-gray-400 text-sm">Loading…</p>
        ) : courses.length === 0 ? (
          <p className="text-gray-400 text-sm">No courses yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map(c => (
              <Link
                key={c.course_code}
                to={`/courses/${c.course_code}`}
                className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md hover:border-indigo-300 transition"
              >
                <div className="text-xs font-mono text-indigo-500 mb-1">{c.course_code}</div>
                <div className="font-semibold text-gray-800">{c.course_name}</div>
                <div className="text-sm text-gray-500 mt-1 line-clamp-2">{c.description}</div>
                {c.grade != null && (
                  <div className="mt-2 text-sm font-medium text-green-600">Grade: {c.grade}%</div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
