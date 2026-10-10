import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle, X, Loader2 } from 'lucide-react';
import { useSelectedUser } from '../../context/UserContext';

const API_BASE = 'http://127.0.0.1:8000/api';

interface UploadResponse {
  message: string;
  total_parsed: number;
  data_quality_metrics: Record<string, number>;
}

export const StatementUpload: React.FC<{ onUploadSuccess: () => void }> = ({ onUploadSuccess }) => {
  const { selectedUserId } = useSelectedUser();
  const [isOpen, setIsOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [result, setResult] = useState<UploadResponse | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus('idle');
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus('uploading');
    setErrorMsg('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/statements/upload?user_id=${selectedUserId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload statement');
      }

      const data = await response.json();
      setResult(data);
      setStatus('success');
      onUploadSuccess();
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred during upload.');
      setStatus('error');
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setFile(null);
    setStatus('idle');
    setResult(null);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)} className="btn-primary">
        <Upload size={16} className="mr-2" />
        Upload Statement
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card-bg w-full max-w-md rounded-2xl shadow-xl border border-border p-6 relative">
            <button
              onClick={handleClose}
              className="absolute right-4 top-4 text-muted hover:text-primary-dark transition-colors"
            >
              <X size={20} />
            </button>

            <h2 className="text-xl font-bold text-primary-dark mb-2">Upload Bank Statement</h2>
            <p className="text-sm text-muted mb-6">Upload a CSV file to update your financial intelligence.</p>

            <div className="space-y-4">
              {!file ? (
                <div
                  className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center text-center hover:border-primary-accent/50 hover:bg-primary-accent/5 transition-colors cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="w-12 h-12 bg-primary-accent/10 rounded-full flex items-center justify-center text-primary-accent mb-3">
                    <FileText size={24} />
                  </div>
                  <p className="text-sm font-medium text-primary-dark">Click to select CSV</p>
                  <p className="text-xs text-muted mt-1">or drag and drop here</p>
                  <input
                    type="file"
                    accept=".csv"
                    className="hidden"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                  />
                </div>
              ) : (
                <div className="bg-background border border-border rounded-xl p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <FileText size={20} className="text-primary-accent flex-shrink-0" />
                    <p className="text-sm font-medium text-primary-dark truncate">{file.name}</p>
                  </div>
                  {status === 'idle' && (
                    <button
                      onClick={() => setFile(null)}
                      className="text-muted hover:text-danger ml-2 p-1"
                    >
                      <X size={16} />
                    </button>
                  )}
                </div>
              )}

              {status === 'error' && (
                <div className="p-3 bg-danger/10 border border-danger/20 rounded-lg flex items-start gap-2 text-danger">
                  <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
                  <p className="text-xs">{errorMsg}</p>
                </div>
              )}

              {status === 'success' && result && (
                <div className="p-4 bg-positive/10 border border-positive/20 rounded-lg text-positive">
                  <div className="flex items-center gap-2 mb-2 font-medium">
                    <CheckCircle size={16} />
                    <p className="text-sm">Statement Processed Successfully</p>
                  </div>
                  <p className="text-xs text-positive/80 ml-6">
                    Parsed {result.total_parsed} transactions.<br/>
                    Categorized using ML intelligence engine.
                  </p>
                </div>
              )}

              <div className="pt-4 flex justify-end gap-3 border-t border-border mt-6">
                <button
                  onClick={handleClose}
                  className="btn-secondary"
                  disabled={status === 'uploading'}
                >
                  {status === 'success' ? 'Close' : 'Cancel'}
                </button>
                {status !== 'success' && (
                  <button
                    onClick={handleUpload}
                    className="btn-primary"
                    disabled={!file || status === 'uploading'}
                  >
                    {status === 'uploading' ? (
                      <>
                        <Loader2 size={16} className="animate-spin mr-2" />
                        Processing...
                      </>
                    ) : (
                      'Upload & Analyze'
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
