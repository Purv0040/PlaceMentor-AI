from typing import Optional, Dict, Any
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        # TODO: Implement complete user profile fetching in future phase.
        return await self.user_repo.get_by_id(user_id)
