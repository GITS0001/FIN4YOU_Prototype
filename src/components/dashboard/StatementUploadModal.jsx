import { useState, useRef } from 'react';
import { Upload, FileText, X, AlertCircle, CheckCircle2, ArrowRight, ShieldCheck, Loader2, Trash2 } from 'lucide-react';
import { parseStatementPreview, confirmStatementImport } from '../../api/fin4youApi';

export default function StatementUploadModal({ isOpen, onClose, onSuccess, currencySymbol = '₹' }) {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [importSuccess, setImportSuccess] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    setPreviewData(null);
    setImportSuccess(null);

    if (!selectedFile) return;

    const fn = selectedFile.name.lowerCase ? selectedFile.name.toLowerCase() : selectedFile.name;
    const ext = fn.split('.').pop();
    if (ext !== 'csv' && ext !== 'pdf') {
      setError('Invalid file format. Only PDF and CSV bank statements are supported.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10MB limit. Please upload a smaller statement file.');
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreviewData(null);
    setError(null);
    setImportSuccess(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleParsePreview = async () => {
    if (!file || loading) return;
    setLoading(true);
    setError(null);
    setPreviewData(null);

    try {
      const data = await parseStatementPreview(file);
      setPreviewData(data);
    } catch (err) {
      setError(err.message || 'Failed to parse statement. Please ensure it is a valid CSV or readable PDF.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!previewData || !previewData.transactions || confirming) return;
    setConfirming(true);
    setError(null);

    try {
      const res = await confirmStatementImport(previewData.transactions);
      setImportSuccess(res.message || `Successfully imported ${res.inserted_count} new transactions.`);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        onClose();
      }, 1800);
    } catch (err) {
      setError(err.message || 'Failed to save transactions to database.');
    } finally {
      setConfirming(false);
    }
  };

  const formatSize = (bytes) => {
    if (!bytes) return '0 KB';
    if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto animate-fade-in">
      <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 w-full max-w-3xl overflow-hidden my-6">
        {/* Header */}
        <div className="p-5 sm:p-6 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-blue-50 text-[#2563EB] grid place-items-center font-bold border border-blue-100">
              <Upload size={20} />
            </div>
            <div>
              <h3 className="font-bold text-base text-gray-900 font-display">
                {previewData ? 'Import Preview & Validation' : 'Upload Bank Statement'}
              </h3>
              <p className="text-xs text-gray-500">
                {previewData ? 'Review detected transactions before persisting to ledger' : 'Upload your bank statement (PDF or CSV)'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 sm:p-6 space-y-5 max-h-[calc(85vh-130px)] overflow-y-auto">
          {error && (
            <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-start gap-2.5 leading-relaxed">
              <AlertCircle size={16} className="text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Extraction Warning: </span>
                {error}
              </div>
            </div>
          )}

          {importSuccess && (
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-3">
              <CheckCircle2 size={20} className="text-emerald-600 flex-shrink-0" />
              <div>
                <div className="font-bold text-sm">{importSuccess}</div>
                <div className="text-[11px] text-emerald-700">Updating ledger and cash flow analytics...</div>
              </div>
            </div>
          )}

          {!previewData && !importSuccess && (
            <>
              {/* Dropzone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-3xl p-8 text-center transition-all cursor-pointer ${
                  isDragging
                    ? 'border-[#2563EB] bg-blue-50/50 scale-[0.99]'
                    : file
                    ? 'border-blue-300 bg-blue-50/20'
                    : 'border-gray-200 bg-gray-50/60 hover:bg-white hover:border-gray-300'
                }`}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.pdf,text/csv,application/pdf"
                  onChange={handleFileSelect}
                  onClick={(e) => {
                    e.target.value = null;
                  }}
                  className="hidden"
                />

                {!file ? (
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-12 h-12 rounded-2xl bg-blue-100 text-[#2563EB] grid place-items-center mb-1">
                      <FileText size={24} />
                    </div>
                    <span className="text-sm font-bold text-gray-900">
                      Upload your bank statement (PDF or CSV)
                    </span>
                    <span className="text-xs text-gray-500 max-w-md">
                      Drag & drop your file here, or click to browse. Supports PDF bank statements and standard CSV files up to 10MB.
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center justify-between p-3.5 bg-white rounded-2xl border border-blue-200 shadow-2xs">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-blue-600 text-white font-black text-xs grid place-items-center uppercase">
                        {file.name.split('.').pop()}
                      </div>
                      <div className="text-left">
                        <div className="text-xs font-bold text-gray-900 truncate max-w-[280px]">
                          {file.name}
                        </div>
                        <div className="text-[11px] text-gray-400 font-medium">
                          {formatSize(file.size)} • Ready for parsing
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          fileInputRef.current?.click();
                        }}
                        className="px-3 py-1.5 text-xs font-semibold text-[#2563EB] bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors"
                      >
                        Change File
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveFile();
                        }}
                        className="p-2 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                        title="Remove file"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Instructions */}
              <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 text-xs text-gray-600 space-y-1.5">
                <div className="font-bold text-gray-800 flex items-center gap-1.5">
                  <ShieldCheck size={14} className="text-emerald-600" />
                  <span>Secure & Private Processing</span>
                </div>
                <p className="leading-relaxed text-[11px]">
                  Files are parsed locally on our secure server. Transactions are validated and deduplicated before being added to your ledger.
                </p>
              </div>
            </>
          )}

          {/* Import Preview Summary & Table */}
          {previewData && !importSuccess && (
            <div className="space-y-4">
              {/* Summary Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-gray-50 rounded-2xl border border-gray-100">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Total Detected</div>
                  <div className="text-lg font-black text-gray-900 font-display">{previewData.total_detected}</div>
                </div>
                <div className="p-3 bg-emerald-50/60 rounded-2xl border border-emerald-100">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">Total Credits</div>
                  <div className="text-lg font-black text-emerald-700 font-display">
                    {currencySymbol}{previewData.total_credits.toLocaleString()}
                  </div>
                </div>
                <div className="p-3 bg-rose-50/60 rounded-2xl border border-rose-100">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-rose-700">Total Debits</div>
                  <div className="text-lg font-black text-rose-700 font-display">
                    {currencySymbol}{previewData.total_debits.toLocaleString()}
                  </div>
                </div>
                <div className="p-3 bg-blue-50/60 rounded-2xl border border-blue-100">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-blue-700">Net Cash Flow</div>
                  <div className="text-lg font-black text-blue-700 font-display">
                    {previewData.net_cash_flow >= 0 ? '+' : ''}{currencySymbol}{previewData.net_cash_flow.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Status Bar */}
              <div className="p-3 bg-gray-50 rounded-2xl border border-gray-100 flex items-center justify-between text-xs">
                <div className="text-gray-600">
                  Date Range: <strong className="text-gray-900">{previewData.date_range}</strong>
                </div>
                {previewData.duplicate_count > 0 && (
                  <div className="px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 font-bold text-[11px]">
                    {previewData.duplicate_count} Duplicate(s) Skipped
                  </div>
                )}
              </div>

              {/* Preview Table */}
              <div className="border border-gray-200 rounded-2xl overflow-hidden max-h-60 overflow-y-auto">
                <table className="min-w-full text-xs text-left">
                  <thead className="bg-gray-100/80 sticky top-0 font-bold text-gray-700">
                    <tr>
                      <th className="p-2.5">Date</th>
                      <th className="p-2.5">Description</th>
                      <th className="p-2.5">Type</th>
                      <th className="p-2.5 text-right">Amount</th>
                      <th className="p-2.5">Category</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 bg-white">
                    {previewData.transactions.slice(0, 50).map((t, idx) => (
                      <tr key={idx} className="hover:bg-blue-50/30">
                        <td className="p-2.5 font-mono text-gray-600 whitespace-nowrap">{t.event_date}</td>
                        <td className="p-2.5 font-medium text-gray-900 max-w-xs truncate">{t.description}</td>
                        <td className="p-2.5">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              t.direction === 'INFLOW' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                            }`}
                          >
                            {t.direction}
                          </span>
                        </td>
                        <td className="p-2.5 text-right font-bold text-gray-900 font-mono">
                          {currencySymbol}{t.amount.toLocaleString()}
                        </td>
                        <td className="p-2.5 text-gray-500">{t.category || 'Uncategorized'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 sm:p-5 border-t border-gray-100 bg-gray-50/50 flex items-center justify-between">
          <button
            type="button"
            onClick={onClose}
            disabled={loading || confirming}
            className="px-4 py-2.5 text-xs font-bold text-gray-600 hover:text-gray-900 rounded-xl hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>

          {!previewData ? (
            <button
              type="button"
              onClick={handleParsePreview}
              disabled={!file || loading}
              className="px-5 py-2.5 bg-[#2563EB] disabled:bg-gray-200 text-white disabled:text-gray-400 font-bold rounded-xl shadow-xs hover:bg-[#1D4ED8] transition-all flex items-center gap-2 text-xs"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Parsing Statement...</span>
                </>
              ) : (
                <>
                  <span>Parse & Preview</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPreviewData(null)}
                disabled={confirming}
                className="px-3.5 py-2 text-xs font-bold text-gray-700 bg-white border border-gray-200 rounded-xl hover:bg-gray-50"
              >
                Re-upload File
              </button>
              <button
                type="button"
                onClick={handleConfirmImport}
                disabled={confirming}
                className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-bold rounded-xl shadow-xs transition-all flex items-center gap-2 text-xs"
              >
                {confirming ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Confirming Import...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={16} />
                    <span>Confirm & Ingest {previewData.valid_count} Records</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
