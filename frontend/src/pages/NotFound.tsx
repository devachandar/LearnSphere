import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="max-w-md mx-auto px-6 py-24 text-center">
      <span className="text-xs font-semibold text-plum uppercase tracking-wide">404</span>
      <h1 className="font-display font-bold text-2xl text-ink mt-2">This lesson doesn't exist.</h1>
      <Link to="/" className="btn btn-primary mt-6 inline-flex">
        Back home
      </Link>
    </div>
  );
}
