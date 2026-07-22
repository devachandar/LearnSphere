import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Course } from "../types";

export function useCourses() {
  return useQuery({
    queryKey: ["courses"],
    queryFn: async () => (await client.get<Course[]>("/learning/courses")).data,
  });
}

export function useCourseSearch(q: string) {
  return useQuery({
    queryKey: ["courses", "search", q],
    queryFn: async () => (await client.get<Course[]>("/learning/courses/search", { params: { q } })).data,
    enabled: q.length > 1,
  });
}

export function useMyCourses() {
  return useQuery({
    queryKey: ["courses", "mine"],
    queryFn: async () => (await client.get<Course[]>("/learning/courses/mine")).data,
  });
}

export function useCourse(id?: string) {
  return useQuery({
    queryKey: ["course", id],
    queryFn: async () => (await client.get<Course>(`/learning/courses/${id}`)).data,
    enabled: !!id,
  });
}

export function useCreateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { title: string; description: string; category: string }) =>
      (await client.post<Course>("/learning/courses", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["courses"] }),
  });
}

export function usePublishCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (courseId: string) => (await client.post(`/learning/courses/${courseId}/publish`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["courses"] }),
  });
}

export function useAddModule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { courseId: string; title: string }) =>
      (await client.post(`/learning/courses/${vars.courseId}/modules`, { title: vars.title })).data,
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: ["course", vars.courseId] }),
  });
}

export function useAddLesson() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      moduleId: string;
      courseId: string;
      title: string;
      contentType: string;
      contentUrl?: string;
      textContent?: string;
      durationMinutes?: number;
    }) =>
      (
        await client.post(`/learning/courses/modules/${vars.moduleId}/lessons`, {
          title: vars.title,
          contentType: vars.contentType,
          contentUrl: vars.contentUrl,
          textContent: vars.textContent,
          durationMinutes: vars.durationMinutes,
        })
      ).data,
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: ["course", vars.courseId] }),
  });
}
