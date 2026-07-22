import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAddLesson, useAddModule, useCourse, usePublishCourse } from "../api/courses";
import { useCourseAssignments, useCourseQuizzes, useCreateAssignment, useCreateQuiz } from "../api/assessments";
import { useCourseEnrollments } from "../api/enrollments";
import { useCourseMetrics } from "../api/admin";
import { useCreateAnnouncement } from "../api/communication";

export default function InstructorCourseBuilder() {
  const { id } = useParams();
  const { data: course, refetch } = useCourse(id);
  const publish = usePublishCourse();
  const addModule = useAddModule();
  const addLesson = useAddLesson();
  const { data: enrollments } = useCourseEnrollments(id);
  const { data: metrics } = useCourseMetrics(id);

  const [moduleTitle, setModuleTitle] = useState("");
  const [lessonForms, setLessonForms] = useState<Record<string, { title: string; contentType: string; textContent: string }>>({});

  if (!course || !id) return <div className="max-w-4xl mx-auto px-6 py-10 text-slate">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-3xl text-ink">{course.title}</h1>
          <span className="text-xs font-semibold text-slate uppercase">{course.status}</span>
        </div>
        {course.status === "draft" && (
          <button className="btn btn-accent" onClick={() => publish.mutate(course.id)} disabled={publish.isPending}>
            Publish course
          </button>
        )}
      </div>

      {metrics && (
        <div className="grid grid-cols-3 gap-3 mt-6 max-w-md">
          <Stat label="Enrolled" value={metrics.enrollmentCount} />
          <Stat label="Completed" value={metrics.completionCount} />
          <Stat label="Avg score" value={metrics.averageScore != null ? `${metrics.averageScore}%` : "—"} />
        </div>
      )}

      <section className="mt-8">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Modules & lessons</h2>
        <div className="space-y-4">
          {course.modules.map((m) => (
            <div key={m.id} className="card p-4">
              <p className="font-semibold text-ink text-sm">{m.title}</p>
              <ul className="mt-2 space-y-1">
                {m.lessons.map((l) => (
                  <li key={l.id} className="text-sm text-slate">
                    {l.title} <span className="text-xs">({l.content_type})</span>
                  </li>
                ))}
              </ul>

              <div className="mt-3 flex gap-2">
                <input
                  className="input text-sm"
                  placeholder="New lesson title"
                  value={lessonForms[m.id]?.title || ""}
                  onChange={(e) =>
                    setLessonForms({ ...lessonForms, [m.id]: { ...lessonForms[m.id], title: e.target.value, contentType: lessonForms[m.id]?.contentType || "text", textContent: lessonForms[m.id]?.textContent || "" } })
                  }
                />
                <select
                  className="input text-sm w-32"
                  value={lessonForms[m.id]?.contentType || "text"}
                  onChange={(e) =>
                    setLessonForms({ ...lessonForms, [m.id]: { ...lessonForms[m.id], contentType: e.target.value, title: lessonForms[m.id]?.title || "", textContent: lessonForms[m.id]?.textContent || "" } })
                  }
                >
                  <option value="text">Text</option>
                  <option value="video">Video</option>
                  <option value="pdf">PDF</option>
                </select>
                <button
                  className="btn btn-ghost text-xs"
                  onClick={async () => {
                    const f = lessonForms[m.id];
                    if (!f?.title) return;
                    await addLesson.mutateAsync({ moduleId: m.id, courseId: course.id, title: f.title, contentType: f.contentType, textContent: f.textContent });
                    setLessonForms({ ...lessonForms, [m.id]: { title: "", contentType: "text", textContent: "" } });
                    refetch();
                  }}
                >
                  Add lesson
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex gap-2 max-w-md">
          <input className="input" placeholder="New module title" value={moduleTitle} onChange={(e) => setModuleTitle(e.target.value)} />
          <button
            className="btn btn-primary text-sm"
            onClick={async () => {
              if (!moduleTitle.trim()) return;
              await addModule.mutateAsync({ courseId: course.id, title: moduleTitle });
              setModuleTitle("");
              refetch();
            }}
          >
            Add module
          </button>
        </div>
      </section>

      <QuizBuilder courseId={course.id} />
      <AssignmentBuilder courseId={course.id} />
      <AnnouncementComposer courseId={course.id} />

      {enrollments && (
        <section className="mt-10">
          <h2 className="font-display font-semibold text-lg text-ink mb-3">Enrolled learners ({enrollments.length})</h2>
          <div className="card divide-y divide-line">
            {enrollments.map((e: any) => (
              <div key={e.id} className="p-3 text-sm text-slate flex justify-between">
                <span>{e.learner_id}</span>
                <span className="capitalize">{e.status}</span>
              </div>
            ))}
            {!enrollments.length && <p className="p-3 text-sm text-slate">No one enrolled yet.</p>}
          </div>
        </section>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card p-3 text-center">
      <p className="font-display font-bold text-xl text-ink">{value}</p>
      <p className="text-xs text-slate">{label}</p>
    </div>
  );
}

function QuizBuilder({ courseId }: { courseId: string }) {
  const { data: quizzes } = useCourseQuizzes(courseId);
  const createQuiz = useCreateQuiz();
  const [title, setTitle] = useState("");
  const [questionText, setQuestionText] = useState("");
  const [options, setOptions] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("");
  const [questions, setQuestions] = useState<any[]>([]);

  return (
    <section className="mt-10">
      <h2 className="font-display font-semibold text-lg text-ink mb-3">Quizzes</h2>
      <div className="space-y-2 mb-4">
        {quizzes?.map((q: any) => (
          <div key={q.id} className="card p-3 text-sm text-ink font-medium">
            {q.title}
          </div>
        ))}
      </div>

      <div className="card p-4 max-w-lg">
        <input className="input mb-2" placeholder="Quiz title" value={title} onChange={(e) => setTitle(e.target.value)} />

        <div className="border-t border-line pt-3 mt-2">
          <p className="text-xs font-semibold text-slate mb-2">Add a question (multiple choice)</p>
          <input className="input mb-2 text-sm" placeholder="Question text" value={questionText} onChange={(e) => setQuestionText(e.target.value)} />
          <input className="input mb-2 text-sm" placeholder="Options, comma separated" value={options} onChange={(e) => setOptions(e.target.value)} />
          <input className="input mb-2 text-sm" placeholder="Correct answer (must match an option)" value={correctAnswer} onChange={(e) => setCorrectAnswer(e.target.value)} />
          <button
            className="btn btn-ghost text-xs"
            onClick={() => {
              if (!questionText || !correctAnswer) return;
              setQuestions([
                ...questions,
                {
                  questionText,
                  questionType: "multiple_choice",
                  options: options.split(",").map((o) => o.trim()).filter(Boolean),
                  correctAnswer,
                  points: 1,
                },
              ]);
              setQuestionText("");
              setOptions("");
              setCorrectAnswer("");
            }}
          >
            + Add question ({questions.length} added)
          </button>
        </div>

        <button
          className="btn btn-primary text-sm mt-4"
          onClick={async () => {
            if (!title || !questions.length) return;
            await createQuiz.mutateAsync({ courseId, title, passingScore: 70, questions });
            setTitle("");
            setQuestions([]);
          }}
        >
          Save quiz
        </button>
      </div>
    </section>
  );
}

function AssignmentBuilder({ courseId }: { courseId: string }) {
  const { data: assignments } = useCourseAssignments(courseId);
  const createAssignment = useCreateAssignment();
  const [form, setForm] = useState({ title: "", description: "", maxPoints: 100 });

  return (
    <section className="mt-10">
      <h2 className="font-display font-semibold text-lg text-ink mb-3">Assignments</h2>
      <div className="space-y-2 mb-4">
        {assignments?.map((a) => (
          <div key={a.id} className="card p-3 text-sm text-ink font-medium">
            {a.title}
          </div>
        ))}
      </div>
      <div className="card p-4 max-w-lg space-y-2">
        <input className="input" placeholder="Assignment title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <textarea className="input" rows={2} placeholder="Instructions" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <input
          className="input"
          type="number"
          placeholder="Max points"
          value={form.maxPoints}
          onChange={(e) => setForm({ ...form, maxPoints: Number(e.target.value) })}
        />
        <button
          className="btn btn-primary text-sm"
          onClick={async () => {
            if (!form.title) return;
            await createAssignment.mutateAsync({ courseId, ...form });
            setForm({ title: "", description: "", maxPoints: 100 });
          }}
        >
          Save assignment
        </button>
      </div>
    </section>
  );
}

function AnnouncementComposer({ courseId }: { courseId: string }) {
  const createAnnouncement = useCreateAnnouncement();
  const [form, setForm] = useState({ title: "", body: "" });

  return (
    <section className="mt-10">
      <h2 className="font-display font-semibold text-lg text-ink mb-3">Post an announcement</h2>
      <div className="card p-4 max-w-lg space-y-2">
        <input className="input" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <textarea className="input" rows={2} placeholder="Message" value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} />
        <button
          className="btn btn-primary text-sm"
          onClick={async () => {
            if (!form.title || !form.body) return;
            await createAnnouncement.mutateAsync({ courseId, ...form });
            setForm({ title: "", body: "" });
          }}
        >
          Post
        </button>
      </div>
    </section>
  );
}
