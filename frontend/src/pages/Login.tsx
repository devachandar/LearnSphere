import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLogin } from "../api/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login.mutateAsync({ email, password });
      navigate("/");
    } catch {
      // surfaced below via login.isError
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-16 px-6">
      <div className="card p-8">
        <h1 className="font-display font-bold text-2xl text-ink">Sign in</h1>
        <p className="text-sm text-slate mt-1 mb-6">Continue learning, teaching, or managing your organization.</p>

        {login.isError && (
          <div className="mb-4 text-sm bg-red-50 text-red-700 border border-red-200 rounded-lg px-3 py-2">
            {(login.error as any)?.response?.data?.error || "Could not sign in."}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              className="input"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary w-full" disabled={login.isPending}>
            {login.isPending ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-sm text-slate text-center mt-6">
          New to LearnSphere?{" "}
          <Link to="/register" className="text-plum font-semibold">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
