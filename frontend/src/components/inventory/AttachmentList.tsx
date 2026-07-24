import { useRef, useState } from "react";

import { downloadAttachment, formatFileSize, type Attachment } from "@/api/attachments";

interface AttachmentListProps {
  attachments: Attachment[];
  assetId: string;
  canUpload: boolean;
  canDelete: boolean;
  isUploading: boolean;
  uploadError: string | null;
  onUpload: (file: File) => void;
  onDelete: (attachment: Attachment) => void;
}

export function AttachmentList({
  attachments,
  assetId,
  canUpload,
  canDelete,
  isUploading,
  uploadError,
  onUpload,
  onDelete,
}: AttachmentListProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  function handleFileSelected() {
    const file = fileInputRef.current?.files?.[0];
    if (file) {
      onUpload(file);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDownload(attachment: Attachment) {
    setDownloadingId(attachment.id);
    try {
      await downloadAttachment(assetId, attachment);
    } finally {
      setDownloadingId(null);
    }
  }

  return (
    <div className="space-y-4">
      {canUpload && (
        <div>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelected}
            disabled={isUploading}
            className="text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-brand-700 hover:file:bg-brand-100"
          />
          <p className="mt-1 text-xs text-slate-400">
            Imagens (PNG/JPEG/SVG), PDF ou texto/Markdown, até 10MB.
          </p>
          {uploadError && <p className="mt-1 text-sm text-red-600">{uploadError}</p>}
        </div>
      )}

      {attachments.length === 0 ? (
        <p className="text-sm text-slate-500">Nenhum anexo enviado ainda.</p>
      ) : (
        <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
          {attachments.map((attachment) => (
            <li key={attachment.id} className="flex items-center justify-between px-4 py-3">
              <div>
                <p className="text-sm font-medium text-slate-900">{attachment.filename}</p>
                <p className="text-xs text-slate-500">
                  {formatFileSize(attachment.size_bytes)} ·{" "}
                  {new Date(attachment.created_at).toLocaleString("pt-BR")}
                </p>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <button
                  onClick={() => handleDownload(attachment)}
                  disabled={downloadingId === attachment.id}
                  className="font-medium text-brand-600 hover:text-brand-700 disabled:opacity-60"
                >
                  Baixar
                </button>
                {canDelete && (
                  <button
                    onClick={() => onDelete(attachment)}
                    className="font-medium text-red-600 hover:text-red-700"
                  >
                    Excluir
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
