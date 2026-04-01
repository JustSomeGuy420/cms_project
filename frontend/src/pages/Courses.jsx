import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCourses } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Courses() {
  const { user } = useAuth()
  const [courses, setCourses]   = useState([])
  const [filtered, setFiltered] = useState([])
  const [search, setSearch]     = useState('')
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    getCourses()
      .then(({ data }) => { setCourses(data); setFiltered(data) })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const q = search.toLowerCase()
    setFiltered(courses.filter(c =>
      c.course_code.toLowerCase().includes(q) ||
      c.course_name.toLowerCase().includes(q)
    ))
  }, [search, courses])

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Courses</h1>
          <p className="text-gray-500 text-sm">{courses.length} courses available</p>
        </div>
        {user.role === 'admin' && (
          <Link to="/admin" className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded transition">
            + New Course
          </Link>
        )}
      </div>

      <input
        type="text"
        placeholder="Search by code or name…"
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="w-full border border-gray-300 rounded px-4 py-2 text-sm mb-6 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      {loading ? (
        <p className="text-gray-400 text-sm">Loading courses…</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(c => (
            <Link
              key={c.course_code}
              to={`/courses/${c.course_code}`}
              className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md hover:border-indigo-300 transition"
            >
              <div className="text-xs font-mono text-indigo-500 mb-1">{c.course_code}</div>
              <div className="font-semibold text-gray-800">{c.course_name}</div>
              <div className="text-sm text-gray-500 mt-1 line-clamp-2">{c.description}</div>
            </Link>
          ))}
          {filtered.length === 0 && (
            <p className="text-gray-400 text-sm col-span-3">No courses match your search.</p>
          )}
        </div>
      )}
    </div>
  )
}
