from fastapi import APIRouter, Depends, HTTPException, status
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User, FinancialReport, ReportAssets, ReportLiabilities, ReportProfitLoss
from ..schemas import FinancialReportCreate, FinancialReportResponse
from .auth import get_current_user 

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

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
