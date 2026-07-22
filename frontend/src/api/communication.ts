import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Notification } from "../types";

export function useAnnouncements(courseId?: string) {
  return useQuery({
    queryKey: ["announcements", courseId],
    queryFn: async () => (await client.get(`/communication/announcements/course/${courseId}`)).data,
    enabled: !!courseId,
  });
}

export function useCreateAnnouncement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { courseId: string; title: string; body: string }) =>
      (await client.post("/communication/announcements", vars)).data,
    onSuccess: (_d, vars) => qc.invalidateQueries({ queryKey: ["announcements", vars.courseId] }),
  });
}

export function useDiscussionThreads(courseId?: string) {
  return useQuery({
    queryKey: ["discussions", courseId],
    queryFn: async () => (await client.get(`/communication/discussions/course/${courseId}`)).data,
    enabled: !!courseId,
  });
}

export function useCreateThread() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { courseId: string; title: string }) =>
      (await client.post("/communication/discussions", vars)).data,
    onSuccess: (_d, vars) => qc.invalidateQueries({ queryKey: ["discussions", vars.courseId] }),
  });
}

export function useThreadPosts(threadId?: string) {
  return useQuery({
    queryKey: ["thread-posts", threadId],
    queryFn: async () => (await client.get(`/communication/discussions/${threadId}/posts`)).data,
    enabled: !!threadId,
  });
}

export function useAddPost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { threadId: string; body: string }) =>
      (await client.post(`/communication/discussions/${vars.threadId}/posts`, { body: vars.body })).data,
    onSuccess: (_d, vars) => qc.invalidateQueries({ queryKey: ["thread-posts", vars.threadId] }),
  });
}

export function useMyNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: async () => (await client.get<Notification[]>("/communication/notifications/mine")).data,
    refetchInterval: 30_000,
  });
}
