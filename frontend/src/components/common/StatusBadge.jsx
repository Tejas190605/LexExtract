import React from 'react';
import { CheckCircle2, Clock, AlertCircle, FileText, ShieldAlert } from 'lucide-react';

export default function StatusBadge({ status, size = 'sm' }) {
  const norm = (status || '').toLowerCase().trim();

  let bg = 'bg-slate-100 text-slate-800 border-slate-300';
  let label = status || 'Unknown';
  let Icon = FileText;

  switch (norm) {
    case 'completed':
    case 'success':
    case 'analyzed':
      bg = 'bg-emerald-50 text-emerald-800 border-emerald-300';
      label = norm === 'analyzed' ? 'Analyzed' : 'Completed';
      Icon = CheckCircle2;
      break;
    case 'processing':
    case 'pending':
    case 'analyzing':
      bg = 'bg-amber-50 text-amber-800 border-amber-300';
      label = 'Processing';
      Icon = Clock;
      break;
    case 'uploaded':
      bg = 'bg-blue-50 text-blue-800 border-blue-300';
      label = 'Uploaded';
      Icon = FileText;
      break;
    case 'failed':
    case 'failure':
    case 'error':
      bg = 'bg-rose-50 text-rose-800 border-rose-300';
      label = 'Failed';
      Icon = AlertCircle;
      break;
    case 'unauthorized':
      bg = 'bg-purple-50 text-purple-800 border-purple-300';
      label = 'Unauthorized';
      Icon = ShieldAlert;
      break;
    default:
      break;
  }

  const sizeClasses = size === 'xs'
    ? 'text-[10px] px-1.5 py-0.5 space-x-1'
    : 'text-xs px-2.5 py-1 space-x-1.5';

  return (
    <span className={`inline-flex items-center font-semibold uppercase tracking-wider border rounded-none ${bg} ${sizeClasses}`}>
      <Icon className={size === 'xs' ? 'w-2.5 h-2.5' : 'w-3 h-3'} />
      <span>{label}</span>
    </span>
  );
}
