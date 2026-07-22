import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import RequireAuth from "./components/RequireAuth";
import { useBootstrapAuth } from "./api/auth";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CourseCatalog from "./pages/CourseCatalog";
import CourseDetail from "./pages/CourseDetail";
import DiscussionThread from "./pages/DiscussionThread";
import InstructorDashboard from "./pages/InstructorDashboard";
import InstructorCourseBuilder from "./pages/InstructorCourseBuilder";
import LearnerDashboard from "./pages/LearnerDashboard";
import OrgAdminDashboard from "./pages/OrgAdminDashboard";
import PlatformAdminDashboard from "./pages/PlatformAdminDashboard";
import NotFound from "./pages/NotFound";

export default function App() {
  useBootstrapAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/catalog" element={<CourseCatalog />} />
          <Route path="/courses/:id" element={<CourseDetail />} />
          <Route path="/discussions/:threadId" element={<DiscussionThread />} />
          <Route
            path="/my-learning"
            element={
              <RequireAuth roles={["learner"]}>
                <LearnerDashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/instructor"
            element={
              <RequireAuth roles={["instructor", "org_admin"]}>
                <InstructorDashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/instructor/courses/:id"
            element={
              <RequireAuth roles={["instructor", "org_admin"]}>
                <InstructorCourseBuilder />
              </RequireAuth>
            }
          />
          <Route
            path="/organization"
            element={
              <RequireAuth roles={["org_admin"]}>
                <OrgAdminDashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/platform"
            element={
              <RequireAuth roles={["platform_admin"]}>
                <PlatformAdminDashboard />
              </RequireAuth>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}
