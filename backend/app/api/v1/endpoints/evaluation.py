"""
Evaluation Endpoints for LexExtract ASTMA Quantitative Information Retrieval Benchmarking.
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.roles import Role
from app.core.deps import get_current_user, require_role, get_client_ip
from app.core.audit_actions import AuditAction
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.evaluation_service import (
    get_latest_evaluation_report,
    execute_full_benchmark,
    load_benchmark_dataset
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", summary="Retrieve ASTMA benchmark evaluation summary & metrics")
def get_evaluation_summary(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns high-level evaluation metrics:
    - Overall Micro & Macro Precision, Recall, and F1 for Keywords and Entities.
    - Top-K cutoff performance (Precision@K, Recall@K, F1@K).
    - Latency statistics (min, max, average).
    - Keyword extraction algorithm ablation comparison.
    """
    try:
        report = get_latest_evaluation_report()
        return {
            "benchmark_summary": report.get("benchmark_summary", {}),
            "performance": report.get("performance", {}),
            "keyword_evaluation": report.get("keyword_evaluation", {}),
            "entity_evaluation": report.get("entity_evaluation", {})
        }
    except Exception as exc:
        logger.error(f"Failed to load evaluation summary: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve evaluation summary: {str(exc)}"
        )


@router.get("/documents", summary="Retrieve per-document benchmark results")
def get_evaluation_documents(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Returns document-level performance metrics for all 12 benchmark legal documents.
    """
    try:
        report = get_latest_evaluation_report()
        return report.get("document_results", [])
    except Exception as exc:
        logger.error(f"Failed to load per-document evaluation results: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document evaluations: {str(exc)}"
        )


@router.get("/documents/{document_id}", summary="Retrieve detailed evaluation for a specific benchmark document")
def get_single_document_evaluation(
    document_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieves granular evaluation details, True Positives, False Positives, and False Negatives
    for a specific benchmark document.
    """
    report = get_latest_evaluation_report()
    doc_results = report.get("document_results", [])
    for doc in doc_results:
        if doc.get("document_id") == document_id:
            return doc

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Benchmark document '{document_id}' not found in evaluation dataset."
    )


@router.get("/errors", summary="Retrieve comprehensive error analysis breakdown")
def get_evaluation_errors(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns categorized error distribution:
    - False Positive Keywords
    - False Negative Keywords
    - False Positive Entities
    - False Negative Entities
    - Entity Type Mismatches
    """
    try:
        report = get_latest_evaluation_report()
        return report.get("error_analysis", {})
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve error analysis: {str(exc)}"
        )


@router.post("/run", summary="Trigger live ASTMA benchmark evaluation run")
def run_evaluation_benchmark(
    request: Request,
    current_user: User = Depends(require_role([Role.ANALYST, Role.ADMIN])),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Executes live evaluation against the 12-document curated benchmark dataset.
    Requires role: ANALYST or ADMIN.
    Records audit event in append-only ledger.
    """
    ip = get_client_ip(request)
    try:
        report = execute_full_benchmark()

        AuditService.record_audit_event(
            db=db,
            action=AuditAction.ANALYSIS_COMPLETE,
            user_id=current_user.id,
            resource_type="EVALUATION",
            resource_id=0,
            status="SUCCESS",
            details=f"ASTMA benchmark completed ({report['benchmark_summary']['total_documents']} documents in {report['benchmark_summary']['total_execution_time_seconds']}s)",
            ip_address=ip
        )

        return report
    except Exception as exc:
        logger.error(f"Benchmark execution failed: {exc}", exc_info=True)
        AuditService.record_audit_event(
            db=db,
            action=AuditAction.ANALYSIS_FAILED,
            user_id=current_user.id,
            resource_type="EVALUATION",
            resource_id=0,
            status="FAILURE",
            details=f"ASTMA benchmark failure: {str(exc)}",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark execution failed: {str(exc)}"
        )
