import { apiClient } from "@/api/client";

export interface DockerContainer {
  id: string;
  name: string;
  image: string;
  status: string;
  state: string;
  created_at: string | null;
  ports: string[];
}

export async function listDockerContainers(): Promise<DockerContainer[]> {
  const { data } = await apiClient.get<DockerContainer[]>("/docker/containers");
  return data;
}
