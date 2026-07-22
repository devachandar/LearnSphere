import { Link } from "react-router-dom";
import { useMyCertificates } from "../api/enrollments";
import { useMyEnrollments } from "../api/enrollments";
import { useMyNotifications } from "../api/communication";
import ProgressRing from "../components/ProgressRing";

export default function LearnerDashboard() {
  const { data: enrollments } = useMyEnrollments();
  const { data: certificates } = useMyCertificates();
  const { data: notifications } = useMyNotifications();

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="font-display font-bold text-3xl text-ink">My learning</h1>

      <section className="mt-8">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">In progress</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {enrollments?.length ? (
            enrollments.map((e) => (
              <Link key={e.id} to={`/courses/${e.course_id}`} className="card p-4 flex items-center gap-4 hover:border-plum">
                <ProgressRing percent={e.progressPercent} />
                <div>
                  <p className="font-semibold text-ink text-sm">{e.course_title}</p>
                  <p className="text-xs text-slate capitalize mt-0.5">{e.status.replace("_", " ")}</p>
                </div>
              </Link>
            ))
          ) : (
            <p className="text-slate text-sm">
              Nothing yet -{" "}
              <Link to="/catalog" className="text-plum font-semibold">
                browse the catalog
              </Link>
              .
            </p>
          )}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Certificates</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {certificates?.length ? (
            certificates.map((c) => (
              <div key={c.id} className="card p-4 border-l-4 border-l-coral">
                <p className="font-semibold text-ink text-sm">{c.course_title}</p>
                <p className="text-xs text-slate mt-1">Issued {new Date(c.issued_at).toLocaleDateString()}</p>
              </div>
            ))
          ) : (
            <p className="text-slate text-sm">Complete a course to earn your first certificate.</p>
          )}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Notifications</h2>
        <div className="card divide-y divide-line">
          {notifications?.length ? (
            notifications.map((n) => (
              <div key={n.id} className="p-3">
                <p className="text-sm font-medium text-ink">{n.title}</p>
                <p className="text-xs text-slate mt-0.5">{n.body}</p>
              </div>
            ))
          ) : (
            <p className="p-3 text-sm text-slate">You're all caught up.</p>
          )}
        </div>
      </section>
    </div>
  );
}
