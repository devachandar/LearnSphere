import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Assignment, Quiz } from "../types";

export function useCourseQuizzes(courseId?: string) {
  return useQuery({
    queryKey: ["quizzes", courseId],
    queryFn: async () => (await client.get(`/assessment/quizzes/course/${courseId}`)).data,
    enabled: !!courseId,
  });
}

export function useQuiz(id?: string) {
  return useQuery({
    queryKey: ["quiz", id],
    queryFn: async () => (await client.get<Quiz>(`/assessment/quizzes/${id}`)).data,
    enabled: !!id,
  });
}

export function useCreateQuiz() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: {
      courseId: string;
      title: string;
      passingScore: number;
      questions: { questionText: string; questionType: string; options: string[]; correctAnswer: string; points: number }[];
    }) => (await client.post("/assessment/quizzes", vars)).data,
    onSuccess: (_d, vars) => qc.invalidateQueries({ queryKey: ["quizzes", vars.courseId] }),
  });
}

export function useSubmitQuiz() {
  return useMutation({
    mutationFn: async (vars: { quizId: string; answers: { questionId: string; answerText: string }[] }) =>
      (await client.post(`/assessment/quizzes/${vars.quizId}/submit`, { answers: vars.answers })).data,
  });
}

export function useCourseAssignments(courseId?: string) {
  return useQuery({
    queryKey: ["assignments", courseId],
    queryFn: async () => (await client.get<Assignment[]>(`/assessment/assignments/course/${courseId}`)).data,
    enabled: !!courseId,
  });
}

export function useCreateAssignment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { courseId: string; title: string; description: string; maxPoints: number }) =>
      (await client.post("/assessment/assignments", vars)).data,
    onSuccess: (_d, vars) => qc.invalidateQueries({ queryKey: ["assignments", vars.courseId] }),
  });
}

export function useSubmitAssignment() {
  return useMutation({
    mutationFn: async (vars: { assignmentId: string; textContent: string }) =>
      (await client.post(`/assessment/assignments/${vars.assignmentId}/submit`, { textContent: vars.textContent })).data,
  });
}
