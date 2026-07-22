import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useRegister } from "../api/auth";
import { Role } from "../types";

const ROLES: { value: Role; label: string }[] = [
  { value: "org_admin", label: "I'm starting a new organization" },
  { value: "instructor", label: "I'm an instructor joining one" },
  { value: "learner", label: "I'm a learner joining one" },
];

export default function Register() {
  const [role, setRole] = useState<Role>("learner");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const register = useRegister();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await register.mutateAsync({
        email,
        password,
        fullName,
        role,
        organizationName: role === "org_admin" ? organizationName : undefined,
        inviteCode: role !== "org_admin" ? inviteCode : undefined,
      });
      navigate(role === "org_admin" ? "/organization" : "/");
    } catch {
      // surfaced via register.isError
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-16 px-6">
      <div className="card p-8">
        <h1 className="font-display font-bold text-2xl text-ink">Create an account</h1>
        <p className="text-sm text-slate mt-1 mb-6">Every organization's data stays completely separate.</p>

        {register.isError && (
          <div className="mb-4 text-sm bg-red-50 text-red-700 border border-red-200 rounded-lg px-3 py-2">
            {(register.error as any)?.response?.data?.error || "Could not create your account."}
          </div>
        )}

        <div className="space-y-2 mb-4">
          {ROLES.map((r) => (
            <button
              key={r.value}
              type="button"
              onClick={() => setRole(r.value)}
              className={`w-full text-left text-sm rounded-lg border px-3 py-2 transition ${
                role === r.value ? "border-plum bg-plum/5 text-ink font-semibold" : "border-line text-slate"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Full name</label>
            <input className="input" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
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
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {role === "org_admin" ? (
            <div>
              <label className="label">Organization name</label>
              <input
                className="input"
                required
                placeholder="e.g. Acme University"
                value={organizationName}
                onChange={(e) => setOrganizationName(e.target.value)}
              />
            </div>
          ) : (
            <div>
              <label className="label">Invite code</label>
              <input
                className="input"
                required
                placeholder="From your organization admin"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
              />
            </div>
          )}

          <button type="submit" className="btn btn-primary w-full" disabled={register.isPending}>
            {register.isPending ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-sm text-slate text-center mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-plum font-semibold">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
