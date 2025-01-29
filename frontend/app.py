import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd
import hashlib
from PIL import Image
import io
import google.generativeai as genai

# Initialize Gemini API
genai.configure(api_key='AIzaSyCfjBj_e9eqpJRSI0l-et5xtKNMYlIfYPo')
model = genai.GenerativeModel('gemini-pro')

# Page configuration
st.set_page_config(
    page_title="Student Productivity Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database functions
def get_db_connection():
    conn = sqlite3.connect('student_productivity.db')
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication functions
def create_user(username, password, email):
    conn = get_db_connection()
    try:
        hashed_pwd = hash_password(password)
        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_pwd, email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    hashed_pwd = hash_password(password)
    cursor = conn.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (username, hashed_pwd)
    )
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Authentication UI
def show_auth_ui():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                user_id = verify_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif create_user(new_username, new_password, new_email):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username or email already exists")

# Main application
def main():
    # Sidebar navigation
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("", 
        ["Dashboard", "Tasks", "Habits", "Progress", "Journal", "About Us", "How to Use", "AI Assistant"],
        format_func=lambda x: f"{'📊' if x=='Dashboard' else '📝' if x=='Tasks' else '🎯' if x=='Habits' else '📈' if x=='Progress' else '📔' if x=='Journal' else '👥' if x=='About Us' else '❓' if x=='How to Use' else '🤖'} {x}")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

    # Page content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Tasks":
        show_tasks()
    elif page == "Habits":
        show_habits()
    elif page == "Progress":
        show_progress()
    elif page == "Journal":
        show_journal()
    elif page == "About Us":
        show_about_us()
    elif page == "How to Use":
        show_how_to_use()
    elif page == "AI Assistant":
        show_ai_assistant()

def show_about_us():
    st.title("👥 About Us")
    
    st.markdown("""
    <div style="padding: 2rem; 
                border-radius: 1rem; 
                background-color: #ffffff;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 2rem;">
        <h2 style="color: #2c3e50; margin-bottom: 1.5rem;">Our Team</h2>
        <p style="color: #34495e; font-size: 1.1rem; line-height: 1.6;">
            We are a team of three students: <strong>Harsh, Tanish, and Bhavishya</strong>. We created this 
            <strong>Student Management System</strong> as our Computer Science project under the guidance of 
            <strong>Deepak Meena Sir</strong>.
        </p>
        <p style="color: #34495e; font-size: 1.1rem; line-height: 1.6;">
            Our aim is to help students manage their tasks, habits, and productivity in a structured manner. 
            We believe that an organized approach to time management can significantly boost efficiency and success.
        </p>
        <p style="color: #34495e; font-size: 1.1rem; line-height: 1.6;">
            This system is designed with a modern UI and AI-powered assistance to ensure seamless productivity tracking.
        </p>
    </div>
    
    <div style="padding: 2rem; 
                border-radius: 1rem; 
                background-color: #ffffff;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #2c3e50; margin-bottom: 1.5rem;">Key Features</h2>
        <ul style="color: #34495e; font-size: 1.1rem; line-height: 1.6;">
            <li>Task Management System</li>
            <li>Habit Tracking</li>
            <li>Progress Monitoring</li>
            <li>Journal Entries</li>
            <li>AI-Powered Assistant</li>
            <li>Modern and User-Friendly Interface</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_how_to_use():
    st.title("❓ How to Use")
    
    # Getting Started Section
    st.markdown("""
    ### 🚀 Getting Started
    1. **Register/Login**: Create an account or login to access all features
    2. **Dashboard**: View your overview and quick statistics
    3. **Tasks**: Add and manage your daily tasks
    4. **Habits**: Track your daily, weekly, or monthly habits
    5. **Progress**: Monitor your productivity scores
    6. **Journal**: Write and maintain your daily thoughts
    7. **AI Assistant**: Get help from our AI chatbot
    """)
    
    # Features Guide Section
    st.subheader("Features Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📝 Tasks
        Add tasks with titles, descriptions, deadlines, and priority levels. Mark them as complete when done.
        
        #### 🎯 Habits
        Create habits you want to maintain and track your streaks with daily check-ins.
        
        #### 📈 Progress
        Rate your daily productivity and add notes to track your progress over time.
        """)
    
    with col2:
        st.markdown("""
        #### 📔 Journal
        Write daily journal entries and track your mood to maintain a personal record.
        
        #### 🤖 AI Assistant
        Get help with your tasks, schedule management, and productivity tips from our AI chatbot.
        """)

