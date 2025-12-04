"""
Finance endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.crud.finance import finance_crud
from app.schemas.finance import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    FinanceSummary,
    FinanceStats,
)
from app.schemas.common import PaginationParams, PaginatedResponse
from app.dependencies import get_current_admin
from datetime import date

router = APIRouter()


@router.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Create a new expense (Admin only)
    """
    expense_dict = expense_data.model_dump()
    expense_dict["created_by"] = admin["id"]
    expense = await finance_crud.create_expense(db, expense_dict)
    return expense


@router.get("/expenses", response_model=PaginatedResponse[ExpenseResponse])
async def get_expenses(
    pagination: PaginationParams = Depends(),
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get list of expenses with pagination (Admin only)
    """
    filters = {}
    if category:
        filters["category"] = category
    
    expenses, total = await finance_crud.get_expenses(
        db,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters,
        start_date=start_date,
        end_date=end_date
    )
    
    expense_list = []
    for expense in expenses:
        expense_dict = {
            "id": expense.id,
            "description": expense.description,
            "amount": float(expense.amount),
            "category": expense.category,
            "notes": expense.notes,
            "created_at": expense.created_at,
            "created_by": expense.created_by,
        }
        expense_list.append(ExpenseResponse(**expense_dict))
    return PaginatedResponse.create(expense_list, total, pagination.page, pagination.page_size)


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get expense by ID (Admin only)
    """
    expense = await finance_crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Update expense (Admin only)
    """
    expense = await finance_crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    update_data = expense_data.model_dump(exclude_unset=True)
    updated_expense = await finance_crud.update_expense(db, expense, update_data)
    return updated_expense


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Delete expense (Admin only)
    """
    deleted = await finance_crud.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )


@router.get("/summary", response_model=FinanceSummary)
async def get_finance_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get finance summary (Admin only)
    """
    summary = await finance_crud.get_summary(db, start_date, end_date)
    return summary


@router.get("/stats", response_model=FinanceStats)
async def get_finance_stats(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Get finance statistics for charts (Admin only)
    """
    stats = await finance_crud.get_stats(db, period)
    return stats

