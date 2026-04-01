import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Attach JWT to every request automatically
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Auth ─────────────────────────────────────────────────────
export const register  = data => api.post('/auth/register', data)
export const login     = data => api.post('/auth/login', data)

// ── Courses ───────────────────────────────────────────────────
export const getCourses            = ()          => api.get('/courses')
export const getCourse             = code        => api.get(`/courses/${code}`)
export const createCourse          = data        => api.post('/courses', data)
export const getCoursesForStudent  = id          => api.get(`/courses/student/${id}`)
export const getCoursesForLecturer = id          => api.get(`/courses/lecturer/${id}`)
export const getCourseMembers      = code        => api.get(`/courses/${code}/members`)
export const enrollStudent         = (code, data)=> api.post(`/courses/${code}/enroll`, data)
export const assignLecturer        = (code, data)=> api.post(`/courses/${code}/assign-lecturer`, data)

// ── Calendar ──────────────────────────────────────────────────
export const getCourseEvents  = code        => api.get(`/courses/${code}/events`)
export const getStudentEvents = (id, date)  => api.get(`/students/${id}/events?date=${date}`)
export const createEvent      = (code, data)=> api.post(`/courses/${code}/events`, data)

// ── Forums ────────────────────────────────────────────────────
export const getCourseForums  = code        => api.get(`/courses/${code}/forums`)
export const createForum      = (code, data)=> api.post(`/courses/${code}/forums`, data)
export const getForumThreads  = id          => api.get(`/forums/${id}/threads`)
export const createThread     = (id, data)  => api.post(`/forums/${id}/threads`, data)
export const replyToThread    = (id, data)  => api.post(`/threads/${id}/reply`, data)

// ── Content ───────────────────────────────────────────────────
export const getCourseContent  = code              => api.get(`/courses/${code}/content`)
export const createSection     = (code, data)      => api.post(`/courses/${code}/sections`, data)
export const createSectionItem = (no, code, data)  => api.post(`/sections/${no}/${code}/items`, data)

// ── Assignments ───────────────────────────────────────────────
export const getCourseAssignments = code       => api.get(`/courses/${code}/assignments`)
export const createAssignment     = (code, data)=> api.post(`/courses/${code}/assignments`, data)
export const submitAssignment     = (id, data)  => api.post(`/assignments/${id}/submit`, data)
export const gradeSubmission      = (id, data)  => api.put(`/submissions/${id}/grade`, data)

// ── Reports ───────────────────────────────────────────────────
export const reportCourses50Plus  = () => api.get('/reports/courses-50-plus')
export const reportStudents5Plus  = () => api.get('/reports/students-5-plus')
export const reportLecturers3Plus = () => api.get('/reports/lecturers-3-plus')
export const reportTop10Courses   = () => api.get('/reports/top-10-courses')
export const reportTop10Students  = () => api.get('/reports/top-10-students')