def show_ai_assistant():
    st.title("🤖 AI Assistant")
    
    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Assistant:** {content}")
    
    # Chat input with automatic clearing
    # Create a unique key for the text input
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0
        
    user_input = st.text_input(
        "Ask me anything about productivity, task management, or study tips!",
        key=f"chat_input_{st.session_state.chat_input_key}"
    )
    
    if user_input:
        try:
            # Add context to make responses more varied
            context = (
                "You are a helpful AI assistant focused on productivity and student success. "
                "Provide varied, personalized responses based on the specific question. "
                "Previous context: " + str([m["content"] for m in st.session_state.chat_history[-2:] if m["role"] == "assistant"])
            )
            
            prompt = context + "\n\nUser: " + user_input
            response = model.generate_content(prompt)
            ai_response = response.text
            
            # Add messages to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Increment the key to create a new input field
            st.session_state.chat_input_key += 1
            
            st.rerun()
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

def show_dashboard():
    st.title("📊 Student Productivity Hub")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    conn = get_db_connection()
    with col1:
        pending_tasks = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM tasks WHERE status='pending' AND user_id=?",
            conn, params=(st.session_state.user_id,)
        ).iloc[0]['count']
        st.metric("Pending Tasks", pending_tasks)
    
    with col2:
        total_habits = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM habits WHERE user_id=?",
            conn, params=(st.session_state.user_id,)
        ).iloc[0]['count']
        st.metric("Active Habits", total_habits)
    
    with col3:
        avg_progress = pd.read_sql_query(
            "SELECT AVG(score) as avg FROM progress WHERE user_id=?",
            conn, params=(st.session_state.user_id,)
        ).iloc[0]['avg']
        st.metric("Average Progress", f"{avg_progress:.1f}/10" if avg_progress else "No data")
    
    conn.close()

    # Recent tasks
    st.subheader("Recent Tasks")
    show_recent_tasks()
    
    # Progress chart
    st.subheader("Progress Overview")
    show_progress_chart()

def show_tasks():
    st.title("📝 Task Management")
    
    # Add new task
    with st.form("new_task"):
        st.subheader("Add New Task")
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        col1, col2 = st.columns(2)
        with col1:
            deadline = st.date_input("Deadline")
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"])
        
        submitted = st.form_submit_button("Add Task")
        if submitted and title:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO tasks (user_id, title, description, deadline, priority, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (st.session_state.user_id, title, description, deadline.strftime('%Y-%m-%d'), 
                  priority, 'pending'))
            conn.commit()
            conn.close()
            st.success("Task added successfully!")

    # Show existing tasks
    status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
    show_task_list(status_filter)

def show_habits():
    st.title("🎯 Habit Tracker")
    
    # Add new habit
    with st.form("new_habit"):
        st.subheader("Create New Habit")
        habit_name = st.text_input("Habit Name")
        description = st.text_area("Description")
        frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
        
        submitted = st.form_submit_button("Add Habit")
        if submitted and habit_name:
            conn = get_db_connection()
            today = datetime.now().strftime('%Y-%m-%d')
            conn.execute("""
                INSERT INTO habits (user_id, habit_name, description, frequency, 
                                  start_date, last_checked, streak)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (st.session_state.user_id, habit_name, description, frequency, 
                  today, today, 0))
            conn.commit()
            conn.close()
            st.success("Habit created successfully!")

    # Show existing habits
    show_habit_list()

def show_progress():
    st.title("📈 Progress Tracker")
    
    # Daily progress input
    with st.form("progress_form"):
        st.subheader("Rate Your Day")
        score = st.slider("Productivity Score", 1, 10, 5)
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Save Progress")
        
        if submitted:
            conn = get_db_connection()
            today = datetime.now().strftime('%Y-%m-%d')
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO progress (user_id, date, score, notes)
                    VALUES (?, ?, ?, ?)
                """, (st.session_state.user_id, today, score, notes))
                conn.commit()
                st.success("Progress saved!")
            except sqlite3.Error as e:
                st.error(f"Error saving progress: {e}")
            finally:
                conn.close()

    # Show progress chart
    show_progress_chart()

def show_journal():
    st.title("📔 Journal")
    
    # Add journal entry
    with st.form("journal_form"):
        st.subheader("New Entry")
        entry_date = st.date_input("Date", datetime.now())
        content = st.text_area("Write your thoughts...")
        mood = st.select_slider("Mood", ["😔", "😐", "😊", "😄", "🌟"])
        
        submitted = st.form_submit_button("Save Entry")
        if submitted and content:
            conn = get_db_connection()
            conn.execute("""
                INSERT INTO journal_entries (user_id, entry_date, content, mood)
                VALUES (?, ?, ?, ?)
            """, (st.session_state.user_id, entry_date.strftime('%Y-%m-%d'), 
                  content, mood))
            conn.commit()
            conn.close()
            st.success("Journal entry saved!")

    # Show past entries
    show_journal_entries()

