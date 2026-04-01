import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getForumThreads, createThread, replyToThread } from '../api'

export default function Forum() {
  const { id } = useParams()
  const { user } = useAuth()
  const [threads, setThreads]     = useState([])
  const [loading, setLoading]     = useState(true)
  const [replyTo, setReplyTo]     = useState(null)
  const [newThread, setNewThread] = useState(false)

  const load = () => getForumThreads(id).then(({ data }) => setThreads(data)).finally(() => setLoading(false))

  useEffect(() => { load() }, [id])

  // Build tree: top-level threads + their replies
  const topLevel = threads.filter(t => !t.parent_id)
  const replies  = threads.filter(t =>  t.parent_id)
  const getReplies = (parentId) => replies.filter(r => r.parent_id === parentId)

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Forum Threads</h1>
        <button onClick={() => setNewThread(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded transition">
          + New Thread
        </button>
      </div>

      {newThread && (
        <ThreadForm
          label="New Thread"
          onSubmit={async ({ title, content }) => {
            await createThread(id, { title, content })
            setNewThread(false); load()
          }}
          onCancel={() => setNewThread(false)}
        />
      )}

      {loading ? (
        <p className="text-gray-400 text-sm">Loading…</p>
      ) : topLevel.length === 0 ? (
        <p className="text-gray-400 text-sm">No threads yet. Start the conversation!</p>
      ) : (
        <div className="space-y-4">
          {topLevel.map(thread => (
            <ThreadCard
              key={thread.dt_id}
              thread={thread}
              replies={getReplies(thread.dt_id)}
              allThreads={threads}
              onReply={() => setReplyTo(thread.dt_id)}
              replyTo={replyTo}
              setReplyTo={setReplyTo}
              onSubmitReply={async ({ title, content }) => {
                await replyToThread(replyTo, { title, content })
                setReplyTo(null); load()
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function ThreadCard({ thread, replies, allThreads, onReply, replyTo, setReplyTo, onSubmitReply }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-800">{thread.title}</h3>
            <p className="text-sm text-gray-600 mt-1">{thread.content}</p>
            <p className="text-xs text-gray-400 mt-2">
              {thread.author_name} · {new Date(thread.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="flex gap-4 mt-3">
          {replies.length > 0 && (
            <button onClick={() => setExpanded(!expanded)}
              className="text-xs text-indigo-500 hover:underline">
              {expanded ? 'Hide' : `Show ${replies.length} repl${replies.length === 1 ? 'y' : 'ies'}`}
            </button>
          )}
          <button onClick={() => setReplyTo(replyTo === thread.dt_id ? null : thread.dt_id)}
            className="text-xs text-gray-500 hover:text-indigo-500">
            Reply
          </button>
        </div>
      </div>

      {/* Reply form */}
      {replyTo === thread.dt_id && (
        <div className="border-t border-gray-100 px-5 pb-4 pt-3">
          <ThreadForm
            label="Post Reply"
            onSubmit={onSubmitReply}
            onCancel={() => setReplyTo(null)}
            compact
          />
        </div>
      )}

      {/* Nested replies */}
      {expanded && replies.length > 0 && (
        <div className="border-t border-gray-100 bg-gray-50 rounded-b-lg">
          {replies.map(reply => (
            <div key={reply.dt_id} className="px-8 py-3 border-b border-gray-100 last:border-0">
              <p className="text-sm font-medium text-gray-700">{reply.title}</p>
              <p className="text-sm text-gray-600 mt-0.5">{reply.content}</p>
              <p className="text-xs text-gray-400 mt-1">
                {reply.author_name} · {new Date(reply.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ThreadForm({ label, onSubmit, onCancel, compact }) {
  const [form, setForm] = useState({ title: '', content: '' })
  const submit = async e => {
    e.preventDefault()
    await onSubmit(form)
    setForm({ title: '', content: '' })
  }
  return (
    <form onSubmit={submit} className={`space-y-2 ${!compact && 'bg-indigo-50 p-4 rounded mb-4'}`}>
      <input required placeholder="Title" value={form.title}
        onChange={e => setForm({...form, title: e.target.value})}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <textarea required placeholder="Content" value={form.content}
        onChange={e => setForm({...form, content: e.target.value})}
        rows={compact ? 2 : 3}
        className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <div className="flex gap-2">
        <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-1.5 rounded transition">
          {label}
        </button>
        <button type="button" onClick={onCancel} className="text-sm text-gray-400 hover:text-gray-600">
          Cancel
        </button>
      </div>
    </form>
  )
}
