import { Link } from "react-router-dom";
import { Course } from "../types";

const CATEGORY_COLORS: Record<string, string> = {
  general: "bg-plum/10 text-plum",
  engineering: "bg-blue-100 text-blue-700",
  design: "bg-pink-100 text-pink-700",
  business: "bg-amber-100 text-amber-700",
};

export default function CourseCard({ course }: { course: Course }) {
  const colorClass = CATEGORY_COLORS[course.category] || "bg-plum/10 text-plum";
  return (
    <Link
      to={`/courses/${course.id}`}
      className="card overflow-hidden hover:shadow-lg hover:-translate-y-0.5 transition block"
    >
      <div className="h-32 bg-gradient-to-br from-ink to-plum flex items-center justify-center">
        {course.thumbnail_url ? (
          <img src={course.thumbnail_url} alt={course.title} className="w-full h-full object-cover" />
        ) : (
          <span className="text-white/70 font-display text-2xl">{course.title.slice(0, 1)}</span>
        )}
      </div>
      <div className="p-4">
        <span className={`inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full ${colorClass}`}>
          {course.category}
        </span>
        <h3 className="mt-2 font-display font-semibold text-ink text-[15px]">{course.title}</h3>
        <p className="mt-1 text-sm text-slate line-clamp-2">{course.description}</p>
      </div>
    </Link>
  );
}
