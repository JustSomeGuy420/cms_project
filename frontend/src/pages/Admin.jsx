import { useState, useEffect } from 'react'
import { createCourse, assignLecturer, enrollStudent, getCourses } from '../api'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Admin() {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user?.role !== 'admin') navigate('/')
  }, [user])

  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  const flash = (m, isErr) => {
    if (isErr) { setErr(m); setTimeout(() => setErr(''), 4000) }
    else        { setMsg(m); setTimeout(() => setMsg(''), 4000) }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Panel</h1>

      {msg && <div className="bg-green-50 border border-green-200 text-green-700 rounded px-4 py-2 text-sm mb-4">{msg}</div>}
      {err && <div className="bg-red-50 border border-red-200 text-red-700 rounded px-4 py-2 text-sm mb-4">{err}</div>}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">

        <Card title="Create Course">
          <CreateCourseForm onDone={m => flash(m)} onErr={e => flash(e, true)} />
        </Card>

        <Card title="Assign Lecturer to Course">
          <AssignLecturerForm onDone={m => flash(m)} onErr={e => flash(e, true)} />
        </Card>

        <Card title="Enroll Student in Course">
          <EnrollStudentForm onDone={m => flash(m)} onErr={e => flash(e, true)} />
        </Card>

      </div>
    </div>
  )
}

function Card({ title, children }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-5">
      <h2 className="font-semibold text-gray-800 mb-4">{title}</h2>
      {children}
    </div>
  )
}

function CreateCourseForm({ onDone, onErr }) {
  const [form, setForm] = useState({ course_code: '', course_name: '', description: '' })
  const [loading, setLoading] = useState(false)
  const submit = async e => {
    e.preventDefault(); setLoading(true)
    try {
      await createCourse(form)
      setForm({ course_code: '', course_name: '', description: '' })
      onDone(`Course ${form.course_code} created.`)
    } catch (err) {
      onErr(err.response?.data?.detail || 'Failed to create course.')
    } finally { setLoading(false) }
  }
  return (
    <form onSubmit={submit} className="space-y-3">
      <input required placeholder="Course Code (e.g. COMP3161)" value={form.course_code}
        onChange={e => setForm({...form, course_code: e.target.value})}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <input required placeholder="Course Name" value={form.course_name}
        onChange={e => setForm({...form, course_name: e.target.value})}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <textarea placeholder="Description (optional)" value={form.description}
        onChange={e => setForm({...form, description: e.target.value})}
        rows={2} className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <button type="submit" disabled={loading}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2 rounded transition disabled:opacity-50">
        {loading ? 'Creating…' : 'Create Course'}
      </button>
    </form>
  )
}

function AssignLecturerForm({ onDone, onErr }) {
  const [courseCode, setCourseCode] = useState('')
  const [lecturerId, setLecturerId] = useState('')
  const [loading, setLoading] = useState(false)
  const submit = async e => {
    e.preventDefault(); setLoading(true)
    try {
      await assignLecturer(courseCode, { lecturer_id: parseInt(lecturerId) })
      setCourseCode(''); setLecturerId('')
      onDone('Lecturer assigned successfully.')
    } catch (err) {
      onErr(err.response?.data?.detail || 'Failed to assign lecturer.')
    } finally { setLoading(false) }
  }
  return (
    <form onSubmit={submit} className="space-y-3">
      <input required placeholder="Course Code" value={courseCode}
        onChange={e => setCourseCode(e.target.value)}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <input required type="number" placeholder="Lecturer Account ID" value={lecturerId}
        onChange={e => setLecturerId(e.target.value)}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <button type="submit" disabled={loading}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2 rounded transition disabled:opacity-50">
        {loading ? 'Assigning…' : 'Assign Lecturer'}
      </button>
    </form>
  )
}

function EnrollStudentForm({ onDone, onErr }) {
  const [courseCode, setCourseCode] = useState('')
  const [studentId, setStudentId]   = useState('')
  const [loading, setLoading] = useState(false)
  const submit = async e => {
    e.preventDefault(); setLoading(true)
    try {
      await enrollStudent(courseCode, { student_id: parseInt(studentId) })
      setCourseCode(''); setStudentId('')
      onDone('Student enrolled successfully.')
    } catch (err) {
      onErr(err.response?.data?.detail || 'Failed to enroll student.')
    } finally { setLoading(false) }
  }
  return (
    <form onSubmit={submit} className="space-y-3">
      <input required placeholder="Course Code" value={courseCode}
        onChange={e => setCourseCode(e.target.value)}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <input required type="number" placeholder="Student Account ID" value={studentId}
        onChange={e => setStudentId(e.target.value)}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      <button type="submit" disabled={loading}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2 rounded transition disabled:opacity-50">
        {loading ? 'Enrolling…' : 'Enroll Student'}
      </button>
    </form>
  )
}
