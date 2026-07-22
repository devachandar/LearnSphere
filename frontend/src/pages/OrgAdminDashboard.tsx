import { useState } from "react";
import { useOrganizationMembers } from "../api/auth";
import { useMyOrganization, useOrgAnalytics, useCreateSupportTicket } from "../api/admin";

export default function OrgAdminDashboard() {
  const { data: org } = useMyOrganization();
  const { data: members } = useOrganizationMembers();
  const { data: analytics } = useOrgAnalytics();
  const createTicket = useCreateSupportTicket();
  const [ticket, setTicket] = useState({ subject: "", body: "" });
  const [sent, setSent] = useState(false);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="font-display font-bold text-3xl text-ink">{org?.name || "Your organization"}</h1>

      {org && (
        <div className="card p-4 mt-4 inline-flex items-center gap-3">
          <span className="text-sm text-slate">Invite code:</span>
          <code className="font-mono font-bold text-plum">{org.invite_code}</code>
          <span className="text-xs text-slate">Share this with instructors and learners to join.</span>
        </div>
      )}

      {analytics && (
        <div className="grid grid-cols-3 gap-3 mt-6 max-w-lg">
          <Stat label="New users (30d)" value={analytics.totals.newUsers} />
          <Stat label="Enrollments (30d)" value={analytics.totals.enrollments} />
          <Stat label="Certificates (30d)" value={analytics.totals.certificatesIssued} />
        </div>
      )}

      <section className="mt-10">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Members</h2>
        <div className="card divide-y divide-line">
          {members?.length ? (
            members.map((m: any) => (
              <div key={m.id} className="p-3 flex justify-between text-sm">
                <span className="text-ink">{m.full_name} <span className="text-slate">({m.email})</span></span>
                <span className="capitalize text-slate">{m.role}</span>
              </div>
            ))
          ) : (
            <p className="p-3 text-sm text-slate">No members yet.</p>
          )}
        </div>
      </section>

      <section className="mt-10 max-w-lg">
        <h2 className="font-display font-semibold text-lg text-ink mb-3">Contact platform support</h2>
        {sent ? (
          <p className="text-sm text-plum font-semibold">Ticket submitted - the platform team will follow up.</p>
        ) : (
          <div className="card p-4 space-y-2">
            <input className="input" placeholder="Subject" value={ticket.subject} onChange={(e) => setTicket({ ...ticket, subject: e.target.value })} />
            <textarea className="input" rows={3} placeholder="Describe the issue" value={ticket.body} onChange={(e) => setTicket({ ...ticket, body: e.target.value })} />
            <button
              className="btn btn-primary text-sm"
              onClick={async () => {
                await createTicket.mutateAsync(ticket);
                setSent(true);
              }}
              disabled={!ticket.subject || !ticket.body}
            >
              Submit ticket
            </button>
          </div>
        )}
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
