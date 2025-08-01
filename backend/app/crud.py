from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, desc, asc
from app.models import User, Task
from app.schemas import UserCreate, UserUpdate, TaskCreate, TaskUpdate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        user= User(**user_data.dict())
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
            )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exlude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        user= await self.get_by_id(user_id)
        if not user:
            return False
        
        await self.session.delete(user)
        await self.session.flush()
        return True
    
class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task_data: TaskCreate, owner_id: int) -> Task:
        task= Task(**task_data.dict(), owner_id=owner_id)
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.owner))
            .where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_user_tasks(
            self,
            owner_id: int, 
            skip: int = 0,
            limit: int = 100,
            completed: Optional[bool] = None,
            priority: Optional[str] = None,
            search: Optional[str] = None
            ) -> List[Task]:
        query = select(Task).where(Task.owner_id == owner_id)

        # Add filters
        if completed is not None:
            query = query.where(Task.completed == completed)

        if priority:
            query = query.where(Task.priority == priority)

        if search:
            query = query.where(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%")
                )
            )

        # Add ordering adn pagination
        query = query.order_by(desc(Task.created_at)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()
    

    async def update(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None
        
        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.session.flush()
        await self.session.refresh(task)
        return task
    
    async def  delete(self, task_id: int) -> bool:
        task= await self.get_by_id(task_id)
        if not task:
            return False
        
        await self.session.delete(task)
        await self.session.flush()
        return True
    
    async def get_task_stats(self, owner_id: int) -> dict:
        """Get task statistics  for a user"""
        total_query = select(Task).where(Task.owner_id == owner_id)
        completed_query = select(Task).where(
            and_(Task.owner_id == owner_id, Task.completed == True)
        )

        total_result = await self.session.execute(total_query)
        completed_result = await self.session.execute(completed_query)

        total_tasks = len(total_result.scalars().all())
        completed_tasks =len(completed_result.scalars().all())

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "peding_tasks": total_tasks - completed_tasks ,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0       
        }
