from app.schemas.daily_task import (
    DailyTaskCreateSchema as TaskCreateSchema,
    DailyTaskUpdateSchema as TaskUpdateSchema,
    DailyTaskStatusUpdateSchema as TaskStatusUpdateSchema,
    DailyTaskCompleteSchema as TaskCompleteSchema,
    DailyTaskSkipSchema as TaskSkipSchema,
    DailyTaskResponseSchema as TaskResponseSchema,
    TodayTasksResponseSchema as TodayTasksResponseSchema,
)

# Aliases for compatibility
TaskCreate = TaskCreateSchema
TaskUpdate = TaskUpdateSchema
TaskResponse = TaskResponseSchema
