import { useOrganizations, usePlatformAnalytics, useSetOrgStatus, useSupportTickets } from "../api/admin";

export default function PlatformAdminDashboard() {
  const { data: orgs } = useOrganizations();
  const { data: analytics } = usePlatformAnalytics();
  const { data: tickets } = useSupportTickets();
  const setStatus = useSetOrgStatus();

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="font-display font-bold text-3xl text-ink">Platform overview</h1>

      {analytics && (
        <div className="grid grid-cols-3 gap-3 mt-6 max-w-lg">
          <Stat label="Active organizations" value={analytics.activeOrganizations} />
          <Stat label="Days tracked" value={analytics.daily.length} />
          <Stat
            label="Total enrollments (30d)"
            value={analytics.daily.reduce((s: number, d: any) => s + Number(d.enrollments), 0)}
          />
        </div>
      )}

      <section className="mt-10">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Organizations</h2>
        <div className="card divide-y divide-line">
          {orgs?.map((o) => (
            <div key={o.id} className="p-3 flex items-center justify-between text-sm">
              <div>
                <p className="font-medium text-ink">{o.name}</p>
                <p className="text-xs text-slate">
                  {o.subscription_plan} plan · invite code {o.invite_code}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${o.status === "active" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                  {o.status}
                </span>
                <button
                  className="btn btn-ghost text-xs py-1"
                  onClick={() => setStatus.mutate({ id: o.id, status: o.status === "active" ? "suspended" : "active" })}
                >
                  {o.status === "active" ? "Suspend" : "Reactivate"}
                </button>
              </div>
            </div>
          ))}
          {!orgs?.length && <p className="p-3 text-sm text-slate">No organizations yet.</p>}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Support tickets</h2>
        <div className="card divide-y divide-line">
          {tickets?.length ? (
            tickets.map((t: any) => (
              <div key={t.id} className="p-3 text-sm">
                <p className="font-medium text-ink">{t.subject}</p>
                <p className="text-xs text-slate mt-0.5">{t.body}</p>
                <span className="text-xs font-semibold text-plum">{t.status}</span>
              </div>
            ))
          ) : (
            <p className="p-3 text-sm text-slate">No tickets.</p>
          )}
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="card p-3 text-center">
      <p className="font-display font-bold text-xl text-ink">{value}</p>
      <p className="text-xs text-slate">{label}</p>
    </div>
  );
}
