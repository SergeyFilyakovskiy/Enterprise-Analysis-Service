from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import User, FinancialReport, ReportAssets, ReportLiabilities, ReportProfitLoss
from ..schemas import FinancialReportCreate, FinancialReportResponse, ReportSummary, CompareResponse
from .auth import get_current_user 
from ..services.math_engine import ReportComparator
from ..services.excel_parser import parse_balance_sheet


router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)


@router.get("/", 
            response_model=list[ReportSummary],
            status_code=status.HTTP_200_OK
            )
async def get_my_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    stmt = select(FinancialReport)\
        .where(FinancialReport.user_id == current_user.id)\
        .order_by(desc(FinancialReport.created_at))
        
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    return reports

@router.post("/", response_model=FinancialReportResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_report(
    report: FinancialReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """

    Uploading a new financial report.
    Data must conform to the FinancialReportCreate schema.
    
    """
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


    new_report = FinancialReport(
        user_id=current_user.id,
        organization_name=report.organization_name,
        period=report.period
    )
    
    db.add(new_report)
    await db.flush() 

    assets_data = report.assets.model_dump()
    new_assets = ReportAssets(
        report_id=new_report.id,
        **assets_data 
    )
    
    liabilities_data = report.liabilities.model_dump()
    new_liabilities = ReportLiabilities(
        report_id=new_report.id,
        **liabilities_data
    )
    
    profit_loss_data = report.profit_loss.model_dump()
    new_profit_loss = ReportProfitLoss(
        report_id=new_report.id,
        **profit_loss_data
    )

    db.add_all([new_assets, new_liabilities, new_profit_loss])
    await db.commit()
    await db.refresh(new_report, attribute_names=["assets", "liabilities", "profit_loss"])

    return new_report


@router.post("/compare", response_model=CompareResponse)
async def compare_reports(
    base_report_id: int, 
    curr_report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Загрузка данных (это ответственность роутера/DB слоя)
    stmt = select(FinancialReport).options(
        selectinload(FinancialReport.assets),
        selectinload(FinancialReport.liabilities),
        selectinload(FinancialReport.profit_loss)
    ).where(FinancialReport.id.in_([base_report_id, curr_report_id]))
    
    result = await db.execute(stmt)
    reports = result.scalars().all()
    
    if len(reports) != 2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reports not found")

    base_rep = next(r for r in reports if r.id == base_report_id)
    curr_rep = next(r for r in reports if r.id == curr_report_id)

    if base_rep.user_id != current_user.id or curr_rep.user_id != current_user.id:
        if current_user.role != "admin":
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # 2. Вызов бизнес-логики (чистая функция)
    return ReportComparator.compare(base_rep, curr_rep)

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление отчета по ID.
    Пользователь может удалить только свой отчет. Админ - любой.
    """
    
    stmt = select(FinancialReport).where(FinancialReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id or current_user.role != "admin":
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this report")

    await db.delete(report)
    await db.commit()

@router.post("/parse_excel")
async def parse_excel_file(file: UploadFile = File(...)):
    content = await file.read()
    try:
        data = parse_balance_sheet(content)
        return data 
    except Exception as e:
        raise HTTPException(400, f"Error parsing file: {e}")