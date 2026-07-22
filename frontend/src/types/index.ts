export type Role = "platform_admin" | "org_admin" | "instructor" | "learner";

export interface AuthUser {
  id: string;
  email: string;
  fullName: string;
  role: Role;
  organizationId: string | null;
}

export interface Lesson {
  id: string;
  title: string;
  content_type: "video" | "text" | "pdf";
  content_url: string | null;
  text_content: string | null;
  duration_minutes: number;
  sort_order: number;
}

export interface Module {
  id: string;
  title: string;
  sort_order: number;
  lessons: Lesson[];
}

export interface Course {
  id: string;
  organization_id: string;
  instructor_id: string;
  title: string;
  description: string;
  category: string;
  status: "draft" | "published" | "archived";
  thumbnail_url: string | null;
  modules: Module[];
  created_at: string;
}

export interface Enrollment {
  id: string;
  course_id: string;
  course_title: string;
  thumbnail_url: string | null;
  learner_id: string;
  status: "active" | "completed" | "dropped";
  progressPercent: number;
  enrolled_at: string;
  completed_at: string | null;
}

export interface Certificate {
  id: string;
  course_id: string;
  course_title: string;
  learner_id: string;
  issued_at: string;
}

export interface Quiz {
  id: string;
  course_id: string;
  title: string;
  passing_score: number;
  questions: QuizQuestion[];
}

export interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: "multiple_choice" | "true_false";
  options: string[];
  points: number;
}

export interface Assignment {
  id: string;
  course_id: string;
  title: string;
  description: string;
  due_date: string | null;
  max_points: number;
}

export interface Organization {
  id: string;
  name: string;
  invite_code: string;
  subscription_plan: string;
  status: "active" | "suspended";
  created_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
}
