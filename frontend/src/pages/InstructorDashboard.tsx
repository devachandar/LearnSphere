import { useState } from "react";
import { Link } from "react-router-dom";
import { useCreateCourse, useMyCourses } from "../api/courses";

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-amber-100 text-amber-700",
  published: "bg-green-100 text-green-700",
  archived: "bg-gray-100 text-gray-600",
};

export default function InstructorDashboard() {
  const { data: courses } = useMyCourses();
  const createCourse = useCreateCourse();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", category: "general" });

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="font-display font-bold text-3xl text-ink">Your courses</h1>
        <button className="btn btn-accent" onClick={() => setShowForm((s) => !s)}>
          + New course
        </button>
      </div>

      {showForm && (
        <div className="card p-5 mt-6 max-w-lg">
          <div className="space-y-3">
            <input
              className="input"
              placeholder="Course title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            <textarea
              className="input"
              rows={2}
              placeholder="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
            <select
              className="input"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            >
              <option value="general">General</option>
              <option value="engineering">Engineering</option>
              <option value="design">Design</option>
              <option value="business">Business</option>
            </select>
            <button
              className="btn btn-primary"
              onClick={async () => {
                await createCourse.mutateAsync(form);
                setShowForm(false);
                setForm({ title: "", description: "", category: "general" });
              }}
              disabled={createCourse.isPending || !form.title}
            >
              Create draft
            </button>
          </div>
        </div>
      )}

      <div className="mt-8 space-y-3">
        {courses?.length ? (
          courses.map((c) => (
            <Link key={c.id} to={`/instructor/courses/${c.id}`} className="card p-4 flex items-center justify-between block hover:border-plum">
              <div>
                <p className="font-semibold text-ink">{c.title}</p>
                <p className="text-xs text-slate mt-0.5">{c.category}</p>
              </div>
              <span className={`text-xs font-semibold px-2 py-1 rounded-full ${STATUS_STYLES[c.status]}`}>
                {c.status}
              </span>
            </Link>
          ))
        ) : (
          <p className="text-slate text-sm">You haven't created a course yet.</p>
        )}
      </div>
    </div>
  );
}
