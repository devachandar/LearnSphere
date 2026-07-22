import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAddPost, useThreadPosts } from "../api/communication";
import { useAuthStore } from "../store/auth";

export default function DiscussionThread() {
  const { threadId } = useParams();
  const { data: posts } = useThreadPosts(threadId);
  const addPost = useAddPost();
  const [body, setBody] = useState("");
  const user = useAuthStore((s) => s.user);

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="font-display font-bold text-2xl text-ink mb-6">Discussion</h1>

      <div className="space-y-3">
        {posts?.map((p: any) => (
          <div key={p.id} className="card p-4">
            <p className="text-sm text-ink">{p.body}</p>
            <p className="text-xs text-slate mt-2">{p.author_id === user?.id ? "You" : "Participant"}</p>
          </div>
        ))}
        {!posts?.length && <p className="text-slate text-sm">No replies yet.</p>}
      </div>

      <div className="mt-6 flex gap-2">
        <input className="input" placeholder="Write a reply..." value={body} onChange={(e) => setBody(e.target.value)} />
        <button
          className="btn btn-primary"
          onClick={async () => {
            if (!body.trim() || !threadId) return;
            await addPost.mutateAsync({ threadId, body });
            setBody("");
          }}
        >
          Reply
        </button>
      </div>
    </div>
  );
}
