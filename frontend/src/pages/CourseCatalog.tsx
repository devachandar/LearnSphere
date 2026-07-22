import { useState } from "react";
import CourseCard from "../components/CourseCard";
import { useCourses, useCourseSearch } from "../api/courses";

export default function CourseCatalog() {
  const [query, setQuery] = useState("");
  const { data: allCourses, isLoading } = useCourses();
  const { data: searchResults, isLoading: searching } = useCourseSearch(query);

  const courses = query.length > 1 ? searchResults : allCourses;
  const loading = query.length > 1 ? searching : isLoading;

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <h1 className="font-display font-bold text-3xl text-ink">Course catalog</h1>
      <p className="text-slate mt-1">Everything published in your organization.</p>

      <input
        className="input mt-6 max-w-md"
        placeholder="Search courses..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {loading ? (
        <p className="text-slate mt-8">Loading courses...</p>
      ) : courses && courses.length ? (
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-5 mt-8">
          {courses.map((c) => (
            <CourseCard key={c.id} course={c} />
          ))}
        </div>
      ) : (
        <p className="text-slate mt-8">No courses match yet.</p>
      )}
    </div>
  );
}