# Helper functions for showing data
def show_recent_tasks():
    conn = get_db_connection()
    tasks = pd.read_sql_query("""
        SELECT title, deadline, status, priority
        FROM tasks 
        WHERE user_id = ? 
        ORDER BY deadline DESC 
        LIMIT 5
    """, conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not tasks.empty:
        st.dataframe(tasks, use_container_width=True)
    else:
        st.info("No tasks found. Add your first task!")

def show_task_list(status_filter):
    conn = get_db_connection()
    if status_filter == "All":
        tasks = pd.read_sql_query("""
            SELECT * FROM tasks 
            WHERE user_id = ? 
            ORDER BY deadline
        """, conn, params=(st.session_state.user_id,))
    else:
        tasks = pd.read_sql_query("""
            SELECT * FROM tasks 
            WHERE user_id = ? AND status = ? 
            ORDER BY deadline
        """, conn, params=(st.session_state.user_id, status_filter.lower()))
    conn.close()

    for _, task in tasks.iterrows():
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"""
                <div style="padding: 1rem; 
                           border-radius: 0.5rem; 
                           background-color: {'#f8f9fa' if task['status']=='completed' else '#ffffff'}; 
                           border-left: 4px solid {'#28a745' if task['priority']=='high' 
                                                 else '#ffc107' if task['priority']=='medium' 
                                                 else '#6c757d'};
                           box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #2c3e50; margin-bottom: 0.5rem;">{task['title']}</h3>
                    <p style="color: #495057; margin-bottom: 0.5rem;">{task['description']}</p>
                    <p style="color: #6c757d;">Deadline: {task['deadline']} | Status: {task['status'].title()}</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if task['status'] == 'pending':
                if st.button("✅ Complete", key=f"complete_{task['id']}"):
                    conn = get_db_connection()
                    conn.execute(
                        "UPDATE tasks SET status = 'completed' WHERE id = ? AND user_id = ?",
                        (task['id'], st.session_state.user_id)
                    )
                    conn.commit()
                    conn.close()
                    st.rerun()
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                conn = get_db_connection()
                conn.execute(
                    "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                    (task['id'], st.session_state.user_id)
                )
                conn.commit()
                conn.close()
                st.rerun()

def show_habit_list():
    conn = get_db_connection()
    habits = pd.read_sql_query("""
        SELECT * FROM habits 
        WHERE user_id = ? 
        ORDER BY streak DESC
    """, conn, params=(st.session_state.user_id,))
    conn.close()

    for _, habit in habits.iterrows():
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"""
                <div style="padding: 1rem; 
                           border-radius: 0.5rem; 
                           background-color: white; 
                           border-left: 4px solid #28a745;
                           box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #2c3e50; margin-bottom: 0.5rem;">{habit['habit_name']}</h3>
                    <p style="color: #495057; margin-bottom: 0.5rem;">{habit['description']}</p>
                    <p style="color: #6c757d;">Frequency: {habit['frequency']} | Streak: {habit['streak']} days</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("✅ Check-in", key=f"habit_{habit['id']}"):
                conn = get_db_connection()
                today = datetime.now().strftime('%Y-%m-%d')
                last_check = datetime.strptime(habit['last_checked'], '%Y-%m-%d')
                
                if last_check.date() < datetime.now().date():
                    conn.execute("""
                        UPDATE habits 
                        SET last_checked = ?, streak = streak + 1 
                        WHERE id = ? AND user_id = ?
                    """, (today, habit['id'], st.session_state.user_id))
                    conn.commit()
                    st.success("Habit checked!")
                else:
                    st.info("Already checked in today!")
                conn.close()
                st.rerun()
        with col3:
            if st.button("🗑️ Delete", key=f"delete_habit_{habit['id']}"):
                conn = get_db_connection()
                conn.execute(
                    "DELETE FROM habits WHERE id = ? AND user_id = ?",
                    (habit['id'], st.session_state.user_id)
                )
                conn.commit()
                conn.close()
                st.rerun()

def show_progress_chart():
    conn = get_db_connection()
    progress_data = pd.read_sql_query("""
        SELECT date, score, notes 
        FROM progress 
        WHERE user_id = ? 
        ORDER BY date
    """, conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not progress_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=progress_data['date'],
            y=progress_data['score'],
            mode='lines+markers',
            name='Daily Score',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title='Your Productivity Trend',
            xaxis_title='Date',
            yaxis_title='Score',
            yaxis_range=[0, 10],
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show notes in expandable section
        if st.checkbox("Show detailed notes"):
            for _, row in progress_data.iterrows():
                if row['notes']:
                    st.markdown(f"**{row['date']}** (Score: {row['score']})")
                    st.markdown(f"> {row['notes']}")
    else:
        st.info("Start tracking your progress to see the trend!")

def show_journal_entries():
    conn = get_db_connection()
    entries = pd.read_sql_query("""
        SELECT * FROM journal_entries 
        WHERE user_id = ? 
        ORDER BY entry_date DESC
    """, conn, params=(st.session_state.user_id,))
    conn.close()
    
    for _, entry in entries.iterrows():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
                <div style="padding: 1rem; 
                           border-radius: 0.5rem; 
                           background-color: white; 
                           margin-bottom: 1rem;
                           border-left: 4px solid #1f77b4;
                           box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4 style="color: #2c3e50;">{entry['entry_date']} {entry['mood']}</h4>
                    <p style="color: #495057;">{entry['content']}</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🗑️ Delete", key=f"delete_entry_{entry['id']}"):
                conn = get_db_connection()
                conn.execute(
                    "DELETE FROM journal_entries WHERE id = ? AND user_id = ?",
                    (entry['id'], st.session_state.user_id)
                )
                conn.commit()
                conn.close()
                st.rerun()


# Add this at the end of your Python file, replacing the existing custom CSS section

st.markdown("""
<style>
    /* Reset and base styles */
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Navigation Sidebar Styling */
    .css-1d391kg, .css-1oyoqpm {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 14rem !important;
        height: 100vh !important;
        background-color: #1e1e1e !important;
        z-index: 999 !important;
        overflow-y: auto !important;
    }

    /* Main Content Adjustment */
    .main .block-container {
        margin-left: 15rem !important;
        padding: 2rem 2rem !important;
        max-width: calc(100% - 15rem) !important;
    }

    /* Sidebar Content Styling */
    .css-1d391kg .stRadio {
        padding: 0.5rem 1rem !important;
    }

    .css-1d391kg .stRadio > label {
        color: white !important;
    }

    /* Custom styling for navigation items */
    .stSidebar .sidebar-content {
        background-color: #1e1e1e !important;
    }

    .css-1d391kg .stRadio > div[role="radiogroup"] {
        margin-top: 1rem !important;
    }

    .css-1d391kg .stRadio > div[role="radiogroup"] > label {
        padding: 0.5rem 1rem !important;
        margin-bottom: 0.5rem !important;
        border-radius: 0.25rem !important;
        transition: background-color 0.2s !important;
    }

    .css-1d391kg .stRadio > div[role="radiogroup"] > label:hover {
        background-color: #2d2d2d !important;
    }

    /* Navigation Title */
    .css-1d391kg h1 {
        color: white !important;
        padding: 1rem !important;
        margin: 0 !important;
        font-size: 1.5rem !important;
    }

    /* Logout Button Styling */
    .css-1d391kg .stButton button {
        width: 100% !important;
        margin-top: 1rem !important;
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.25rem !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
    }

    .css-1d391kg .stButton button:hover {
        background-color: #c82333 !important;
    }

    /* Hide Streamlit's default menu button */
    .css-fblp2m {
        visibility: hidden !important;
    }

    /* App Header Styling */
    .stApp header {
        background-color: transparent !important;
        border-bottom: none !important;
    }

    /* Scrollbar Styling */
    .css-1d391kg::-webkit-scrollbar {
        width: 5px !important;
    }

    .css-1d391kg::-webkit-scrollbar-track {
        background: #1e1e1e !important;
    }

    .css-1d391kg::-webkit-scrollbar-thumb {
        background: #888 !important;
        border-radius: 5px !important;
    }

    .css-1d391kg::-webkit-scrollbar-thumb:hover {
        background: #555 !important;
    }

    /* Active Navigation Item */
    .css-1d391kg .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #0d6efd !important;
        color: white !important;
    }

    /* Card Styling */
    .card {
        padding: 1.5rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 1rem !important;
        background-color: white !important;
        transition: transform 0.2s !important;
    }

    .metric-card {
        text-align: center !important;
        padding: 2rem !important;
        background: linear-gradient(145deg, #ffffff, #f5f7fa) !important;
    }

    /* Responsive adjustments */
    @media screen and (max-width: 768px) {
        .main .block-container {
            margin-left: 0 !important;
            max-width: 100% !important;
        }
        
        .css-1d391kg {
            width: 100% !important;
            transform: translateX(-100%) !important;
            transition: transform 0.3s ease-in-out !important;
        }
        
        .css-1d391kg.shown {
            transform: translateX(0) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    if st.session_state.user_id is None:
        show_auth_ui()
    else:
        main()