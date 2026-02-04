# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from mysql.connector import Error

# ----------------- Database Config -----------------
DB_NAME = "student_db"
DB_USER = "student_user"
DB_PASSWORD = "12345678"
DB_HOST = "localhost"

def get_connection():
    """Establish a connection to MySQL and ensure the 'students' table exists."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            gender VARCHAR(10),
            math_score INT,
            reading_score INT,
            writing_score INT,
            average_score FLOAT,
            grade VARCHAR(2),
            pass_fail VARCHAR(10)
        )
        """)
        conn.commit()
        cursor.close()
        return conn
    except Error as e:
        st.error(f"❌ Error connecting to MySQL: {e}")
        return None

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="🎓 Student Performance App",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Sidebar Navigation -----------------
st.sidebar.title("📚 Student App")
menu = ["🏠 Home","➕ Add Student","📋 View / Update / Delete","📊 Charts","💾 Export CSV"]
choice = st.sidebar.radio("Navigation", menu)

# ----------------- Home -----------------
if choice == "🏠 Home":
    st.markdown("## Welcome to the Student Performance Management System 🎓")
    st.write("""
    Manage student records efficiently:
    - Add, update, or delete students
    - Visualize performance with charts
    - Export records to CSV for reports
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)

# ----------------- Add Student -----------------
elif choice == "➕ Add Student":
    st.header("Add New Student ➕")
    with st.form("student_form", clear_on_submit=True):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        gender = st.selectbox("Gender", ["Male", "Female"])
        math_score = st.number_input("Math Score", 0, 100)
        reading_score = st.number_input("Reading Score", 0, 100)
        writing_score = st.number_input("Writing Score", 0, 100)
        submit = st.form_submit_button("Add Student")

        if submit:
            average = (math_score + reading_score + writing_score) / 3
            grade = "A" if average >= 90 else "B" if average >= 75 else "C" if average >= 60 else "D" if average >= 50 else "F"
            pass_fail = "Pass" if average >= 35 else "Fail"

            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                query = """
                INSERT INTO students
                (first_name,last_name,gender,math_score,reading_score,writing_score,average_score,grade,pass_fail)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
                cursor.execute(query, (first_name,last_name,gender,math_score,reading_score,writing_score,average,grade,pass_fail))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"✅ Student {first_name} {last_name} added successfully!")

# ----------------- View / Update / Delete -----------------
elif choice == "📋 View / Update / Delete":
    st.header("View / Update / Delete Students 📋")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM students", conn)
        st.dataframe(df)
        st.markdown("---")
        st.subheader("Update / Delete a Student ✏️ / 🗑️")
        
        student_ids = df["student_id"].tolist()
        if student_ids:
            selected_id = st.selectbox("Select Student ID", student_ids)
            action = st.radio("Action", ["Update ✏️", "Delete 🗑️"])
            
            if st.button("Proceed"):
                cursor = conn.cursor()
                if action == "Delete 🗑️":
                    cursor.execute("DELETE FROM students WHERE student_id=%s", (selected_id,))
                    conn.commit()
                    st.success(f"✅ Student ID {selected_id} deleted successfully!")
                else:  # Update
                    student = df[df["student_id"] == selected_id].iloc[0]
                    st.info("Fill new details to update the student:")
                    first_name = st.text_input("First Name", student["first_name"])
                    last_name = st.text_input("Last Name", student["last_name"])
                    gender = st.selectbox("Gender", ["Male", "Female"], index=0 if student["gender"]=="Male" else 1)
                    math_score = st.number_input("Math Score", 0, 100, int(student["math_score"]))
                    reading_score = st.number_input("Reading Score", 0, 100, int(student["reading_score"]))
                    writing_score = st.number_input("Writing Score", 0, 100, int(student["writing_score"]))
                    
                    if st.button("Update Student ✏️"):
                        average = (math_score + reading_score + writing_score) / 3
                        grade = "A" if average >= 90 else "B" if average >= 75 else "C" if average >= 60 else "D" if average >= 50 else "F"
                        pass_fail = "Pass" if average >= 35 else "Fail"
                        query = """
                        UPDATE students SET first_name=%s,last_name=%s,gender=%s,
                        math_score=%s,reading_score=%s,writing_score=%s,
                        average_score=%s,grade=%s,pass_fail=%s WHERE student_id=%s
                        """
                        cursor.execute(query, (first_name,last_name,gender,math_score,reading_score,writing_score,average,grade,pass_fail,selected_id))
                        conn.commit()
                        st.success(f"✅ Student ID {selected_id} updated successfully!")
                cursor.close()
        else:
            st.info("No student records found.")
        conn.close()

# ----------------- Charts -----------------
elif choice == "📊 Charts":
    st.header("Student Performance Charts 📊")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM students", conn)
        conn.close()
        if not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Average Marks per Subject")
                st.bar_chart(df[["math_score","reading_score","writing_score"]].mean())
            with col2:
                st.subheader("Pass vs Fail")
                counts = df["pass_fail"].value_counts()
                fig1, ax1 = plt.subplots()
                ax1.pie(counts, labels=counts.index, autopct="%1.1f%%", colors=["green","red"])
                st.pyplot(fig1)

            st.subheader("Score Correlation Heatmap")
            fig2, ax2 = plt.subplots(figsize=(6,4))
            sns.heatmap(df[["math_score","reading_score","writing_score","average_score"]].corr(), annot=True, ax=ax2)
            st.pyplot(fig2)
        else:
            st.info("No data to display charts.")

# ----------------- Export CSV -----------------
elif choice == "💾 Export CSV":
    st.header("Export Data to CSV 💾")
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM students", conn)
        conn.close()
        if not df.empty:
            df.to_csv("students_export.csv", index=False)
            st.success("✅ Data exported successfully to students_export.csv")
            st.download_button("Download CSV", data=open("students_export.csv","rb"), file_name="students_export.csv")
        else:
            st.info("No data to export.")
