import React, { useState, useRef, useEffect } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  Scale, 
  Sparkles, 
  Layers, 
  Calendar, 
  DollarSign, 
  ShieldAlert, 
  ArrowRight,
  Loader2
} from 'lucide-react';
import { uploadDocument, analyzeDocument } from '../services/api';
import { useToast } from '../context/ToastContext';

export default function NewAnalysisPage({ onNavigateToResults, onNavigateToViewer }) {
  const { showToast } = useToast();
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [errorMessage, setErrorMessage] = useState(null);

  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB

  const validateFile = (selectedFile) => {
    if (!selectedFile) return false;
    const ext = selectedFile.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setErrorMessage('Unsupported format. Please select a valid PDF or DOCX document.');
      return false;
    }
    if (selectedFile.size > MAX_FILE_SIZE) {
      setErrorMessage('File is too large. Maximum supported document size is 25 MB.');
      return false;
    }
    setErrorMessage(null);
    return true;
  };

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected && validateFile(selected)) {
      setFile(selected);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped && validateFile(dropped)) {
      setFile(dropped);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const stages = [
    'Extracting document text stream & canonical tokens...',
    'Normalizing legal citations, references & terminology...',
    'Identifying domain keywords via hybrid statistical scoring...',
    'Extracting named legal entities, parties & authorities...',
    'Detecting contractual clauses, covenants & obligations...',
    'Finalizing structured intelligence summary & report...'
  ];

  // Stage progression timer during analysis
  useEffect(() => {
    let interval;
    if (isProcessing) {
      setProcessingStage(0);
      interval = setInterval(() => {
        setProcessingStage((prev) => (prev < stages.length - 1 ? prev + 1 : prev));
      }, 900);
    }
    return () => clearInterval(interval);
  }, [isProcessing]);

  const handleStartAnalysis = async () => {
    if (!file) return;

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      // 1. Upload Document
      const uploadedDoc = await uploadDocument(file);
      const docId = uploadedDoc.id;

      // 2. Execute NLP Analysis Pipeline
      const analysisResult = await analyzeDocument(docId);
      const analysisId = analysisResult.analysis_id || analysisResult.id;

      showToast('Document analyzed successfully.', 'success');

      // 3. Navigate directly to the results summary
      if (onNavigateToResults) {
        onNavigateToResults(analysisId, docId);
      }
    } catch (err) {
      console.error('Analysis error:', err);
      const detail = err.response?.data?.detail || 'Document analysis failed. Please verify the document is a readable legal contract or brief.';
      setErrorMessage(detail);
      showToast(detail, 'error');
      setIsProcessing(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Heading */}
      <div className="text-center space-y-2">
        <h1 className="font-display text-3xl sm:text-4xl text-midnight font-bold tracking-tight">
          Analyze a Legal Document
        </h1>
        <p className="text-[15px] text-charcoal-muted max-w-xl mx-auto">
          Upload a PDF or DOCX file and LexExtract will identify important legal terms, entities, obligations, and clauses automatically.
        </p>
      </div>

      {/* Main Workspace Card */}
      <div className="bg-white border border-line p-8 sm:p-10 shadow-subtle space-y-6">
        
        {/* Error notification if any */}
        {errorMessage && (
          <div className="p-4 bg-legalred-subtle border border-legalred-border text-legalred text-[13px] flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 text-legalred" />
              <span>{errorMessage}</span>
            </div>
            <button 
              onClick={() => setErrorMessage(null)} 
              className="p-1 hover:opacity-80"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Processing State: Multi-stage NLP Pipeline view */}
        {isProcessing ? (
          <div className="p-10 sm:p-14 text-center space-y-6 max-w-lg mx-auto">
            <div className="w-14 h-14 rounded-full bg-midnight/5 border border-line flex items-center justify-center mx-auto text-midnight">
              <Loader2 className="w-7 h-7 animate-spin text-midnight" />
            </div>

            <div className="space-y-2">
              <h3 className="font-display text-2xl text-midnight font-bold">
                Analyzing Document...
              </h3>
              <p className="text-[13px] text-charcoal-muted font-mono truncate max-w-sm mx-auto">
                {file?.name} ({formatFileSize(file?.size)})
              </p>
            </div>

            {/* Stages checklist */}
            <div className="text-left bg-ivory border border-line p-5 space-y-3 font-sans text-[13px]">
              {stages.map((stg, idx) => {
                const isDone = idx < processingStage;
                const isCurrent = idx === processingStage;
                return (
                  <div key={idx} className="flex items-center space-x-3">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-legalgreen shrink-0" />
                    ) : isCurrent ? (
                      <div className="w-4 h-4 rounded-full border-2 border-midnight border-t-transparent animate-spin shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-line-dark shrink-0" />
                    )}
                    <span className={isDone ? 'text-charcoal font-medium' : isCurrent ? 'text-midnight font-bold' : 'text-charcoal-subtle'}>
                      {stg}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ) : !file ? (
          /* Drag and drop selection area */
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              border-2 border-dashed p-10 sm:p-14 text-center cursor-pointer transition-all
              ${isDragging 
                ? 'border-midnight bg-ivory-subtle scale-[1.01]' 
                : 'border-line-dark/70 hover:border-midnight bg-ivory/40 hover:bg-ivory'}
            `}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
            />

            <div className="w-14 h-14 rounded-full bg-white border border-line shadow-subtle flex items-center justify-center mx-auto text-midnight mb-4">
              <UploadCloud className="w-7 h-7 text-midnight" />
            </div>

            <div className="space-y-1.5">
              <p className="text-[16px] font-semibold text-midnight">
                Drop your legal document here
              </p>
              <p className="text-[14px] text-charcoal-muted">
                or <span className="text-crimson font-semibold hover:underline">browse files</span> from your computer
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-line/60 inline-flex items-center space-x-4 text-[12px] text-charcoal-muted">
              <span>PDF or DOCX</span>
              <span>•</span>
              <span>Maximum 25 MB</span>
              <span>•</span>
              <span>Text &amp; contract extraction</span>
            </div>
          </div>
        ) : (
          /* File Selected: Preview & Analyze CTA */
          <div className="space-y-6">
            <div className="p-5 bg-ivory border border-line flex items-center justify-between">
              <div className="flex items-center space-x-3.5">
                <div className="w-10 h-10 rounded bg-white border border-line flex items-center justify-center text-midnight shrink-0">
                  <FileText className="w-5 h-5 text-midnight" />
                </div>
                <div>
                  <h4 className="font-semibold text-midnight text-[15px] truncate max-w-md">
                    {file.name}
                  </h4>
                  <div className="flex items-center space-x-2 text-[12px] text-charcoal-muted mt-0.5">
                    <span className="font-mono uppercase">{file.name.split('.').pop()}</span>
                    <span>•</span>
                    <span>{formatFileSize(file.size)}</span>
                    <span>•</span>
                    <span className="text-legalgreen font-medium">Ready for analysis</span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setFile(null)}
                className="p-1.5 text-charcoal-muted hover:text-charcoal hover:bg-white rounded transition-colors"
                title="Remove file"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="btn-secondary w-full sm:w-auto"
              >
                Change Document
              </button>

              <button
                type="button"
                onClick={handleStartAnalysis}
                className="btn-primary w-full sm:w-auto py-3 px-8 text-[15px] font-semibold"
              >
                <span>Analyze Document</span>
                <ArrowRight className="w-4 h-4 text-gold-light" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* "What will be extracted?" Information Grid */}
      <div className="bg-white border border-line p-8 shadow-subtle space-y-4">
        <h3 className="text-[13px] font-bold text-midnight uppercase tracking-wider">
          What LexExtract Extracts
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-[13px]">
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-midnight/5 rounded shrink-0 mt-0.5">
              <Sparkles className="w-4 h-4 text-midnight" />
            </div>
            <div>
              <span className="font-semibold text-midnight block">Keywords</span>
              <p className="text-charcoal-muted text-[12px] leading-relaxed mt-0.5">
                Important contractual terms identified across the document.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-2 bg-midnight/5 rounded shrink-0 mt-0.5">
              <Layers className="w-4 h-4 text-midnight" />
            </div>
            <div>
              <span className="font-semibold text-midnight block">Legal Entities</span>
              <p className="text-charcoal-muted text-[12px] leading-relaxed mt-0.5">
                Contractual parties, judicial courts, statutory acts, and specific sections.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-2 bg-midnight/5 rounded shrink-0 mt-0.5">
              <Scale className="w-4 h-4 text-midnight" />
            </div>
            <div>
              <span className="font-semibold text-midnight block">Important Clauses</span>
              <p className="text-charcoal-muted text-[12px] leading-relaxed mt-0.5">
                Termination, indemnification, liability caps, governing law, and dispute resolution.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-2 bg-midnight/5 rounded shrink-0 mt-0.5">
              <Calendar className="w-4 h-4 text-midnight" />
            </div>
            <div>
              <span className="font-semibold text-midnight block">Critical Dates</span>
              <p className="text-charcoal-muted text-[12px] leading-relaxed mt-0.5">
                Effective dates, execution deadlines, expiration dates, and renewal periods.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-2 bg-midnight/5 rounded shrink-0 mt-0.5">
              <DollarSign className="w-4 h-4 text-midnight" />
            </div>
            <div>
              <span className="font-semibold text-midnight block">Financial Values</span>
              <p className="text-charcoal-muted text-[12px] leading-relaxed mt-0.5">
                Remuneration, payment schedules, liquidated damages, penalties, and deposits.
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="p-2 bg-crimson/5 rounded shrink-0 mt-0.5">
              <ShieldAlert className="w-4 h-4 text-crimson" />
            </div>
            <div>
              <span className="font-semibold text-midnight block">Attention Areas</span>
              <p className="text-charcoal-muted text-[12px] leading-relaxed mt-0.5">
                High-exposure liability conditions, restrictive covenants, and unusual notice requirements.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
