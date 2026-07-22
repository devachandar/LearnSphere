import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useCourse } from "../api/courses";
import { useCompleteLesson, useEnroll, useMyEnrollments } from "../api/enrollments";
import { useCourseAssignments, useCourseQuizzes, useSubmitAssignment } from "../api/assessments";
import { useAnnouncements, useCreateThread, useDiscussionThreads } from "../api/communication";
import { useAuthStore } from "../store/auth";
import ProgressRing from "../components/ProgressRing";
import QuizPanel from "../components/QuizPanel";

type Tab = "content" | "quizzes" | "assignments" | "discussion" | "announcements";

export default function CourseDetail() {
  const { id } = useParams();
  const user = useAuthStore((s) => s.user);
  const [tab, setTab] = useState<Tab>("content");
  const [activeQuizId, setActiveQuizId] = useState<string | null>(null);

  const { data: course, isLoading } = useCourse(id);
  const { data: enrollments } = useMyEnrollments();
  const enroll = useEnroll();
  const completeLesson = useCompleteLesson();

  const enrollment = enrollments?.find((e) => e.course_id === id);
  const completedLessonIds = new Set<string>(); // populated lazily below if needed

  if (isLoading || !course) return <div className="max-w-4xl mx-auto px-6 py-10 text-slate">Loading...</div>;

  const isLearner = user?.role === "learner";
  const isOwner = user?.id === course.instructor_id;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <span className="text-xs font-semibold text-plum uppercase tracking-wide">{course.category}</span>
      <div className="flex items-start justify-between gap-4 mt-1">
        <h1 className="font-display font-bold text-3xl text-ink">{course.title}</h1>
        {enrollment && <ProgressRing percent={enrollment.progressPercent} />}
      </div>
      <p className="text-slate mt-2 max-w-2xl">{course.description}</p>

      <div className="mt-4 flex gap-3">
        {isLearner && !enrollment && (
          <button className="btn btn-accent" onClick={() => enroll.mutate(course.id)} disabled={enroll.isPending}>
            {enroll.isPending ? "Enrolling..." : "Enroll now"}
          </button>
        )}
        {isOwner && (
          <Link to={`/instructor/courses/${course.id}`} className="btn btn-ghost">
            Manage this course
          </Link>
        )}
      </div>

      <div className="mt-8 border-b border-line flex gap-6 text-sm font-medium">
        {(["content", "quizzes", "assignments", "discussion", "announcements"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`pb-3 -mb-px border-b-2 capitalize ${
              tab === t ? "border-plum text-ink" : "border-transparent text-slate"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {tab === "content" && (
          <div className="space-y-5">
            {course.modules.map((m) => (
              <div key={m.id} className="card p-4">
                <h3 className="font-display font-semibold text-ink">{m.title}</h3>
                <ul className="mt-3 divide-y divide-line">
                  {m.lessons.map((l) => (
                    <li key={l.id} className="py-2.5 flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-medium text-ink">{l.title}</p>
                        <p className="text-xs text-slate">
                          {l.content_type} · {l.duration_minutes} min
                        </p>
                      </div>
                      {isLearner && enrollment && (
                        <button
                          className="btn btn-ghost text-xs py-1.5"
                          onClick={() => completeLesson.mutate(l.id)}
                          disabled={completeLesson.isPending || completedLessonIds.has(l.id)}
                        >
                          Mark complete
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
            {!course.modules.length && <p className="text-slate text-sm">No content published yet.</p>}
          </div>
        )}

        {tab === "quizzes" && (
          <QuizzesTab courseId={course.id} activeQuizId={activeQuizId} setActiveQuizId={setActiveQuizId} />
        )}

        {tab === "assignments" && <AssignmentsTab courseId={course.id} />}

        {tab === "discussion" && <DiscussionTab courseId={course.id} />}

        {tab === "announcements" && <AnnouncementsTab courseId={course.id} />}
      </div>
    </div>
  );
}

function QuizzesTab({
  courseId,
  activeQuizId,
  setActiveQuizId,
}: {
  courseId: string;
  activeQuizId: string | null;
  setActiveQuizId: (id: string | null) => void;
}) {
  const { data: quizzes } = useCourseQuizzes(courseId);

  if (activeQuizId) {
    return <QuizPanel quizId={activeQuizId} onDone={() => setActiveQuizId(null)} />;
  }

  return (
    <div className="space-y-3">
      {quizzes?.length ? (
        quizzes.map((q: any) => (
          <div key={q.id} className="card p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold text-ink text-sm">{q.title}</p>
              <p className="text-xs text-slate">Passing score: {q.passing_score}%</p>
            </div>
            <button className="btn btn-primary text-xs py-1.5" onClick={() => setActiveQuizId(q.id)}>
              Take quiz
            </button>
          </div>
        ))
      ) : (
        <p className="text-slate text-sm">No quizzes yet.</p>
      )}
    </div>
  );
}

function AssignmentsTab({ courseId }: { courseId: string }) {
  const { data: assignments } = useCourseAssignments(courseId);
  const submit = useSubmitAssignment();
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({});

  return (
    <div className="space-y-4">
      {assignments?.length ? (
        assignments.map((a) => (
          <div key={a.id} className="card p-4">
            <p className="font-semibold text-ink text-sm">{a.title}</p>
            <p className="text-xs text-slate mt-1">{a.description}</p>
            {submitted[a.id] ? (
              <p className="text-xs text-plum mt-3 font-semibold">Submitted - waiting on instructor feedback.</p>
            ) : (
              <div className="mt-3">
                <textarea
                  className="input"
                  rows={3}
                  placeholder="Write your submission..."
                  value={drafts[a.id] || ""}
                  onChange={(e) => setDrafts({ ...drafts, [a.id]: e.target.value })}
                />
                <button
                  className="btn btn-primary text-xs py-1.5 mt-2"
                  onClick={async () => {
                    await submit.mutateAsync({ assignmentId: a.id, textContent: drafts[a.id] || "" });
                    setSubmitted({ ...submitted, [a.id]: true });
                  }}
                >
                  Submit
                </button>
              </div>
            )}
          </div>
        ))
      ) : (
        <p className="text-slate text-sm">No assignments yet.</p>
      )}
    </div>
  );
}

function DiscussionTab({ courseId }: { courseId: string }) {
  const { data: threads } = useDiscussionThreads(courseId);
  const createThread = useCreateThread();
  const [title, setTitle] = useState("");

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <input
          className="input"
          placeholder="Start a new discussion..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button
          className="btn btn-primary"
          onClick={async () => {
            if (!title.trim()) return;
            await createThread.mutateAsync({ courseId, title });
            setTitle("");
          }}
        >
          Post
        </button>
      </div>
      <div className="space-y-2">
        {threads?.length ? (
          threads.map((t: any) => (
            <Link key={t.id} to={`/discussions/${t.id}`} className="card p-3 block hover:border-plum text-sm font-medium text-ink">
              {t.title}
            </Link>
          ))
        ) : (
          <p className="text-slate text-sm">No discussions yet - start one.</p>
        )}
      </div>
    </div>
  );
}

function AnnouncementsTab({ courseId }: { courseId: string }) {
  const { data: announcements } = useAnnouncements(courseId);
  return (
    <div className="space-y-3">
      {announcements?.length ? (
        announcements.map((a: any) => (
          <div key={a.id} className="card p-4">
            <p className="font-semibold text-ink text-sm">{a.title}</p>
            <p className="text-xs text-slate mt-1">{a.body}</p>
          </div>
        ))
      ) : (
        <p className="text-slate text-sm">No announcements yet.</p>
      )}
    </div>
  );
}
