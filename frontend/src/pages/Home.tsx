import { Link } from "react-router-dom";
import { useAuthStore } from "../store/auth";

export default function Home() {
  const user = useAuthStore((s) => s.user);

  return (
    <>
      <section className="bg-ink text-white">
        <div className="max-w-6xl mx-auto px-6 py-24">
          <span className="text-coral text-xs font-semibold tracking-widest uppercase">
            LearnSphere · multi-tenant learning platform
          </span>
          <h1 className="font-display font-bold text-4xl md:text-5xl mt-3 max-w-xl leading-tight">
            One platform, every organization's own{" "}
            <span className="text-coral">training universe.</span>
          </h1>
          <p className="mt-4 max-w-md text-white/70">
            Instructors build courses, learners track real progress, and admins see it all -
            without any organization ever seeing another's data.
          </p>
          <div className="mt-8 flex gap-3">
            {user ? (
              <Link to="/catalog" className="btn btn-accent">
                Browse courses
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-accent">
                  Get started
                </Link>
                <Link to="/login" className="btn border border-white/30 text-white hover:border-white">
                  Sign in
                </Link>
              </>
            )}
          </div>

          <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg">
            <div>
              <div className="font-display text-2xl font-bold">10M+</div>
              <div className="text-xs text-white/50 uppercase tracking-wide">Learners supported</div>
            </div>
            <div>
              <div className="font-display text-2xl font-bold">50K+</div>
              <div className="text-xs text-white/50 uppercase tracking-wide">Organizations</div>
            </div>
            <div>
              <div className="font-display text-2xl font-bold">&lt;300ms</div>
              <div className="text-xs text-white/50 uppercase tracking-wide">Course load target</div>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="font-display font-bold text-2xl text-ink">Built for every role</h2>
        <div className="mt-6 grid md:grid-cols-4 gap-4">
          {[
            ["Learners", "Enroll, watch lessons, take quizzes, and earn certificates as you go."],
            ["Instructors", "Build courses with modules, lessons, quizzes, and assignments."],
            ["Org admins", "Invite your team, assign courses, and watch organization-wide progress."],
            ["Platform admins", "Manage every organization, subscriptions, and platform health."],
          ].map(([title, body]) => (
            <div key={title} className="card p-5">
              <h3 className="font-display font-semibold text-ink">{title}</h3>
              <p className="mt-2 text-sm text-slate">{body}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
