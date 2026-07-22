import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Certificate, Enrollment } from "../types";

export function useMyEnrollments() {
  return useQuery({
    queryKey: ["enrollments", "mine"],
    queryFn: async () => (await client.get<Enrollment[]>("/learning/enrollments/mine")).data,
  });
}

export function useEnroll() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (courseId: string) => (await client.post(`/learning/enrollments/${courseId}`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["enrollments"] }),
  });
}

export function useCompleteLesson() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (lessonId: string) => (await client.post(`/learning/enrollments/lessons/${lessonId}/complete`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["enrollments"] }),
  });
}

export function useMyCertificates() {
  return useQuery({
    queryKey: ["certificates", "mine"],
    queryFn: async () => (await client.get<Certificate[]>("/learning/enrollments/certificates/mine")).data,
  });
}

export function useCourseEnrollments(courseId?: string) {
  return useQuery({
    queryKey: ["enrollments", "course", courseId],
    queryFn: async () => (await client.get(`/learning/enrollments/course/${courseId}`)).data,
    enabled: !!courseId,
  });
}
