# Advanced Task Management and Reminders System
# Provides comprehensive task scheduling, reminders, and productivity features

import json
import datetime
import threading
import time
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum
import uuid

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    status: TaskStatus
    created_at: str
    due_date: Optional[str] = None
    reminder_time: Optional[str] = None
    tags: List[str] = None
    estimated_duration: Optional[int] = None  # in minutes
    actual_duration: Optional[int] = None
    completion_date: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class Reminder:
    id: str
    title: str
    message: str
    reminder_time: str
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    is_active: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()

class TaskManager:
    def __init__(self):
        self.data_dir = "Data/Tasks"
        self.tasks_file = f"{self.data_dir}/tasks.json"
        self.reminders_file = f"{self.data_dir}/reminders.json"
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data files
        self.tasks = self._load_tasks()
        self.reminders = self._load_reminders()
        
        # Start reminder checker thread
        self.reminder_thread = threading.Thread(target=self._check_reminders, daemon=True)
        self.reminder_thread.start()
        
        # Productivity tracking
        self.productivity_file = f"{self.data_dir}/productivity.json"
        self.productivity_stats = self._load_productivity_stats()
    
    def create_task(self, title: str, description: str = "", priority: str = "medium", 
                   due_date: str = None, tags: List[str] = None, estimated_duration: int = None) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=Priority(priority.lower()),
            status=TaskStatus.PENDING,
            created_at=datetime.datetime.now().isoformat(),
            due_date=due_date,
            tags=tags or [],
            estimated_duration=estimated_duration
        )
        
        self.tasks[task_id] = task
        self._save_tasks()
        
        print(f"✅ Task created: {title}")
        return task_id
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update an existing task"""
        if task_id not in self.tasks:
            print(f"❌ Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                if key == "priority":
                    value = Priority(value.lower())
                elif key == "status":
                    value = TaskStatus(value.lower())
                    if value == TaskStatus.COMPLETED:
                        task.completion_date = datetime.datetime.now().isoformat()
                        self._update_productivity_stats(task)
                
                setattr(task, key, value)
        
        self._save_tasks()
        print(f"✅ Task updated: {task.title}")
        return True
    
    def complete_task(self, task_id: str, actual_duration: int = None) -> bool:
        """Mark a task as completed"""
        return self.update_task(task_id, status="completed", actual_duration=actual_duration)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        if task_id in self.tasks:
            task_title = self.tasks[task_id].title
            del self.tasks[task_id]
            self._save_tasks()
            print(f"🗑️ Task deleted: {task_title}")
            return True
        return False
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get tasks filtered by status"""
        return [task for task in self.tasks.values() if task.status.value == status.lower()]
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get tasks filtered by priority"""
        return [task for task in self.tasks.values() if task.priority.value == priority.lower()]
    
    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks filtered by tag"""
        return [task for task in self.tasks.values() if tag in task.tags]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.datetime.now()
        overdue = []
        
        for task in self.tasks.values():
            if task.due_date and task.status != TaskStatus.COMPLETED:
                due_date = datetime.datetime.fromisoformat(task.due_date)
                if due_date < now:
                    overdue.append(task)
        
        return overdue
    
    def get_today_tasks(self) -> List[Task]:
        """Get tasks due today"""
        today = datetime.date.today().isoformat()
        return [task for task in self.tasks.values() 
                if task.due_date and task.due_date.startswith(today)]
    
    def create_reminder(self, title: str, message: str, reminder_time: str, 
                       is_recurring: bool = False, recurrence_pattern: str = None) -> str:
        """Create a new reminder"""
        reminder_id = str(uuid.uuid4())
        
        reminder = Reminder(
            id=reminder_id,
            title=title,
            message=message,
            reminder_time=reminder_time,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern
        )
        
        self.reminders[reminder_id] = reminder
        self._save_reminders()
        
        print(f"⏰ Reminder created: {title}")
        return reminder_id
    
    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        if reminder_id in self.reminders:
            reminder_title = self.reminders[reminder_id].title
            del self.reminders[reminder_id]
            self._save_reminders()
            print(f"🗑️ Reminder deleted: {reminder_title}")
            return True
        return False
    
    def get_productivity_stats(self) -> Dict:
        """Get productivity statistics"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.get_tasks_by_status("completed")),
            "pending_tasks": len(self.get_tasks_by_status("pending")),
            "overdue_tasks": len(self.get_overdue_tasks()),
            "completion_rate": self._calculate_completion_rate(),
            "average_completion_time": self._calculate_average_completion_time(),
            "productivity_score": self._calculate_productivity_score()
        }
    
    def get_weekly_summary(self) -> Dict:
        """Get weekly task summary"""
        now = datetime.datetime.now()
        week_start = now - datetime.timedelta(days=now.weekday())
        
        weekly_tasks = []
        for task in self.tasks.values():
            created_date = datetime.datetime.fromisoformat(task.created_at)
            if created_date >= week_start:
                weekly_tasks.append(task)
        
        return {
            "total_created": len(weekly_tasks),
            "completed": len([t for t in weekly_tasks if t.status == TaskStatus.COMPLETED]),
            "pending": len([t for t in weekly_tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in weekly_tasks if t.status == TaskStatus.IN_PROGRESS])
        }
    
    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description"""
        query = query.lower()
        results = []
        
        for task in self.tasks.values():
            if (query in task.title.lower() or 
                query in task.description.lower() or
                any(query in tag.lower() for tag in task.tags)):
                results.append(task)
        
        return results
    
    def _check_reminders(self):
        """Background thread to check for due reminders"""
        while True:
            try:
                now = datetime.datetime.now()
                
                for reminder in list(self.reminders.values()):
                    if not reminder.is_active:
                        continue
                    
                    reminder_time = datetime.datetime.fromisoformat(reminder.reminder_time)
                    
                    # Check if reminder time has passed
                    if reminder_time <= now:
                        self._trigger_reminder(reminder)
                        
                        if reminder.is_recurring:
                            self._schedule_next_occurrence(reminder)
                        else:
                            reminder.is_active = False
                            self._save_reminders()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in reminder checker: {e}")
                time.sleep(60)
    
    def _trigger_reminder(self, reminder: Reminder):
        """Trigger a reminder notification"""
        print(f"\n🔔 REMINDER: {reminder.title}")
        print(f"📝 {reminder.message}")
        print(f"🕐 {reminder.reminder_time}")
        
        # Here you could add more notification methods:
        # - GUI popup
        # - System notification
        # - Sound alert
        # - Email notification
    
    def _schedule_next_occurrence(self, reminder: Reminder):
        """Schedule next occurrence for recurring reminders"""
        current_time = datetime.datetime.fromisoformat(reminder.reminder_time)
        
        if reminder.recurrence_pattern == "daily":
            next_time = current_time + datetime.timedelta(days=1)
        elif reminder.recurrence_pattern == "weekly":
            next_time = current_time + datetime.timedelta(weeks=1)
        elif reminder.recurrence_pattern == "monthly":
            next_time = current_time + datetime.timedelta(days=30)
        else:
            return
        
        reminder.reminder_time = next_time.isoformat()
        self._save_reminders()
    
    def _calculate_completion_rate(self) -> float:
        """Calculate task completion rate"""
        if not self.tasks:
            return 0.0
        
        completed = len(self.get_tasks_by_status("completed"))
        total = len(self.tasks)
        return (completed / total) * 100
    
    def _calculate_average_completion_time(self) -> float:
        """Calculate average task completion time"""
        completed_tasks = self.get_tasks_by_status("completed")
        total_time = 0
        count = 0
        
        for task in completed_tasks:
            if task.actual_duration:
                total_time += task.actual_duration
                count += 1
        
        return total_time / count if count > 0 else 0
    
    def _calculate_productivity_score(self) -> float:
        """Calculate overall productivity score"""
        completion_rate = self._calculate_completion_rate()
        overdue_count = len(self.get_overdue_tasks())
        total_tasks = len(self.tasks)
        
        # Simple scoring algorithm
        score = completion_rate
        if total_tasks > 0:
            overdue_penalty = (overdue_count / total_tasks) * 20
            score = max(0, score - overdue_penalty)
        
        return round(score, 2)
    
    def _update_productivity_stats(self, task: Task):
        """Update productivity statistics when task is completed"""
        if not hasattr(self, 'productivity_stats'):
            self.productivity_stats = {}
        
        today = datetime.date.today().isoformat()
        if today not in self.productivity_stats:
            self.productivity_stats[today] = {
                "tasks_completed": 0,
                "total_time": 0,
                "tasks_created": 0
            }
        
        self.productivity_stats[today]["tasks_completed"] += 1
        if task.actual_duration:
            self.productivity_stats[today]["total_time"] += task.actual_duration
        
        self._save_productivity_stats()
    
    def _load_tasks(self) -> Dict[str, Task]:
        """Load tasks from file"""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = {}
                for task_id, task_data in data.items():
                    task_data['priority'] = Priority(task_data['priority'])
                    task_data['status'] = TaskStatus(task_data['status'])
                    tasks[task_id] = Task(**task_data)
                return tasks
        return {}
    
    def _save_tasks(self):
        """Save tasks to file"""
        data = {}
        for task_id, task in self.tasks.items():
            task_dict = asdict(task)
            task_dict['priority'] = task.priority.value
            task_dict['status'] = task.status.value
            data[task_id] = task_dict
        
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def _load_reminders(self) -> Dict[str, Reminder]:
        """Load reminders from file"""
        if os.path.exists(self.reminders_file):
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reminders = {}
                for reminder_id, reminder_data in data.items():
                    reminders[reminder_id] = Reminder(**reminder_data)
                return reminders
        return {}
    
    def _save_reminders(self):
        """Save reminders to file"""
        data = {}
        for reminder_id, reminder in self.reminders.items():
            data[reminder_id] = asdict(reminder)
        
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def _load_productivity_stats(self) -> Dict:
        """Load productivity statistics from file"""
        if os.path.exists(self.productivity_file):
            with open(self.productivity_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_productivity_stats(self):
        """Save productivity statistics to file"""
        with open(self.productivity_file, 'w', encoding='utf-8') as f:
            json.dump(self.productivity_stats, f, indent=4)

# Global task manager instance
task_manager = TaskManager()

# Voice command functions for task management
def create_task_voice(command: str):
    """Create task from voice command"""
    # Parse command like "create task buy groceries with high priority due tomorrow"
    parts = command.lower().split()
    
    if "create task" in command:
        # Extract task title
        start_idx = command.lower().find("create task") + len("create task")
        title_part = command[start_idx:].strip()
        
        # Extract priority if mentioned
        priority = "medium"
        if "high priority" in title_part:
            priority = "high"
            title_part = title_part.replace("high priority", "").strip()
        elif "low priority" in title_part:
            priority = "low"
            title_part = title_part.replace("low priority", "").strip()
        elif "urgent" in title_part:
            priority = "urgent"
            title_part = title_part.replace("urgent", "").strip()
        
        # Extract due date if mentioned
        due_date = None
        if "due tomorrow" in title_part:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            due_date = tomorrow.isoformat()
            title_part = title_part.replace("due tomorrow", "").strip()
        elif "due today" in title_part:
            due_date = datetime.date.today().isoformat()
            title_part = title_part.replace("due today", "").strip()
        
        # Clean up title
        title = title_part.replace("with", "").strip()
        
        if title:
            task_id = task_manager.create_task(title, priority=priority, due_date=due_date)
            return f"Task '{title}' created successfully with ID {task_id[:8]}"
    
    return "Please specify a task title to create"

def list_tasks_voice(command: str):
    """List tasks from voice command"""
    if "pending tasks" in command or "open tasks" in command:
        tasks = task_manager.get_tasks_by_status("pending")
    elif "completed tasks" in command:
        tasks = task_manager.get_tasks_by_status("completed")
    elif "overdue tasks" in command:
        tasks = task_manager.get_overdue_tasks()
    elif "today tasks" in command or "today's tasks" in command:
        tasks = task_manager.get_today_tasks()
    else:
        tasks = list(task_manager.tasks.values())[:10]  # Limit to 10
    
    if not tasks:
        return "No tasks found"
    
    result = f"Found {len(tasks)} tasks:\n"
    for i, task in enumerate(tasks[:5], 1):  # Limit to 5 for voice
        result += f"{i}. {task.title} ({task.priority.value} priority)\n"
    
    return result

def complete_task_voice(command: str):
    """Complete task from voice command"""
    # Simple approach: find task by title keywords
    query = command.lower().replace("complete task", "").replace("mark", "").replace("done", "").strip()
    
    if query:
        tasks = task_manager.search_tasks(query)
        if tasks:
            # Complete the first matching task
            task = tasks[0]
            if task_manager.complete_task(task.id):
                return f"Task '{task.title}' marked as completed"
        else:
            return f"No task found matching '{query}'"
    
    return "Please specify which task to complete"