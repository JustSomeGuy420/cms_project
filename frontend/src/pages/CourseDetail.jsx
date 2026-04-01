import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  getCourse, getCourseContent, getCourseAssignments,
  getCourseForums, getCourseEvents, getCourseMembers,
  submitAssignment, gradeSubmission, createSection,
  createSectionItem, createAssignment, createForum, createEvent
} from '../api'

const TABS = ['Content', 'Assignments', 'Forums', 'Events', 'Members']

export default function CourseDetail() {
  const { code } = useParams()
  const { user }  = useAuth()
  const [course, setCourse]     = useState(null)
  const [tab, setTab]           = useState('Content')
  const [content, setContent]   = useState([])
  const [assignments, setAssignments] = useState([])
  const [forums, setForums]     = useState([])
  const [events, setEvents]     = useState([])
  const [members, setMembers]   = useState([])
  const [loading, setLoading]   = useState(true)
  const [msg, setMsg]           = useState('')

  useEffect(() => {
    getCourse(code).then(({ data }) => setCourse(data)).finally(() => setLoading(false))
  }, [code])

  useEffect(() => {
    if (tab === 'Content')     getCourseContent(code).then(({ data }) => setContent(data))
    if (tab === 'Assignments') getCourseAssignments(code).then(({ data }) => setAssignments(data))
    if (tab === 'Forums')      getCourseForums(code).then(({ data }) => setForums(data))
    if (tab === 'Events')      getCourseEvents(code).then(({ data }) => setEvents(data))
    if (tab === 'Members')     getCourseMembers(code).then(({ data }) => setMembers(data))
  }, [tab, code])

  const flash = m => { setMsg(m); setTimeout(() => setMsg(''), 3000) }

  if (loading) return <div className="p-8 text-gray-400">Loading…</div>
  if (!course) return <div className="p-8 text-red-500">Course not found.</div>

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">

      {/* Header */}
      <div className="mb-6">
        <div className="text-xs font-mono text-indigo-500 mb-1">{course.course_code}</div>
        <h1 className="text-2xl font-bold text-gray-900">{course.course_name}</h1>
        <p className="text-gray-500 text-sm mt-1">{course.description}</p>
        {course.lecturer_name && (
          <p className="text-sm text-gray-400 mt-1">Lecturer: {course.lecturer_name}</p>
        )}
      </div>

      {msg && <div className="bg-green-50 border border-green-200 text-green-700 rounded px-4 py-2 text-sm mb-4">{msg}</div>}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium transition ${
              tab === t
                ? 'border-b-2 border-indigo-600 text-indigo-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}>
            {t}
          </button>
        ))}
      </div>

      {/* Content Tab */}
      {tab === 'Content' && (
        <div className="space-y-6">
          {user.role === 'lecturer' && <AddSectionForm code={code} onDone={() => { getCourseContent(code).then(({ data }) => setContent(data)); flash('Section added.') }} />}
          {content.length === 0 && <p className="text-gray-400 text-sm">No content yet.</p>}
          {content.map(sec => (
            <div key={sec.sec_no} className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-3">Section {sec.sec_no}: {sec.section_title}</h3>
              {user.role === 'lecturer' && <AddItemForm secNo={sec.sec_no} code={code} onDone={() => { getCourseContent(code).then(({ data }) => setContent(data)); flash('Item added.') }} />}
              <div className="space-y-2 mt-3">
                {sec.items.map(item => (
                  <a key={item.item_id} href={item.content_url} target="_blank" rel="noreferrer"
                    className="flex items-center gap-2 text-sm text-indigo-600 hover:underline">
                    <span className="bg-indigo-50 text-indigo-500 text-xs px-2 py-0.5 rounded capitalize">{item.type}</span>
                    {item.title}
                  </a>
                ))}
                {sec.items.length === 0 && <p className="text-gray-400 text-xs">No items in this section.</p>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Assignments Tab */}
      {tab === 'Assignments' && (
        <div className="space-y-4">
          {user.role === 'lecturer' && <AddAssignmentForm code={code} onDone={() => { getCourseAssignments(code).then(({ data }) => setAssignments(data)); flash('Assignment created.') }} />}
          {assignments.length === 0 && <p className="text-gray-400 text-sm">No assignments yet.</p>}
          {assignments.map(a => (
            <div key={a.ass_id} className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-800">{a.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{a.description}</p>
                  <p className="text-xs text-gray-400 mt-1">Due: {new Date(a.due_date).toLocaleString()}</p>
                </div>
              </div>
              {user.role === 'student' && <SubmitForm assId={a.ass_id} studentId={user.acc_id} onDone={() => flash('Submitted!')} />}
            </div>
          ))}
        </div>
      )}

      {/* Forums Tab */}
      {tab === 'Forums' && (
        <div className="space-y-4">
          {user.role === 'lecturer' && <AddForumForm code={code} onDone={() => { getCourseForums(code).then(({ data }) => setForums(data)); flash('Forum created.') }} />}
          {forums.length === 0 && <p className="text-gray-400 text-sm">No forums yet.</p>}
          {forums.map(f => (
            <Link key={f.df_id} to={`/forums/${f.df_id}`}
              className="block bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md hover:border-indigo-300 transition">
              <div className="font-semibold text-gray-800">{f.title}</div>
              <div className="text-sm text-gray-400 mt-1">Created by {f.created_by_name} · {new Date(f.created_at).toLocaleDateString()}</div>
            </Link>
          ))}
        </div>
      )}

      {/* Events Tab */}
      {tab === 'Events' && (
        <div className="space-y-4">
          {user.role === 'lecturer' && <AddEventForm code={code} onDone={() => { getCourseEvents(code).then(({ data }) => setEvents(data)); flash('Event created.') }} />}
          {events.length === 0 && <p className="text-gray-400 text-sm">No events yet.</p>}
          {events.map(ev => (
            <div key={ev.ev_id} className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm flex items-center gap-4">
              <div className="bg-indigo-50 text-indigo-600 font-bold text-center rounded px-3 py-2 text-sm min-w-[60px]">
                {new Date(ev.event_date).toLocaleDateString('en', { month: 'short', day: 'numeric' })}
              </div>
              <div>
                <div className="font-semibold text-gray-800">{ev.title}</div>
                <div className="text-sm text-gray-500">{ev.description}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Members Tab */}
      {tab === 'Members' && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Student No.</th>
                <th className="px-4 py-3 font-medium">Program</th>
                <th className="px-4 py-3 font-medium">Grade</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {members.map(m => (
                <tr key={m.acc_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-800">{m.name}</td>
                  <td className="px-4 py-3 text-gray-500 font-mono">{m.student_no}</td>
                  <td className="px-4 py-3 text-gray-500">{m.program}</td>
                  <td className="px-4 py-3 text-gray-500">{m.grade != null ? `${m.grade}%` : '—'}</td>
                </tr>
              ))}
              {members.length === 0 && (
                <tr><td colSpan={4} className="px-4 py-6 text-center text-gray-400">No members.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

    </div>
  )
}

// ── Inline mini-forms ─────────────────────────────────────────

function AddSectionForm({ code, onDone }) {
  const [open, setOpen] = useState(false)
  const [sec_no, setNo] = useState('')
  const [title, setTitle] = useState('')
  const submit = async e => {
    e.preventDefault()
    await createSection(code, { sec_no: parseInt(sec_no), title })
    setOpen(false); setNo(''); setTitle(''); onDone()
  }
  if (!open) return <button onClick={() => setOpen(true)} className="text-sm text-indigo-600 hover:underline">+ Add Section</button>
  return (
    <form onSubmit={submit} className="flex gap-2 items-end bg-indigo-50 p-3 rounded">
      <div><label className="text-xs text-gray-600">No.</label><input required value={sec_no} onChange={e => setNo(e.target.value)} className="block border rounded px-2 py-1 text-sm w-16" /></div>
      <div className="flex-1"><label className="text-xs text-gray-600">Title</label><input required value={title} onChange={e => setTitle(e.target.value)} className="block border rounded px-2 py-1 text-sm w-full" /></div>
      <button type="submit" className="bg-indigo-600 text-white text-sm px-3 py-1 rounded">Add</button>
      <button type="button" onClick={() => setOpen(false)} className="text-sm text-gray-400 hover:text-gray-600">Cancel</button>
    </form>
  )
}

function AddItemForm({ secNo, code, onDone }) {
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ title: '', type: 'file', content_url: '' })
  const submit = async e => {
    e.preventDefault()
    await createSectionItem(secNo, code, form)
    setOpen(false); onDone()
  }
  if (!open) return <button onClick={() => setOpen(true)} className="text-xs text-indigo-500 hover:underline">+ Add Item</button>
  return (
    <form onSubmit={submit} className="flex flex-wrap gap-2 items-end bg-gray-50 p-3 rounded mt-2">
      <div><label className="text-xs text-gray-600">Title</label><input required value={form.title} onChange={e => setForm({...form,title:e.target.value})} className="block border rounded px-2 py-1 text-sm" /></div>
      <div><label className="text-xs text-gray-600">Type</label>
        <select value={form.type} onChange={e => setForm({...form,type:e.target.value})} className="block border rounded px-2 py-1 text-sm">
          {['link','file','video','document','slide'].map(t => <option key={t}>{t}</option>)}
        </select>
      </div>
      <div className="flex-1"><label className="text-xs text-gray-600">URL</label><input required value={form.content_url} onChange={e => setForm({...form,content_url:e.target.value})} className="block border rounded px-2 py-1 text-sm w-full" /></div>
      <button type="submit" className="bg-indigo-600 text-white text-sm px-3 py-1 rounded">Add</button>
      <button type="button" onClick={() => setOpen(false)} className="text-sm text-gray-400">Cancel</button>
    </form>
  )
}

function AddAssignmentForm({ code, onDone }) {
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', due_date: '' })
  const submit = async e => {
    e.preventDefault()
    await createAssignment(code, form)
    setOpen(false); onDone()
  }
  if (!open) return <button onClick={() => setOpen(true)} className="text-sm text-indigo-600 hover:underline">+ Create Assignment</button>
  return (
    <form onSubmit={submit} className="bg-indigo-50 p-4 rounded space-y-2">
      <input required placeholder="Title" value={form.title} onChange={e => setForm({...form,title:e.target.value})} className="w-full border rounded px-3 py-2 text-sm" />
      <textarea placeholder="Description" value={form.description} onChange={e => setForm({...form,description:e.target.value})} className="w-full border rounded px-3 py-2 text-sm" rows={2} />
      <input required type="datetime-local" value={form.due_date} onChange={e => setForm({...form,due_date:e.target.value})} className="w-full border rounded px-3 py-2 text-sm" />
      <div className="flex gap-2">
        <button type="submit" className="bg-indigo-600 text-white text-sm px-4 py-1 rounded">Create</button>
        <button type="button" onClick={() => setOpen(false)} className="text-sm text-gray-400">Cancel</button>
      </div>
    </form>
  )
}

function SubmitForm({ assId, studentId, onDone }) {
  const [open, setOpen] = useState(false)
  const [url, setUrl] = useState('')
  const submit = async e => {
    e.preventDefault()
    await submitAssignment(assId, { student_id: studentId, file_url: url })
    setOpen(false); onDone()
  }
  if (!open) return <button onClick={() => setOpen(true)} className="mt-3 text-sm bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700">Submit</button>
  return (
    <form onSubmit={submit} className="mt-3 flex gap-2 items-center">
      <input required placeholder="File URL" value={url} onChange={e => setUrl(e.target.value)} className="flex-1 border rounded px-3 py-1 text-sm" />
      <button type="submit" className="bg-indigo-600 text-white text-sm px-3 py-1 rounded">Submit</button>
      <button type="button" onClick={() => setOpen(false)} className="text-sm text-gray-400">Cancel</button>
    </form>
  )
}

function AddForumForm({ code, onDone }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const submit = async e => {
    e.preventDefault()
    await createForum(code, { title })
    setOpen(false); setTitle(''); onDone()
  }
  if (!open) return <button onClick={() => setOpen(true)} className="text-sm text-indigo-600 hover:underline">+ Create Forum</button>
  return (
    <form onSubmit={submit} className="flex gap-2 bg-indigo-50 p-3 rounded">
      <input required placeholder="Forum title" value={title} onChange={e => setTitle(e.target.value)} className="flex-1 border rounded px-3 py-1 text-sm" />
      <button type="submit" className="bg-indigo-600 text-white text-sm px-3 py-1 rounded">Create</button>
      <button type="button" onClick={() => setOpen(false)} className="text-sm text-gray-400">Cancel</button>
    </form>
  )
}

function AddEventForm({ code, onDone }) {
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', event_date: '' })
  const submit = async e => {
    e.preventDefault()
    await createEvent(code, form)
    setOpen(false); onDone()
  }
  if (!open) return <button onClick={() => setOpen(true)} className="text-sm text-indigo-600 hover:underline">+ Add Event</button>
  return (
    <form onSubmit={submit} className="bg-indigo-50 p-4 rounded space-y-2">
      <input required placeholder="Title" value={form.title} onChange={e => setForm({...form,title:e.target.value})} className="w-full border rounded px-3 py-2 text-sm" />
      <input placeholder="Description" value={form.description} onChange={e => setForm({...form,description:e.target.value})} className="w-full border rounded px-3 py-2 text-sm" />
      <input required type="datetime-local" value={form.event_date} onChange={e => setForm({...form,event_date:e.target.value})} className="w-full border rounded px-3 py-2 text-sm" />
      <div className="flex gap-2">
        <button type="submit" className="bg-indigo-600 text-white text-sm px-4 py-1 rounded">Add</button>
        <button type="button" onClick={() => setOpen(false)} className="text-sm text-gray-400">Cancel</button>
      </div>
    </form>
  )
}
