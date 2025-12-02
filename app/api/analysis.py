from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models import User, FinancialReport
from ..database import get_db
from ..services.math_engine import FinancialAnalyzer, AnalysisResultSchema
from .auth import get_current_user


router = APIRouter(
    prefix="/analysis",
    tags=['analysis']
)

@router.get("/{report_id}", response_model=AnalysisResultSchema)
async def analyze_report(
    report_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    stmt = select(FinancialReport)\
        .options(
            selectinload(FinancialReport.assets),
            selectinload(FinancialReport.liabilities),
            selectinload(FinancialReport.profit_loss)
        )\
        .where(FinancialReport.id == report_id)
        
    result = await db.execute(stmt)
    report: FinancialReport | None = result.scalar_one_or_none()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != current_user.id and current_user.role != "admin": # type: ignore
        raise HTTPException(status_code=403, detail="Not authorized")


    analyzer = FinancialAnalyzer(report)
    return analyzer.get_full_analysis()
