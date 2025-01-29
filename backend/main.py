from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import logging
import sqlite3

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('tasks_habits_reminders.db')
    conn.row_factory = sqlite3.Row
    return conn

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    status: str = "pending"

class Habit(BaseModel):
    id: int
    name: str
    frequency: str

class Reminder(BaseModel):
    id: int
    task_id: int
    reminder_time: str

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (id, title, description, deadline, status) VALUES (?, ?, ?, ?, ?)',
                 (task.id, task.title, task.description, task.deadline, task.status))
    conn.commit()
    conn.close()
    return task

@app.get("/tasks/", response_model=List[Task])
def read_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return [dict(task) for task in tasks]  # Convert Row objects to dictionaries

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET title = ?, description = ?, deadline = ?, status = ? WHERE id = ?',
                 (updated_task.title, updated_task.description, updated_task.deadline, updated_task.status, task_id))
    conn.commit()
    conn.close()
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted successfully"}

@app.post("/habits/", response_model=Habit)
def create_habit(habit: Habit):
    conn = get_db_connection()
    conn.execute('INSERT INTO habits (id, name, frequency) VALUES (?, ?, ?)',
                 (habit.id, habit.name, habit.frequency))
    conn.commit()
    conn.close()
    return habit

@app.get("/habits/", response_model=List[Habit])
def read_habits():
    conn = get_db_connection()
    habits = conn.execute('SELECT * FROM habits').fetchall()
    conn.close()
    return [dict(habit) for habit in habits]  # Convert Row objects to dictionaries

@app.put("/habits/{habit_id}", response_model=Habit)
def update_habit(habit_id: int, updated_habit: Habit):
    conn = get_db_connection()
    conn.execute('UPDATE habits SET name = ?, frequency = ? WHERE id = ?',
                 (updated_habit.name, updated_habit.frequency, habit_id))
    conn.commit()
    conn.close()
    return updated_habit

@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int):
    conn = get_db_connection()
    conn.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    conn.commit()
    conn.close()
    return {"message": "Habit deleted successfully"}

@app.post("/reminders/", response_model=Reminder)
def create_reminder(reminder: Reminder):
    conn = get_db_connection()
    conn.execute('INSERT INTO reminders (id, task_id, reminder_time) VALUES (?, ?, ?)',
                 (reminder.id, reminder.task_id, reminder.reminder_time))
    conn.commit()
    conn.close()
    return reminder

@app.get("/reminders/", response_model=List[Reminder])
def read_reminders():
    conn = get_db_connection()
    reminders = conn.execute('SELECT * FROM reminders').fetchall()
    conn.close()
    return [dict(reminder) for reminder in reminders]  # Convert Row objects to dictionaries

@app.post("/chatbot/")
def chatbot_response(query: str):
    api_key = "AIzaSyBlJu4Nhje47zjEbLd1W27ShaQKr4Axgmk"  # Updated Gemini API key
    logging.info(f"Chatbot query: {query}")
    
    request_body = {"query": query}
    logging.info(f"Sending request to chatbot API with body: {request_body}")
    
    response = requests.post(
        "https://api.gemini.com/v1/chat",
        headers={"Authorization": f"Bearer {api_key}"},
        json=request_body
    )
    
    logging.info(f"Chatbot API response status: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error from chatbot API: {response.text}")
        raise HTTPException(status_code=response.status_code, detail="Error from chatbot API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Task & Productivity Management System"}
