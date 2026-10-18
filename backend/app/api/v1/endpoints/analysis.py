import re
import time
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.audit_actions import AuditAction
from app.core.deps import get_current_user, check_document_access, get_client_ip
from app.models.analysis import AnalysisRun
from app.models.document import Document
from app.models.keyword import ExtractedKeyword
from app.models.entity import ExtractedEntity
from app.models.user import User
from app.schemas.analysis import (
    AnalysisStartResponse,
    AnalysisSummaryResponse,
    KeywordListResponse,
    KeywordItem,
    EntityListResponse,
    EntityItem,
    AnalysisRunResponse
)
from app.schemas.insights import (
    ClauseListResponse,
    ClauseItem,
    ObligationListResponse,
    ObligationItem,
    FactsResponse,
    FactItem,
    DocumentInsightsResponse
)
from app.services.keyword_extractor import extract_keywords
from app.services.entity_extractor import extract_legal_entities
from app.services.clause_obligation_service import (
    extract_important_clauses,
    extract_obligations,
    extract_structured_facts,
    generate_document_insights,
    generate_analysis_report_json,
    generate_analysis_report_pdf
)
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{document_id}", response_model=AnalysisStartResponse, summary="Execute legal analysis (keywords & entities)")
def analyze_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Orchestrates legal keyword and entity extraction for the given document:
    1. Validates document ownership (403 if unauthorized)
    2. Initializes AnalysisRun record with status 'processing'
    3. Runs hybrid candidate generation, filtering, TF-IDF, RAKE, and Lexicon scoring
    4. Runs hybrid spaCy + rule-based Legal Entity Extraction
    5. Persists extracted keywords in ExtractedKeyword and entities in ExtractedEntity tables
    6. Finalizes AnalysisRun record with 'completed' status, timing, keyword count, and entity count
    7. Records audit events (ANALYSIS_START, ANALYSIS_COMPLETE / ANALYSIS_FAILED)
    """
    ip = get_client_ip(request)
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Enforce document ownership
    check_document_access(doc, current_user, db, ip_address=ip)

    if not doc.extracted_text or not doc.extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Document has no extracted text available for analysis. Ensure document is processed."
        )

    # Initialize AnalysisRun record (status: processing)
    analysis = AnalysisRun(
        document_id=doc.id,
        status="processing",
        total_keywords=0,
        total_entities=0
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.ANALYSIS_START,
        user_id=current_user.id,
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        status="SUCCESS",
        details=f"Initiated keyword and entity extraction for '{doc.filename}'",
        ip_address=ip
    )

    start_time = time.perf_counter()

    try:
        # Phase 4 Keyword extraction
        ranked_keywords = extract_keywords(
            document_text=doc.extracted_text,
            top_k=20
        )

        keyword_records = []
        for idx, kw in enumerate(ranked_keywords, 1):
            keyword_records.append(
                ExtractedKeyword(
                    analysis_run_id=analysis.id,
                    keyword=kw["keyword"],
                    final_score=kw.get("score", kw.get("final_score", 0.0)),
                    category=kw.get("category", "General"),
                    frequency=kw.get("frequency", 1),
                    rank=kw.get("rank", idx),
                    tfidf_score=kw.get("tfidf_score", 0.0),
                    rake_score=kw.get("rake_score", 0.0),
                    lexicon_score=kw.get("lexicon_score", 0.0)
                )
            )

        if keyword_records:
            db.add_all(keyword_records)

        # Phase 5 Legal Entity Extraction
        extracted_entities = extract_legal_entities(doc.extracted_text)
        entity_records = []
        for ent in extracted_entities:
            entity_records.append(
                ExtractedEntity(
                    analysis_run_id=analysis.id,
                    entity_text=ent["text"],
                    normalized_text=ent.get("normalized_text", ent["text"]),
                    entity_type=ent["entity_type"],
                    confidence=ent.get("confidence", 0.75),
                    source=ent.get("source", "rule"),
                    start_position=ent.get("start_position", 0),
                    end_position=ent.get("end_position", 0)
                )
            )

        if entity_records:
            db.add_all(entity_records)

        elapsed = time.perf_counter() - start_time

        # Update AnalysisRun to completed
        analysis.status = "completed"
        analysis.processing_time = round(elapsed, 4)
        analysis.total_keywords = len(keyword_records)
        analysis.total_entities = len(entity_records)
        analysis.completed_at = datetime.now(timezone.utc)
        db.commit()

        AuditService.record_audit_event(
            db=db,
            action=AuditAction.ANALYSIS_COMPLETE,
            user_id=current_user.id,
            resource_type="ANALYSIS",
            resource_id=analysis.id,
            status="SUCCESS",
            details=f"Analysis completed: {len(keyword_records)} keywords, {len(entity_records)} entities in {round(elapsed, 3)}s",
            ip_address=ip
        )

        return AnalysisStartResponse(
            analysis_id=analysis.id,
            document_id=doc.id,
            status="completed",
            total_keywords=len(keyword_records),
            total_entities=len(entity_records),
            processing_time=round(elapsed, 4)
        )

    except Exception as exc:
        db.rollback()
        logger.error(f"Analysis pipeline error for doc {document_id}: {exc}", exc_info=True)
        analysis.status = "failed"
        analysis.completed_at = datetime.now(timezone.utc)
        db.commit()

        AuditService.record_audit_event(
            db=db,
            action=AuditAction.ANALYSIS_FAILED,
            user_id=current_user.id,
            resource_type="ANALYSIS",
            resource_id=analysis.id,
            status="FAILURE",
            details=f"Analysis failed: {exc}",
            ip_address=ip
        )

        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline execution failed: {exc}"
        )


@router.get("/{analysis_id}/keywords", response_model=KeywordListResponse, summary="Retrieve ranked keywords for analysis run")
def get_analysis_keywords(
    analysis_id: int,
    request: Request,
    category: Optional[str] = Query(None, description="Optional category filter (e.g., 'contract', 'criminal')"),
    limit: int = Query(20, ge=1, le=100, description="Max keywords to return (1-100)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves ranked legal keywords for an analysis run.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    query = db.query(ExtractedKeyword).filter(ExtractedKeyword.analysis_id == analysis.id)

    if category:
        query = query.filter(ExtractedKeyword.category.ilike(category.strip()))

    total = query.count()
    keywords = query.order_by(ExtractedKeyword.rank.asc()).limit(limit).all()

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.KEYWORD_VIEW,
        user_id=current_user.id,
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        status="SUCCESS",
        details=f"Viewed {len(keywords)} keywords (category: {category or 'All'})",
        ip_address=ip
    )

    return KeywordListResponse(
        analysis_id=analysis.id,
        total=total,
        keywords=[KeywordItem.model_validate(k) for k in keywords]
    )


@router.get("/{analysis_id}/entities", response_model=EntityListResponse, summary="Retrieve extracted legal entities for analysis run")
def get_analysis_entities(
    analysis_id: int,
    request: Request,
    type: Optional[str] = Query(None, description="Filter by legal entity type (e.g. 'PERSON', 'SECTION', 'ACT')"),
    limit: int = Query(50, ge=1, le=200, description="Max entities to return (1-200)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves extracted legal entities for an analysis run.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    query = db.query(ExtractedEntity).filter(ExtractedEntity.analysis_id == analysis.id)

    if type and type.strip().upper() != "ALL":
        query = query.filter(ExtractedEntity.entity_type == type.strip().upper())

    total = query.count()
    entities = query.order_by(ExtractedEntity.id.asc()).limit(limit).all()

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.ENTITY_VIEW,
        user_id=current_user.id,
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        status="SUCCESS",
        details=f"Viewed {len(entities)} entities (type: {type or 'All'})",
        ip_address=ip
    )

    return EntityListResponse(
        analysis_id=analysis.id,
        total=total,
        entities=[EntityItem.model_validate(e) for e in entities]
    )


@router.get("/{analysis_id}/entities/summary", response_model=Dict[str, int], summary="Retrieve entity counts grouped by entity type")
def get_analysis_entities_summary(
    analysis_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns counts of extracted entities aggregated by entity type.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    rows = db.query(
        ExtractedEntity.entity_type,
        func.count(ExtractedEntity.id)
    ).filter(
        ExtractedEntity.analysis_id == analysis.id
    ).group_by(
        ExtractedEntity.entity_type
    ).all()

    return {row[0]: row[1] for row in rows}


@router.get("/{analysis_id}", response_model=AnalysisSummaryResponse, summary="Get analysis run execution summary")
def get_analysis_summary(
    analysis_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves execution summary for an analysis run.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    return AnalysisSummaryResponse(
        analysis_id=analysis.id,
        document_id=analysis.document_id,
        status=analysis.status,
        processing_time=analysis.processing_time,
        total_keywords=analysis.total_keywords,
        total_entities=analysis.total_entities,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at
    )


@router.get("/document/{document_id}", response_model=List[AnalysisRunResponse], summary="List all analysis runs for a document")
def list_document_analyses(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists historical analysis runs for a document.
    Enforces document ownership check (403 on cross-user access).
    """
    ip = get_client_ip(request)
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    check_document_access(doc, current_user, db, ip_address=ip)

    runs = db.query(AnalysisRun).filter(
        AnalysisRun.document_id == document_id
    ).order_by(AnalysisRun.created_at.desc()).all()

    return runs


