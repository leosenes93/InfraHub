import { apiClient } from "@/api/client";

export interface Attachment {
  id: string;
  asset_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  uploaded_by_id: string | null;
  created_at: string;
}

export async function listAttachments(assetId: string): Promise<Attachment[]> {
  const { data } = await apiClient.get<Attachment[]>(`/assets/${assetId}/attachments`);
  return data;
}

export async function uploadAttachment(assetId: string, file: File): Promise<Attachment> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<Attachment>(
    `/assets/${assetId}/attachments`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

export async function deleteAttachment(assetId: string, attachmentId: string): Promise<void> {
  await apiClient.delete(`/assets/${assetId}/attachments/${attachmentId}`);
}

export async function downloadAttachment(assetId: string, attachment: Attachment): Promise<void> {
  const { data } = await apiClient.get(
    `/assets/${assetId}/attachments/${attachment.id}/download`,
    { responseType: "blob" }
  );
  const url = window.URL.createObjectURL(new Blob([data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = attachment.filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
