from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models.report import Report, ReportFormat, ReportStatus

router = APIRouter()


class ReportCreate(BaseModel):
    org_id: str
    report_type: str = "esg"
    format: ReportFormat = ReportFormat.PDF
    from_date: str
    to_date: str


class ReportResponse(BaseModel):
    id: str
    org_id: str
    report_type: str
    format: ReportFormat
    from_date: str
    to_date: str
    status: ReportStatus
    download_url: str | None
    created_at: str
    completed_at: str | None

    class Config:
        from_attributes = True


@router.post("/reports", response_model=ReportResponse)
async def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """
    Create an async report generation job.
    Worker will pick this up and generate PDF/CSV.
    """
    db_report = Report(
        org_id=report.org_id,
        report_type=report.report_type,
        format=report.format,
        from_date=report.from_date,
        to_date=report.to_date,
        status=ReportStatus.PENDING,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get report status and download URL"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return {"error": "Report not found"}, 404
    return report


@router.get("/orgs/{org_id}/reports", response_model=list[ReportResponse])
async def list_reports(org_id: str, db: Session = Depends(get_db)):
    """List reports for an organization"""
    reports = db.query(Report).filter(Report.org_id == org_id).order_by(Report.created_at.desc()).limit(50).all()
    return reports