@router.get("/{analysis_id}/insights", response_model=DocumentInsightsResponse, summary="Get Document At-a-Glance Executive Insights")
def get_document_insights_endpoint(
    analysis_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes and aggregates high-level document insights at-a-glance:
    - Document name, type, pages, sections
    - Extracted keywords & entities count
    - Detected parties, key dates, monetary figures
    - Important clause detections, obligations count
    - Specific attention areas & risks
    - Explicit 'Not detected' fallbacks for missing attributes
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    text = analysis.document.extracted_text or ""
    pages_json = analysis.document.pages_json

    clauses = extract_important_clauses(text, pages_json)
    obligations = extract_obligations(text, pages_json, analysis.entities)
    facts = extract_structured_facts(text, pages_json, analysis.entities)

    insights = generate_document_insights(
        document=analysis.document,
        analysis_run=analysis,
        keywords=analysis.keywords,
        entities=analysis.entities,
        clauses=clauses,
        obligations=obligations,
        facts=facts
    )

    return insights


@router.get("/{analysis_id}/clauses", response_model=ClauseListResponse, summary="Retrieve Important Clause Detections across 13 Legal Categories")
def get_document_clauses_endpoint(
    analysis_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scans document for 13 controlled legal clause categories:
    Termination, Confidentiality, Payment, Liability, Indemnification, Arbitration,
    Governing Law, Renewal, Notice, Intellectual Property, Non-Disclosure, Non-Compete, Force Majeure.
    Returns status (Found/Not Found), source section, page, relevant text snippet, and confidence.
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    text = analysis.document.extracted_text or ""
    pages_json = analysis.document.pages_json

    clauses_data = extract_important_clauses(text, pages_json)
    found_count = sum(1 for c in clauses_data if c["status"] == "Found")

    return ClauseListResponse(
        analysis_id=analysis.id,
        document_id=analysis.document_id,
        total_detected=found_count,
        total_categories=13,
        clauses=[ClauseItem(**c) for c in clauses_data]
    )


@router.get("/{analysis_id}/obligations", response_model=ObligationListResponse, summary="Extract Contractual Obligations & Responsibilities")
def get_document_obligations_endpoint(
    analysis_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extracts explicit contractual duties and prohibitions:
    Identifies modal verbs (shall, must, required to, agrees to, may not, shall not)
    Extracts responsible party, obligation action, deadline, type, and source passage.
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    text = analysis.document.extracted_text or ""
    pages_json = analysis.document.pages_json

    obligations_data = extract_obligations(text, pages_json, analysis.entities)

    return ObligationListResponse(
        analysis_id=analysis.id,
        document_id=analysis.document_id,
        total=len(obligations_data),
        obligations=[ObligationItem(**o) for o in obligations_data]
    )


@router.get("/{analysis_id}/facts", response_model=FactsResponse, summary="Extract Structured Dates, Monetary Amounts, and Deadlines")
def get_document_facts_endpoint(
    analysis_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extracts and categorizes dates (effective, expiry, execution),
    monetary sums (salary, fees, damages, deposits), and durations/deadlines (notice period, term).
    Includes normalized values and original verbatim text.
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    text = analysis.document.extracted_text or ""
    pages_json = analysis.document.pages_json

    facts_data = extract_structured_facts(text, pages_json, analysis.entities)

    return FactsResponse(
        analysis_id=analysis.id,
        document_id=analysis.document_id,
        dates=[FactItem(**d) for d in facts_data["dates"]],
        money=[FactItem(**m) for m in facts_data["money"]],
        deadlines=[FactItem(**dl) for dl in facts_data["deadlines"]]
    )


@router.get("/{analysis_id}/export", summary="Export Comprehensive Legal Analysis Report (PDF or JSON)")
def export_analysis_report_endpoint(
    analysis_id: int,
    request: Request,
    format: str = Query("pdf", description="Export format: 'pdf' or 'json'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exports a professional, publication-ready legal document analysis report:
    Contains all 11 required sections:
    1. Document Information
    2. Document Overview & Metadata
    3. Top Keywords
    4. Extracted Entities
    5. Important Clauses (13 Categories)
    6. Obligations & Responsibilities
    7. Dates / Deadlines
    8. Monetary Information
    9. Attention Areas & Governance Risks
    10. Search/Analysis Execution Metadata
    11. System Disclaimer (Not Legal Advice)
    """
    ip = get_client_ip(request)
    analysis = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    check_document_access(analysis.document, current_user, db, ip_address=ip)

    text = analysis.document.extracted_text or ""
    pages_json = analysis.document.pages_json

    clauses = extract_important_clauses(text, pages_json)
    obligations = extract_obligations(text, pages_json, analysis.entities)
    facts = extract_structured_facts(text, pages_json, analysis.entities)

    insights = generate_document_insights(
        document=analysis.document,
        analysis_run=analysis,
        keywords=analysis.keywords,
        entities=analysis.entities,
        clauses=clauses,
        obligations=obligations,
        facts=facts
    )

    report_dict = generate_analysis_report_json(
        document=analysis.document,
        analysis_run=analysis,
        keywords=analysis.keywords,
        entities=analysis.entities,
        clauses=clauses,
        obligations=obligations,
        facts=facts,
        insights=insights
    )

    AuditService.record_audit_event(
        db=db,
        action=AuditAction.REPORT_EXPORT,
        user_id=current_user.id,
        resource_type="ANALYSIS",
        resource_id=analysis.id,
        status="SUCCESS",
        details=f"Exported analysis report in '{format.upper()}' for '{analysis.document.filename}'",
        ip_address=ip
    )

    if format.lower() == "json":
        return report_dict

    # Default to PDF
    pdf_bytes = generate_analysis_report_pdf(report_dict)
    clean_filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', analysis.document.filename)
    filename = f"LexExtract_Report_{clean_filename}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

