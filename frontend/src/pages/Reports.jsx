import { useEffect, useState } from 'react'
import {
  reportCourses50Plus, reportStudents5Plus, reportLecturers3Plus,
  reportTop10Courses, reportTop10Students
} from '../api'

export default function Reports() {
  const [data, setData]       = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      reportCourses50Plus(),
      reportStudents5Plus(),
      reportLecturers3Plus(),
      reportTop10Courses(),
      reportTop10Students(),
    ]).then(([r1, r2, r3, r4, r5]) => {
      setData({
        courses50:   r1.data,
        students5:   r2.data,
        lecturers3:  r3.data,
        top10courses:r4.data,
        top10students:r5.data,
      })
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="p-8 text-gray-400">Loading reports…</div>

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">

      <h1 className="text-2xl font-bold text-gray-900">Reports</h1>

      <ReportTable
        title="Courses with 50 or More Students"
        rows={data.courses50}
        cols={[
          { key: 'course_code',  label: 'Code' },
          { key: 'course_name',  label: 'Course Name' },
          { key: 'student_count',label: 'Students' },
        ]}
      />

      <ReportTable
        title="Students Enrolled in 5 or More Courses"
        rows={data.students5}
        cols={[
          { key: 'name',         label: 'Name' },
          { key: 'student_no',   label: 'Student No.' },
          { key: 'program',      label: 'Program' },
          { key: 'course_count', label: 'Courses' },
        ]}
      />

      <ReportTable
        title="Lecturers Teaching 3 or More Courses"
        rows={data.lecturers3}
        cols={[
          { key: 'name',         label: 'Name' },
          { key: 'staff_id',     label: 'Staff ID' },
          { key: 'department',   label: 'Department' },
          { key: 'course_count', label: 'Courses' },
        ]}
      />

      <ReportTable
        title="Top 10 Most Enrolled Courses"
        rows={data.top10courses}
        cols={[
          { key: 'course_code',   label: 'Code' },
          { key: 'course_name',   label: 'Course Name' },
          { key: 'lecturer_name', label: 'Lecturer' },
          { key: 'student_count', label: 'Enrolled' },
        ]}
        ranked
      />

      <ReportTable
        title="Top 10 Students by Overall Average"
        rows={data.top10students}
        cols={[
          { key: 'name',            label: 'Name' },
          { key: 'student_no',      label: 'Student No.' },
          { key: 'program',         label: 'Program' },
          { key: 'graded_courses',  label: 'Courses Graded' },
          { key: 'overall_average', label: 'Average (%)' },
        ]}
        ranked
      />

    </div>
  )
}

function ReportTable({ title, rows, cols, ranked }) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-3">{title}</h2>
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 text-left">
            <tr>
              {ranked && <th className="px-4 py-3 font-medium w-10">#</th>}
              {cols.map(c => (
                <th key={c.key} className="px-4 py-3 font-medium">{c.label}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {rows?.length === 0 && (
              <tr><td colSpan={cols.length + (ranked ? 1 : 0)} className="px-4 py-6 text-center text-gray-400">No data.</td></tr>
            )}
            {rows?.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50">
                {ranked && (
                  <td className="px-4 py-3 text-gray-400 font-medium">{i + 1}</td>
                )}
                {cols.map(c => (
                  <td key={c.key} className="px-4 py-3 text-gray-700">{row[c.key] ?? '—'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-400 mt-1">{rows?.length ?? 0} rows</p>
    </div>
  )
}
