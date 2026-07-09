from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.subscription_service import user_has_access


def require_feature(section: str):
    async def _check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_admin:
            return current_user
        has = await user_has_access(db, current_user.id, section)
        if not has:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/pricing"},
                detail="Subscription required",
            )
        return current_user
    return _check
