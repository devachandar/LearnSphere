import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";
import { useLogout } from "../api/auth";

export default function Navbar() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-line">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-display font-bold text-lg text-ink">
          <span className="w-6 h-6 rounded-full bg-gradient-to-br from-plum to-coral" />
          LearnSphere
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate">
          <Link to="/catalog" className="hover:text-ink">
            Catalog
          </Link>
          {user?.role === "learner" && (
            <Link to="/my-learning" className="hover:text-ink">
              My learning
            </Link>
          )}
          {(user?.role === "instructor" || user?.role === "org_admin") && (
            <Link to="/instructor" className="hover:text-ink">
              Instructor
            </Link>
          )}
          {user?.role === "org_admin" && (
            <Link to="/organization" className="hover:text-ink">
              Organization
            </Link>
          )}
          {user?.role === "platform_admin" && (
            <Link to="/platform" className="hover:text-ink">
              Platform
            </Link>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden sm:block text-sm text-slate">{user.fullName}</span>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">
                Sign in
              </Link>
              <Link to="/register" className="btn btn-primary">
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
