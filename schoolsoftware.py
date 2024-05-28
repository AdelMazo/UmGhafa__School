from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, url_for, session, flash, make_response
import psycopg2
import logging
from datetime import date, datetime
from passlib.hash import bcrypt
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from psycopg2 import connect, sql, Error as Psycopg2Error
import random
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Inches
from bs4 import BeautifulSoup
import requests







logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

app = Flask(__name__)
app.secret_key = 'Ck0PmY6ZvDDo+YA6iFTAP4OkUzHjKBo+ZHTnfGNZwUK9Cj/xUxkT0WaAqzV0mRTy'

# Database connection
conn = psycopg2.connect(
    dbname='adel_mazouzi_qfv4',
    user='adel_mazouzi_qfv4_user',
    password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
    host='dpg-cpakbfn109ks73apokt0-a',
    port='5432'
)
cur = conn.cursor()
def initialize_my_database(teachers_data):
    try:
        # Connect to the database
        print("Connecting to the database...")
        with psycopg2.connect(
            dbname='adel_mazouzi_qfv4',
    	    user='adel_mazouzi_qfv4_user',
    	    password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
    	    host='dpg-cpakbfn109ks73apokt0-a',
    	    port='5432'
        ) as conn:
            print("Connected to the database.")
            with conn.cursor() as cursor:
                # Check if the table exists
                print("Checking if table 'tblteachers' exists...")
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                    ('tblteachers',)
                )
                table_exists = cursor.fetchone()[0]
                print(f"Table exists: {table_exists}")

                # If the table doesn't exist, create it
                if not table_exists:
                    print("Creating table 'tblteachers'...")
                    create_table_query = """
                        CREATE TABLE tblteachers (
                            id SERIAL PRIMARY KEY,
                            employee_name VARCHAR(255),
                            date_of_birth DATE,
                            gender VARCHAR(10),
                            job_id VARCHAR(50),
                            email VARCHAR(100),
                            mission VARCHAR(100),
                            subject VARCHAR(100),
                            phone_number VARCHAR(15),
                            coordinator BOOLEAN,
                            teacher_classes VARCHAR(100),
                            password VARCHAR(100),
                            "group_number" VARCHAR(20)
                        )
                    """
                    cursor.execute(create_table_query)

                    # Insert initial data
                    print("Inserting initial data...")
                    insert_query = """
                        INSERT INTO tblteachers (
                            employee_name,
                            date_of_birth,
                            gender,
                            job_id,
                            email,
                            mission,
                            subject,
                            phone_number,
                            coordinator,
                            teacher_classes,
                            password,
                            "group_number"
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # Clean and format the data for insertion
                    cleaned_data = []
                    for record in teachers_data:
                        # Convert empty strings to None for nullable fields
                        date_of_birth = record[1] if record[1] else None
                        coordinator = True if record[8].lower() == 'true' else False
                        group_number = record[11] if record[11] else None
                        cleaned_record = (
                            record[0], date_of_birth, record[2], record[3], record[4],
                            record[5], record[6], record[7], coordinator, record[9], record[10], group_number
                        )
                        cleaned_data.append(cleaned_record)
                    
                    # Execute parameterized query for each record
                    cursor.executemany(insert_query, cleaned_data)

                    # Commit changes to the database
                    print("Committing changes to the database...")
                    conn.commit()
                    print("Table 'tblteachers' created and initial data inserted successfully.")
                else:
                    print("Table 'tblteachers' already exists. Skipping creation and data insertion.")

    except Exception as e:
        print(f"Error initializing database: {e}")

teachers_data = [
    ("Andy Corchado Javier Ortiz Corchado", "", "male", "20553AD", "Andy.Corchado@ese.gov.ae", "TEACHER", "CCDI", "", "", "", "Andy@OrtizJavier$%", ""),
    ("EBTESAM SAEED MOHAMMED ALMEQBAALI", "", "female", "29461AD", "Ebtesam.Almeqbaali@ese.gov.ae", "TEACHER", "ISLAMIC", "", "", "", "Ebtesam$MohammedAlmeqbaali#%", ""),
    ("AHMAD JEHAD AHMAD SEMREEN", "", "male", "38179AD", "Ahmad.Semreen@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Ahmad#SemreenJehad$%", ""),
    ("AHMAD HASAN SABRI AHMAD", "", "male", "13561AD", "Ahmad.Ahmad@ese.gov.ae", "TEACHER", "", "", "", "", "Ahmad@SabriHasan#%", ""),
    ("AHMED SALEH MOHAMED AHMED", "", "male", "42427ad", "Ahmed-S.Ahmed@ese.gov.ae", "TEACHER", "SOCIAL STUDIES", "", "", "", "Ahmed$SalehMohamed#%", ""),
    ("AHMED ADEL AHMED EBRAHEM AGGOUR", "", "male", "39415ad", "Ahmed.Aggour@ese.gov.ae", "TEACHER", "ENGLISH", "", "TRUE", "", "Ahmed#AdelAggour$%", ""),
    ("Ahmad Faisal Mohammad Mohammad", "", "male", "36702AD", "Ahmad.Mmohammad@ese.gov.ae", "TEACHER", "PHYSICS", "", "", "", "Ahmad@MohammadFaisal$%", ""),
    ("Ashraf Mohamed Hussein Elsharkawy", "", "male", "38491AD", "Ashraf.Elsharkawy@ese.gov.ae", "TEACHER", "DRAMA", "", "", "", "Ashraf$ElsharkawyHussein#%", ""),
    ("Afrah Abdulla Ali Mohammed Alshimmari", "", "female", "14267AD", "Afrah.Alshmmari@ese.gov.ae", "TEACHER", "", "", "", "", "Afrah#AlshimmariAbdulla$%", ""),
    ("Elhassan Hossni Mohamed Sayd Ahmed Elgendi", "", "male", "14017AD", "Elhassan.Elgendi@ese.gov.ae", "TEACHER", "", "", "", "", "Elhassan@ElgendiHossni$%", ""),
    ("ELSAID ALI ABOUELMAATI ALI", "", "male", "TID-0097380", "TID-Elsaid.Ali@ese.gov.ae", "TEACHER", "ENGLISH", "", "", "", "Elsaid$AbouelmaatiAli#%", ""),
    ("Elsayed Abdelfattah Elsayed Abdelfattah", "", "male", "TID-0016476", "TID-e.abdelfattah@ese.gov.ae", "TEACHER", "ENGLISH", "", "", "", "Elsayed#AbdelfattahElsayed$%", ""),
    ("AMIRA ABDELRAFE MANSOUR MOHAMED ELSHARKAWY", "", "female", "5357AD", "Amira.Alshrkawi@ese.gov.ae", "TEACHER", "", "", "", "", "Amira$ElsharkawyMansour#%", ""),
    ("ANU ARAYATHINAL SAVIO", "", "male", "35645AD", "Anu.Savio@ese.gov.ae", "TEACHER", "PHYSICS", "", "", "", "Anu@SavioArayathinal$%", ""),
    ("EHAB MOHAMED ABDELSATTAR ELSAYED", "", "male", "7125AD", "Ehab.Elnahas@ese.gov.ae", "TEACHER", "CCDI", "", "TRUE", "", "Ehab#ElsayedAbdelsattar@%", ""),
    ("AYOOB MOHAMED YOOSIF ADAM", "", "male", "42570ad", "Ayoob.Adam@ese.gov.ae", "TEACHER", "ENGLISH", "", "", "", "Ayoub@AdamYoosif#%", ""),
    ("JAMAL AHMAD AUAD AL LOUBANI", "", "male", "2322AD", "Jamal.Alloubani@ese.gov.ae", "TEACHER", "ARABIC", "", "", "", "Jamal@LoubaniAuad#%", ""),
    ("Hatem Mohamed Elrphay Abdalrehim", "", "male", "2901AD", "Hatem.Abdalrehem@ese.gov.ae", "TEACHER", "", "", "", "", "Hatem$AbdalrehimElrphay#%", ""),
    ("HASSAN ISMAIL MOHAMMAD AL FAR", "", "male", "8115AD", "Hassan.Alfar@ese.gov.ae", "TEACHER", "ENGLISH", "", "", "", "Hassan#AlfarIsmail$%", ""),
    ("Hamza Al Mesaouil", "", "male", "38024ad", "Hamza.Almesaouil@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Hamza%Mesaouil@#%", ""),
    ("Khaula Mohammed Rashed Sulaiman Almarbooei", "", "female", "9687AD", "Khaula.Almarboi@ese.gov.ae", "TEACHER", "", "", "", "", "Khaula@RashedAlmarbooei#%", ""),
    ("Dileep Krishnan Poruppath", "", "male", "37288AD", "Dileep.Poruppath@ese.gov.ae", "TEACHER", "PHYSICS", "", "", "", "Dileep#KrishnanPoruppath$%", ""),
    ("SADATH CHERIYA RAYAROTH KUNHABDULLA CHERIYA RAYAROTH", "", "male", "36978AD", "Sadath.Rayaroth@ese.gov.ae", "TEACHER", "SCIENCE", "", "", "", "Sadath@CheriyaRayaroth$%", ""),
    ("Salem Khalfan Humaid Mohammed Al Ghaithi", "", "male", "2703AD", "Salem.Alghaithi@ese.gov.ae", "", "", "", "", "", "Salem@KhalfanAlghaithi#%", ""),
    ("Shardul Mishra", "", "male", "37876AD", "Shardul.Mishra@ese.gov.ae", "TEACHER", "SCIENCE", "", "", "", "Shardul$Mishra#%", ""),
    ("CHIHEB BIN CHOUCHENE", "", "male", "36713AD", "Chiheb.Chouchene@ese.gov.ae", "TEACHER", "PHYSICAL EDUCATION", "", "", "", "Chiheb#BinChouchene@%", ""),
    ("SHAHEERA JAMIL HAMAD SALEM ALHAMDANI", "", "female", "1050AD", "Shaheera.Alhamadani@ese.gov.ae", "TEACHER", "SCIENCE", "", "", "", "Shaheera@JamilAlhamdani#%", ""),
    ("SALAH SALIM RASHED ALMUKHAINI", "", "male", "42585ad", "Salah.Almukhaini@ese.gov.ae", "", "", "", "", "", "Salah@SalimAlmukhaini$%", ""),
    ("SUHIB JAMAL ISMAIL ALSHOUBAKI", "", "male", "36587AD", "Suhib.Alshoubaki@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Suhib@JamalAlshoubaki#%", ""),
    ("AYSHA SAEED HAMAD ALSAEDI", "", "female", "6845AD", "Aysha-Sh.Alsaedi@ese.gov.ae", "TEACHER", "", "", "", "", "Aysha$SaeedAlsaedi@#", ""),
    ("Adel Mazouzi", "", "male", "35627AD", "Adel.Mazouzi@ese.gov.ae", "TEACHER", "MUSIC", "", "TRUE", "", "Adel%Mazouzi@#", ""),
    ("AYED HUSSEIN YUSUF DARAGHMEH", "", "male", "3650AD", "Ayed.Daraghmeh@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Ayed$HusseinDaraghmeh@%", ""),
    ("ABDULELAH OKLEH FARIS FARIS", "", "male", "9360AD", "Abdulelah.Faris@ese.gov.ae", "TEACHER", "ARABIC", "", "TRUE", "", "Abdulelah#OklehFaris@%", ""),
    ("ABDEL RAHMAN TAYSEER HUSSEIN MOWAFI", "", "male", "38114ad", "Abdel.Mowafi@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Abdelrahman$TayseerMowafi@#", ""),
    ("ABDULLA KHAMIS SAEED ALMEQBAALI", "", "male", "9373AD", "Abdulla.Almeqbali@ese.gov.ae", "", "", "", "", "", "Abdulla@KhamisAlmeqbali#%", ""),
    ("Abdulla Rashed Saeed Al Kindi", "", "male", "8153AD", "Abdulla.Alkendi@ese.gov.ae", "", "", "", "", "", "Abdulla@RashedAlkindi#%", ""),
    ("ABDULLA NASSER MOHAMMED NASSER AL ABDUL SALAM", "", "male", "13600AD", "Abdullah.Alsalaamy@ese.gov.ae", "TEACHER", "", "", "", "", "Abdulla%NasserAlabdulsalam@#", ""),
    ("ITANI NDLOVU", "", "male", "40195AD", "Itani.Ndlovu@ese.gov.ae", "TEACHER", "ENGLISH", "", "", "", "Itani$Ndlovu#%", ""),
    ("ALAA MOUSAA IBRAHIM MOUSSA", "", "male", "11510AD", "Alaa.Moussa@ese.gov.ae", "TEACHER", "CHEMISTRY", "", "", "", "Alaa%MousaaMoussa@#", ""),
    ("GHUWAYA RASHED NASSER OBAID ALDEREI", "", "female", "24043AD", "Ghuwaya.Alderei@ese.gov.ae", "TEACHER", "ISLAMIC", "", "", "", "Ghuwaya@RashedObaid$%", ""),
    ("FERAS AHMAD SHEHADEH SALEH", "", "male", "35060AD", "Feras.Saleh@ese.gov.ae", "TEACHER", "", "", "", "", "Feras@AhmadSaleh#%", ""),
    ("Feras Mohmmad Sleman Al Anber", "", "male", "9850AD", "Feras.Alanber@ese.gov.ae", "TEACHER", "ARABIC", "", "", "", "Feras$MohammadAnber@#", ""),
    ("QUSEI MOHMMAD SROOR KHAMAYSEH", "", "male", "13322AD", "Qusei.Khamaysaeh@ese.gov.ae", "TEACHER", "MATH", "", "TRUE", "", "Qusei#MohammadKhamayseh$%", ""),
    ("Kamla Awad Mardad Tuwairesh Alhanaee", "", "female", "25470AD", "Kamla.Alhanaee@ese.gov.ae", "TEACHER", "", "", "", "", "Kamla$AwadTuwairesh@%", ""),
    ("Latifa Rashed Khalfan Ali Al Shamsi", "", "female", "27167AD", "Latifa-Rk.Alshamsi@ese.gov.ae", "TEACHER", "", "", "", "", "Latifa@RashedAlshamsi#%", ""),
    ("Liam James Mcevoy", "", "male", "34667AD", "Liam.Mcevoy@ese.gov.ae", "TEACHER", "PHYSICAL EDUCATION", "", "", "", "Liam$JamesMcevoy@%", ""),
    ("Llewellyn George James", "", "male", "33317AD", "Llewellyn.James@ese.gov.ae", "TEACHER", "BIOLOGY", "", "", "", "Llewellyn#GeorgeJames$%", ""),
    ("Mehrez Mohamed Ellouz", "", "male", "36344AD", "Mehrez.Ellouz@ese.gov.ae", "TEACHER", "VISUAL ARTS", "", "", "", "Mehrez@MohamedEllouz#%", ""),
    ("Mohamed Gaber Mahmoud Elsayed", "", "male", "14884AD", "Mohammed.Elsayed@ese.gov.ae", "TEACHER", "SOCIAL STUDIES", "", "TRUE", "",  "Mohamed#GaberElsayed$%", ""),
    ("MOHAMMAD SALEM HUSSEIN ALSHARAWNEH", "", "male", "37380AD", "Mohammad.Alsharawneh@ese.gov.ae", "TEACHER", "CCDI", "", "", "", "Mohammad@SalemAlsharawneh$%", ""),
    ("Mohamed Attia Ali Ibrahim", "", "male", "15419AD", "Mohamed-A.Ibrahim@ese.gov.ae", "TEACHER", "ARABIC", "", "", "", "Mohamed@AttiaIbrahim$#", ""),
    ("Mohamed Medhat Mohamed Eldanasouri", "", "male", "21355AD", "Mohamed.Eldanasouri@ese.gov.ae", "TEACHER", "CHEMISTRY", "", "TRUE", "", "Mohamed$MedhatEldanasouri@#", ""),
    ("MOHD MUSBAH ABDELQADER INAIM", "", "male", "838AD", "Mohamed.Inaim@ese.gov.ae", "TEACHER", "ARABIC", "", "", "", "Mohd@MusbahInaim$%", ""),
    ("Mariam Salem Ali Saeed Alkindi", "", "female", "23963AD", "Mariam-Sa.Alkindi@ese.gov.ae", "TEACHER", "SOCIAL STUDIES", "", "", "", "Mariam$SalemAlkindi@%", ""),
    ("Mariam Ali Nasser Alsenani", "", "female", "24061AD", "Mariam.Alsenaani@ese.gov.ae", "TEACHER", "ARABIC", "", "", "", "Mariam@AliAlsenani$%", ""),
    ("MOUSTAFA MOUSTAFA MOHAMED ABDOU", "", "male", "10353AD", "Moustafa.Abdou@ese.gov.ae", "TEACHER", "MATH", "", "", "","Moustafa%MohamedAbdou@%", ""),
    ("MOATH JAMAL M SALEH", "", "male", "38075AD", "Moath.Saleh@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Moath@JamalSaleh$%", ""),
    ("Mohannad Khaleel Subhi Suleiman", "", "male", "38149AD", "Mohannad.Suleiman@ese.gov.ae", "TEACHER", "MATH", "", "", "", "Mohannad@KhaleelSuleiman$%", ""),
    ("Nasser Husain Nasser Aleissaee", "", "male", "42837ad", "Nasser.Aleissaee@ese.gov.ae", "", "", "", "", "", "Nasser@HusainAleissaee$%", ""),
    ("NAEEMA MOHAMMED SAEED MOHAMMED ALKAABI", "", "female", "41749ad", "Naeema-M.Alkaabi@ese.gov.ae", "", "", "", "", "", "Naeema$MohammedAlkaabi#%", ""),
    ("Haitham Sulaiman Ali Alshamsi", "", "male", "43064ad", "Haitham.Alshamsi@ese.gov.ae", "TEACHER", "ENGLISH", "", "", "","Haitham$SulaimanAlshamsi@%", ""),
    ("WAEL ALI ABD ELHAMED ALI AYAD", "", "male", "7475AD", "Wael.Ayad@ese.gov.ae", "TEACHER", "ISLAMIC", "", "TRUE", "", "Wael#AliAyad@%", ""),
    ("Wadha Mohammed Ali Salem Alketbi", "", "female", "2321AD", "Wadha.Alketbi@ese.gov.ae", "TEACHER", "", "", "", "", "Wadha@MohammedAlketbi#%", ""),
    ("YOUSSEF ADEL YOUSSEF MAHMOUD", "", "male", "36753AD", "Youssef.Mahmoud@ese.gov.ae", "TEACHER", "HEALTH SCIENCE", "", "", "", "Youssef@AdelMahmoud$%", "")
]


initialize_my_database(teachers_data)

# Function to create database tables if not exists
def create_table():
    
    cur.execute('''CREATE TABLE IF NOT EXISTS tblclasses (
                    id SERIAL PRIMARY KEY,
                    ClassName VARCHAR(255) NOT NULL, 
                    ClassNameNumeric INT NOT NULL, 
                    NumberOfStudents INT DEFAULT 0,
                    Section VARCHAR(255) NOT NULL,
                    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')

    
    cur.execute('''CREATE TABLE IF NOT EXISTS tblevents (
                    id SERIAL PRIMARY KEY,
                    event VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    date DATE NOT NULL
                )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS tblattendance (
                    id SERIAL PRIMARY KEY,
                    attendance_date DATE,
                    period INTEGER,
                    class_name VARCHAR(255),
                    student_name VARCHAR(255),
                    student_number VARCHAR(255),
                    attendance VARCHAR(50),
                    specialist_comments TEXT
                )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS tblresults (
                    id SERIAL PRIMARY KEY,
                    result_date DATE,
                    class_name VARCHAR(255),
                    student_name VARCHAR(255),
                    student_number VARCHAR(255),
                    emirates_id VARCHAR(255),
                    subject VARCHAR(255),
                    assessment_type VARCHAR(255),
                    marks VARCHAR(255),
                    behavior_notes TEXT,
                    other_notes TEXT,
                    action VARCHAR(255)
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tbladmins (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
                )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS tblusers (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
                )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS tblcalendar (
                    id SERIAL PRIMARY KEY,
                    class_id INT REFERENCES tblclasses(id),
                    teacher_id INT REFERENCES tblteachers(id),
                    exam_date DATE NOT NULL,
                    exam_type VARCHAR(100),
                    subject VARCHAR(100),
                    UNIQUE (class_id, exam_date) -- Ensures each class can have only one exam per day
                )''')

    conn.commit()

create_table()


# Dummy user credentials (replace with actual authentication logic)
ADMIN_USERNAME = 'ADMIN'
ADMIN_PASSWORD = 'Admin@2024$'
TEACHER_USERNAME = 'teacher'
TEACHER_PASSWORD = 'teacher'

@app.route('/')
def index():
    if session.get('student_parent_login'):
        # Call JavaScript function to display popup message
        return render_template('student_reports.html')  # Pass a flag to indicate showing the popup
    elif session.get('admin_login'):
        return render_template('index.html')  # Render admin index page if admin is logged in
    elif session.get('teacher_login'):
        return render_template('teacher_index.html')  # Render teacher index page if teacher is logged in
    else:
        return redirect(url_for('admin_login'))  # Redirect to admin login if no user is logged in

# Function to fetch teachers and classes from the database
@app.route('/get-teachers-and-classes', methods=['GET'])
def get_teachers_and_classes():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch teachers
    cur.execute("SELECT id, employee_name FROM tblteachers")
    teachers = cur.fetchall()
    
    # Fetch classes
    cur.execute("SELECT id, ClassName FROM tblclasses")
    classes = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    # Return the data in JSON format
    return jsonify({
        'teachers': [{'id': t[0], 'employee_name': t[1]} for t in teachers],
        'classes': [{'id': c[0], 'ClassName': c[1]} for c in classes]
    })


@app.route('/booking-exam', methods=['GET', 'POST'])
def booking_exam():
    # Handle GET request
    if request.method == 'GET':
        # You may still want to handle fetching exams based on provided criteria here
        # Get query parameters as before
        class_id = request.args.get('class_id')
        teacher_id = request.args.get('teacher_id')
        exam_date = request.args.get('exam_date')
        
        # Connect to the database and fetch exams as before
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "SELECT * FROM tblcalendar WHERE 1=1"
        params = []
        
        if class_id:
            query += " AND class_id = %s"
            params.append(class_id)
        if teacher_id:
            query += " AND teacher_id = %s"
            params.append(teacher_id)
        if exam_date:
            query += " AND exam_date = %s"
            params.append(exam_date)
        
        cur.execute(query, params)
        exams = cur.fetchall()
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        # Process the exam data to pass to the template
        exam_list = []
        for exam in exams:
            exam_data = {
                'id': exam[0],
                'class_id': exam[1],
                'teacher_id': exam[2],
                'exam_date': exam[3],
                'exam_type': exam[4],
                'subject': exam[5]
            }
            exam_list.append(exam_data)
        
        # Return the list of exams to the template (if any)
        return render_template('booking_exam.html', exams=exam_list)
    # Handle GET request
    elif request.method == 'GET':
        # Retrieve query parameters (you can customize this based on your needs)
        class_id = request.args.get('class_id')
        teacher_id = request.args.get('teacher_id')
        exam_date = request.args.get('exam_date')
        
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query to fetch exams based on provided criteria
        query = "SELECT * FROM tblcalendar WHERE 1=1"
        params = []
        
        if class_id:
            query += " AND class_id = %s"
            params.append(class_id)
        if teacher_id:
            query += " AND teacher_id = %s"
            params.append(teacher_id)
        if exam_date:
            query += " AND exam_date = %s"
            params.append(exam_date)
        
        cur.execute(query, params)
        exams = cur.fetchall()
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        # Process the exam data and return it as JSON
        exam_list = []
        for exam in exams:
            exam_data = {
                'id': exam[0],
                'class_id': exam[1],
                'teacher_id': exam[2],
                'exam_date': exam[3],
                'exam_type': exam[4],
                'subject': exam[5]
            }
            exam_list.append(exam_data)
        
        # Return the list of exams as JSON
        return jsonify({'exams': exam_list})
    
    # Handle POST request
    if request.method == 'POST':
        # Get JSON data from the request
        data = request.get_json()
        
        # Ensure data is valid and contains necessary keys
        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        teacher_id = data.get('teacher_id')
        class_id = data.get('class_id')
        exam_date = data.get('exam_date')
        exam_type = data.get('exam_type')
        subject = data.get('subject')
        
        # Validate input data
        if not all([teacher_id, class_id, exam_date, exam_type, subject]):
            return jsonify({'error': 'Missing required data'}), 400
        
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO tblcalendar (teacher_id, class_id, exam_date, exam_type, subject)
                VALUES (%s, %s, %s, %s, %s)
            """, (teacher_id, class_id, exam_date, exam_type, subject))
            
            # Commit the transaction
            conn.commit()
            
            # Return success message
            return jsonify({'message': 'Exam day booked successfully'}), 200
        except Exception as e:
            # Rollback the transaction in case of an error
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            # Close the cursor and connection
            cur.close()
            conn.close()
@app.route('/get-exam', methods=['GET'])
def get_exam():
    # Retrieve query parameters from the request
    class_id = request.args.get('class_id')
    teacher_id = request.args.get('teacher_id')
    exam_date = request.args.get('exam_date')
    
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Query to fetch exam data based on provided criteria
    query = "SELECT * FROM tblcalendar WHERE 1=1"
    params = []
    
    if class_id:
        query += " AND class_id = %s"
        params.append(class_id)
    if teacher_id:
        query += " AND teacher_id = %s"
        params.append(teacher_id)
    if exam_date:
        query += " AND exam_date = %s"
        params.append(exam_date)
    
    cur.execute(query, params)
    exams = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    # Process the exam data and return it as JSON
    exam_list = []
    for exam in exams:
        exam_data = {
            'id': exam[0],
            'class_id': exam[1],
            'teacher_id': exam[2],
            'exam_date': exam[3],
            'exam_type': exam[4],
            'subject': exam[5]
        }
        exam_list.append(exam_data)
    
    # Return the list of exams as JSON
    return jsonify({
        'exams': exam_list
    })





def get_rotational_list(teachers):
    """Returns a rotational list of teachers for cyclic usage."""
    if teachers:
        return teachers * ((2 * len(teachers) // len(teachers)) + 1)
    else:
        return []

def create_weekday_dates(start_date, end_date):
    """Create a list of dates from start_date to end_date, excluding weekends."""
    weekday_dates = []
    current_date = start_date
    while current_date <= end_date:
        # If the current date is not Saturday (5) or Sunday (6)
        if current_date.weekday() < 5:
            weekday_dates.append(current_date)
        current_date += timedelta(days=1)
    return weekday_dates

@app.route('/morning_duty_scheduling')
def morning_duty_scheduling():
    try:
        # Assuming `cur` is a cursor from a database connection
        cur = conn.cursor()

        # Fetch male and female teachers
        cur.execute("SELECT employee_name FROM tblteachers WHERE mission = 'TEACHER' AND gender = 'male'")
        male_teachers = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT employee_name FROM tblteachers WHERE mission = 'TEACHER' AND gender = 'female'")
        female_teachers = [row[0] for row in cur.fetchall()]

        # Calculate current and next month date ranges
        today = datetime.today()
        start_of_current_month = today.replace(day=1)
        next_month_start_date = (start_of_current_month + timedelta(days=32)).replace(day=1)

        end_of_current_month = next_month_start_date - timedelta(days=1)
        start_of_next_month = next_month_start_date
        end_of_next_month = (start_of_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Create lists for dates in current and next month, excluding weekends
        current_month_dates = create_weekday_dates(start_of_current_month, end_of_current_month)
        next_month_dates = create_weekday_dates(start_of_next_month, end_of_next_month)

        # Initialize duty schedule dictionaries
        duty_schedule_current = defaultdict(dict)
        duty_schedule_next = defaultdict(dict)

        # Initialize rotational lists for male and female teachers
        male_teachers_rotational = get_rotational_list(male_teachers)
        female_teachers_rotational = get_rotational_list(female_teachers)

        # Initialize indices for rotational selection
        male_index = 0
        female_index = 0

        # Function to assign duty to a specific date
        def assign_duty(date, duty_schedule, male_idx, female_idx):
            """Assigns duties for a given date."""
            date_key = date.strftime("%A, %B %d")

            # Assign students' entrance gate and playground duties
            students_gate_playground = []
            for _ in range(2):
                students_gate_playground.append(male_teachers_rotational[male_idx])
                male_idx = (male_idx + 1) % len(male_teachers_rotational)
            duty_schedule['students_entrance_gate_and_playground'][date_key] = ', '.join(students_gate_playground)

            # Assign grade 11/12 entrance gate duty
            grade_11_12_gate = male_teachers_rotational[male_idx]
            male_idx = (male_idx + 1) % len(male_teachers_rotational)
            duty_schedule['grade_11_12_entrance_gate'][date_key] = grade_11_12_gate

            # Assign grade 5 entrance duty
            grade_5_entrance = female_teachers_rotational[female_idx]
            female_idx = (female_idx + 1) % len(female_teachers_rotational)
            duty_schedule['grade_5_entrance'][date_key] = grade_5_entrance

            # Assign main gate duty
            main_gate = male_teachers_rotational[male_idx]
            male_idx = (male_idx + 1) % len(male_teachers_rotational)
            duty_schedule['main_gate'][date_key] = main_gate

            return male_idx, female_idx

        # Assign duties for each date in the current month
        for date in current_month_dates:
            male_index, female_index = assign_duty(date, duty_schedule_current, male_index, female_index)

        # Assign duties for each date in the next month
        for date in next_month_dates:
            male_index, female_index = assign_duty(date, duty_schedule_next, male_index, female_index)

        # Render the template with the duty schedules for the current and next months
        return render_template(
            'morning_duty_scheduling.html',
            duty_schedule_current=duty_schedule_current,
            duty_schedule_next=duty_schedule_next,
            current_month_dates=current_month_dates,
            next_month_dates=next_month_dates
        )

    except Exception as e:
        logging.error(f"An internal server error occurred: {e}")
        return "An internal server error occurred.", 500

@app.route('/add_teachers', methods=['GET', 'POST'])
def add_teachers():
    if request.method == 'GET':
        # Render the form to add teachers
        return render_template('add_teachers.html')
    elif request.method == 'POST':
        try:
            # Extract form data
            employee_name = request.form['employee_name']
            date_of_birth = request.form['date_of_birth']
            gender = request.form['gender']
            job_id = request.form['job_id']
            email = request.form['email']
            mission = request.form.get('mission', '')
            subject = request.form.get('subject', '')
            phone_number = request.form['phone_number']
            coordinator = request.form.get('coordinator', '') == 'on'
            teacher_classes = request.form.get('teacher_classes', '')
            password = request.form['password']
            


            conn = psycopg2.connect(
                dbname='adel_mazouzi_qfv4',
    		user='adel_mazouzi_qfv4_user',
    		password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
    		host='dpg-cpakbfn109ks73apokt0-a',
    		port='5432'
            )
            cur = conn.cursor()

            # Insert new teacher into the database
            cur.execute("""
                INSERT INTO tblteachers (
                    employee_name,
                    date_of_birth,
                    gender,
                    job_id,
                    email,
                    mission,
                    subject,
                    phone_number,
                    coordinator,
                    teacher_classes,
                    password
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                employee_name,
                date_of_birth,
                gender,
                job_id,
                email,
                mission,
                subject,
                phone_number,
                coordinator,
                teacher_classes,
                password
            ))

            # Commit the changes
            conn.commit()

            # Close the cursor and connection
            cur.close()
            conn.close()

            # Return JSON response with success status
            return jsonify({'success': True, 'message': 'Teacher added successfully.'})

        except psycopg2.Error as e:
            # Log and handle database errors
            print("Database error occurred:", e)
            return jsonify({'success': False, 'error': 'Database error: ' + str(e)})

        except Exception as e:
            # Log and handle other types of errors
            print("An error occurred:", e)
            return jsonify({'success': False, 'error': 'An error occurred: ' + str(e)})


# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname='adel_mazouzi_qfv4',
    	user='adel_mazouzi_qfv4_user',
    	password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
    	host='dpg-cpakbfn109ks73apokt0-a',
    	port='5432'
    )
    cur = conn.cursor()

@app.route('/manage_teachers', methods=['GET', 'POST'])
def manage_teachers():
    response = None
    print('Entering manage_teachers function')  # Check if the function is triggered
    conn = get_db_connection()  # Assume this function returns a connection to the database
    cur = conn.cursor()
    
    try:
        if request.method == 'POST':
            action = request.form.get('action')
            teacher_id = request.form.get('teacher_id')
            print('POST request received')  # Check if POST request is being processed
            print('Action:', action)  # Log the action
            print('Teacher ID:', teacher_id)  # Log the teacher ID
            
            if action == 'update' and teacher_id:
                form_data = {
                    'employee_name': request.form.get('employee_name'),
                    'date_of_birth': request.form.get('date_of_birth'),
                    'gender': request.form.get('gender'),
                    'job_id': request.form.get('job_id'),
                    'email': request.form.get('email'),
                    'mission': request.form.get('mission'),
                    'subject': request.form.get('subject'),
                    'phone_number': request.form.get('phone_number'),
                    'coordinator': request.form.get('coordinator') == 'on',
                    'teacher_classes': request.form.get('teacher_classes'),
                    'password': request.form.get('password'),
                    'group_number': request.form.get('group_number')
                }
                
                try:
                    print('Updating teacher data')  # Log before executing the update query
                    cur.execute('''
                        UPDATE tblteachers
                        SET employee_name = %s,
                            date_of_birth = %s,
                            gender = %s,
                            job_id = %s,
                            email = %s,
                            mission = %s,
                            subject = %s,
                            phone_number = %s,
                            coordinator = %s,
                            teacher_classes = %s,
                            password = %s,
                            group_number = %s
                        WHERE id = %s
                    ''', (
                        form_data['employee_name'], form_data['date_of_birth'], form_data['gender'],
                        form_data['job_id'], form_data['email'], form_data['mission'],
                        form_data['subject'], form_data['phone_number'], form_data['coordinator'],
                        form_data['teacher_classes'], form_data['password'], form_data['group_number'],
                        teacher_id
                    ))
                    
                    conn.commit()
                    print('Teacher data updated successfully')  # Log after successful commit
                    
                    response = jsonify({'status': 'success', 'message': 'Teacher updated successfully.'})
                    
                except Exception as e:
                    print('Error while updating teacher:', e)
                    response = jsonify({'status': 'error', 'message': f'Error while updating teacher: {e}'})
                    response.status_code = 400
                
            else:
                response = jsonify({'status': 'error', 'message': 'Action or teacher ID is missing.'})
                response.status_code = 400
        
        elif request.method == 'GET':
            cur.execute('SELECT * FROM tblteachers')
            teachers = cur.fetchall()
            return render_template('manage_teachers.html', teachers=teachers)
    
    except Exception as e:
        print('An unexpected error occurred:', e)
        response = jsonify({'status': 'error', 'message': f'An unexpected error occurred: {e}'})
        response.status_code = 500
    
    finally:
        cur.close()
        conn.close()
    
    if response is None:
        response = jsonify({'status': 'error', 'message': 'No response set.'})
    
    return response


@app.route('/get_attendance_data', methods=['GET'])
def get_attendance_data():
    try:
        # Get the current date
        current_date = datetime.today().date()
        
        # Database connection
        cur = conn.cursor()
        
        # Fetch class names from tblclasses
        cur.execute('SELECT ClassName FROM tblclasses')
        all_classes = [row[0] for row in cur.fetchall()]
        
        # Fetch attendance data for the current day and all periods
        cur.execute('''
            SELECT
                attendance_date,
                period,
                class_name,
                student_name,
                student_number,
                attendance
            FROM tblattendance
            WHERE attendance_date = %s
        ''', (current_date,))

        rows = cur.fetchall()

        # Process rows into a structured format (dictionary)
        attendance_data = {}
        classes_with_attendance = {f'Period {i}': set() for i in range(1, 9)}
        for row in rows:
            attendance_date, period, class_name, student_name, student_number, attendance = row
            period_key = f'Period {period}'

            # Track classes with attendance data
            classes_with_attendance[period_key].add(class_name)

            if period_key not in attendance_data:
                attendance_data[period_key] = {
                    'classes_with_attendance': set(),
                    'records': []
                }

            attendance_data[period_key]['records'].append({
                'class_name': class_name,
                'student_name': student_name,
                'student_number': student_number,
                'attendance': attendance
            })

            attendance_data[period_key]['classes_with_attendance'].add(class_name)

        # Calculate attendance input percentage and classes without attendance
        attendance_summary = {}
        for period_key in attendance_data:
            classes_with_attendance_set = attendance_data[period_key]['classes_with_attendance']

            # Calculate classes without attendance
            classes_without_attendance = set(all_classes) - classes_with_attendance_set

            # Calculate attendance input percentage
            attendance_input_percentage = (len(classes_with_attendance_set) / len(all_classes)) * 100

            attendance_summary[period_key] = {
                'attendance_input_percentage': attendance_input_percentage,
                'classes_without_attendance': list(classes_without_attendance)
            }

        # Close the cursor
        cur.close()

        # Return the attendance summary as a JSON response
        return jsonify({'attendanceSummary': attendance_summary})

    except Exception as e:
        # Handle any exceptions that occur
        print("Error fetching attendance data:", e)
        return jsonify({'error': 'Error fetching attendance data'}), 500


# Route to render the HTML template
@app.route('/student_report_card')
def student_report_card():
    return render_template('student_report_card.html')
@app.route('/fetch_report_card', methods=['POST'])
def fetch_report_card():
    try:
        # Define the start and end dates for the selected term based on the academic year
        def start_date_of_term(academic_year, term):
            academic_year_str = str(academic_year)  # Convert academic year to string
            if term == 'Term 1':
                return f"{academic_year_str}-08-01"  # Term 1 starts on August 1st of the previous year
            elif term == 'Term 2':
                next_academic_year_str = str(academic_year + 1)  # Next academic year
                return f"{next_academic_year_str}-01-01"  # Term 2 starts on January 1st of the next academic year
            elif term == 'Term 3':
                next_academic_year_str = str(academic_year + 1)  # Next academic year
                return f"{next_academic_year_str}-04-01"  # Term 3 starts on April 1st of the next academic year

        def end_date_of_term(academic_year, term):
            academic_year_str = str(academic_year)  # Convert academic year to string
            if term == 'Term 1':
                return f"{academic_year_str}-12-31"  # Term 1 ends on December 31st of the same academic year
            elif term == 'Term 2':
                next_academic_year_str = str(academic_year + 1)  # Next academic year
                return f"{next_academic_year_str}-03-31"  # Term 2 ends on March 31st of the next academic year
            elif term == 'Term 3':
                next_academic_year_str = str(academic_year + 1)  # Next academic year
                return f"{next_academic_year_str}-07-31"  # Term 3 ends on July 31st of the next academic year

        # Extract form data from the request
        data = request.json
        print("Received data:", data)  # Print the received data for debugging
        academic_year = data.get('academicYear')
        term = data.get('term')
        assessment_type = data.get('assessmentType')
        selected_class = data.get('class_name')

        # Check if all required parameters are provided
        if not all([academic_year, term, assessment_type, selected_class]):
            print("Missing parameters:", academic_year, term, assessment_type, selected_class)  # Print missing parameters for debugging
            return jsonify(error='Missing parameters'), 400

        # Split the academic year into start and end parts
        academic_year_start, academic_year_end = map(int, academic_year.split('-'))

        # Define the start and end dates for the selected term based on the academic year
        term_start_date = start_date_of_term(academic_year_start, term)
        term_end_date = end_date_of_term(academic_year_start, term)

        print("Term start date:", term_start_date)  # Print term start date for debugging
        print("Term end date:", term_end_date)  # Print term end date for debugging

        # Query the database to fetch report card data based on the selected criteria
        if selected_class == 'All Classes':
            cur.execute('''SELECT student_name, student_number, class_name, subject, assessment_type, marks, behavior_notes 
                        FROM tblresults 
                        WHERE result_date BETWEEN %s AND %s 
                        AND assessment_type = %s''',
                        (term_start_date, term_end_date, assessment_type))
        else:
            cur.execute('''SELECT student_name, student_number, class_name, subject, assessment_type, marks, behavior_notes 
                        FROM tblresults 
                        WHERE result_date BETWEEN %s AND %s 
                        AND assessment_type = %s 
                        AND class_name = %s''',
                        (term_start_date, term_end_date, assessment_type, selected_class))
        
        # Print the SQL query being executed
        print("SQL Query:", cur.query.decode('utf-8'))

        report_card_data = cur.fetchall()

        # Process the retrieved data and format it appropriately
        processed_report_card_data = []
        for row in report_card_data:
            processed_report_card_data.append({
                'student_name': row[0],
                'student_number': row[1],
                'class_name': row[2],
                'subject': row[3],
                'assessment_type': row[4],
                'marks': row[5],
                'behavior_notes': row[6]
            })

        # Print the processed report card data for debugging
        print("Processed report card data:", processed_report_card_data)

        # Return the processed report card data as JSON response
        return jsonify(report_card_data=processed_report_card_data)

    except Exception as e:
        print("Error:", e)  # Print any exceptions for debugging
        return jsonify(error=str(e)), 500
def get_academic_years():
    cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM result_date), EXTRACT(MONTH FROM result_date) FROM tblresults")
    academic_years = []
    for row in cur.fetchall():
        year = int(row[0])
        month = int(row[1])
        # Adjust the academic year start based on the month
        academic_year_start = year if month >= 8 else year - 1
        academic_years.append((academic_year_start, academic_year_start + 1))
    academic_years = list(set(academic_years))  # Remove duplicates
    academic_years.sort()  # Sort the list of academic years
    return academic_years


@app.route('/fetch_academic_years', methods=['GET'])
def fetch_academic_years():
    academic_years = get_academic_years()
    return jsonify(academic_years)


@app.route('/fetch_terms', methods=['POST'])
def fetch_terms():
    try:
        academic_year = request.json.get('academicYear')
        if academic_year is None:
            return jsonify(error='Academic year not provided'), 400

        # Check if academic year is received correctly
        print("Received academic year:", academic_year)

        # Split the academic year and get the first and last years
        academic_year_start, academic_year_end = map(int, academic_year.split('-'))
        print("Academic year start:", academic_year_start)
        print("Academic year end:", academic_year_end)

        terms = get_terms(academic_year_start)  # Get terms based on the academic year start
        return jsonify(terms=terms)
    except Exception as e:
        print("Error:", e)
        return jsonify(error='An error occurred while fetching terms'), 500







def get_terms(academic_year):
    # Define the start and end dates for each term based on the academic year
    term1_start = datetime(academic_year, 8, 1)  # Term 1 starts in August of the previous year
    term1_end = datetime(academic_year, 12, 31)  # Term 1 ends in December of the previous year
    term2_start = datetime(academic_year + 1, 1, 1)  # Term 2 starts in January
    term2_end = datetime(academic_year + 1, 3, 31)  # Term 2 ends in March
    term3_start = datetime(academic_year + 1, 4, 1)  # Term 3 starts in April
    term3_end = datetime(academic_year + 1, 7, 31)  # Term 3 ends in July

    # Fetch the result dates from the tblresults table
    cur.execute("SELECT result_date FROM tblresults")

    # Initialize lists to store the result dates for each term
    term1_dates = []
    term2_dates = []
    term3_dates = []

    # Classify the result dates into each term based on the term ranges
    for row in cur.fetchall():
        result_date = datetime.combine(row[0], datetime.min.time())  # Convert date to datetime
        if term1_start <= result_date <= term1_end:
            term1_dates.append(result_date)
        elif term2_start <= result_date <= term2_end:
            term2_dates.append(result_date)
        elif term3_start <= result_date <= term3_end:
            term3_dates.append(result_date)

    terms = ['Term 1', 'Term 2', 'Term 3']
    return terms


def get_assessment_types(academic_year, term):
    try:
        # Define the start and end dates for each term
        if term == 'Term 1':
            term_start_date = f"{academic_year}-08-01"  # Term 1 starts on August 1st
            term_end_date = f"{academic_year}-12-31"    # Term 1 ends on December 31st
        elif term == 'Term 2':
            term_start_date = f"{academic_year + 1}-01-01"  # Term 2 starts on January 1st of the next year
            term_end_date = f"{academic_year + 1}-03-31"    # Term 2 ends on March 31st of the next year
        elif term == 'Term 3':
            term_start_date = f"{academic_year + 1}-04-01"  # Term 3 starts on April 1st
            term_end_date = f"{academic_year + 1}-07-31"    # Term 3 ends on July 31st
        
        print("Term start date:", term_start_date)
        print("Term end date:", term_end_date)

        # Query the database to fetch assessment types for the specified term
        cur.execute('''SELECT DISTINCT assessment_type FROM tblresults
                       WHERE result_date BETWEEN %s AND %s''',
                    (term_start_date, term_end_date))
        assessment_types = [row[0] for row in cur.fetchall()]
        print("Assessment types:", assessment_types)
        return assessment_types
    except Exception as e:
        print("Error fetching assessment types:", e)
        return None
@app.route('/fetch_my_assessment_types', methods=['POST'])
def fetch_my_assessment_types_route():
    return fetch_my_assessment_types()
def fetch_my_assessment_types():
    try:
        data = request.json
        print("Received data:", data)  # Add this line to print the received data
        academic_year = data.get('academicYear')
        term = data.get('term')
        
        if academic_year is None or term is None:
            return jsonify(error='Academic year or term not provided'), 400

        # Print or log the received values
        print("Received academic year:", academic_year)
        print("Received term:", term)

        # Split the academic year into start and end parts
        academic_year_start, academic_year_end = map(int, academic_year.split('-'))
        print("Academic year start:", academic_year_start)
        print("Academic year end:", academic_year_end)
        
        # Adjust academic year based on the provided term
        if term == 'Term 1':
            # For Term 1, academic year starts from August of the previous year
            academic_year_start = academic_year_start
            academic_year_end = academic_year_end - 1
        elif term in ['Term 2', 'Term 3']:
            # For Term 2 and Term 3, academic year remains the same
            pass
        else:
            return jsonify(error='Invalid term provided'), 400

        # Call the function to get assessment types
        assessment_types = get_assessment_types(academic_year_start, term)
        
        if assessment_types is None:
            return jsonify(error='Failed to fetch assessment types'), 500
        
        print("Assessment types:", assessment_types)

        return jsonify(assessment_types=assessment_types)
    except Exception as e:
        print("Error:", e)
        return jsonify(error='An error occurred while fetching assessment types'), 500
    


@app.route('/fetch_my_classes', methods=['POST'])
def fetch_my_classes_route():
    return fetch_my_classes()

def fetch_my_classes():
    try:
        # Extract data from the request
        data = request.json
        academic_year = data.get('academicYear')
        term = data.get('term')
        assessment_type = data.get('assessmentType')
        
        if academic_year is None or term is None or assessment_type is None:
            return jsonify(error='Academic year, term, or assessment type not provided'), 400

        # Split the academic year into start and end parts
        academic_year_start, academic_year_end = map(int, academic_year.split('-'))

        # Define the start and end dates for each term based on the academic year
        term1_start = datetime(academic_year_start, 8, 1)  # Term 1 starts in August of the previous year
        term1_end = datetime(academic_year_start, 12, 31)  # Term 1 ends in December of the previous year
        term2_start = datetime(academic_year_start + 1, 1, 1)  # Term 2 starts in January
        term2_end = datetime(academic_year_start + 1, 3, 31)  # Term 2 ends in March
        term3_start = datetime(academic_year_start + 1, 4, 1)  # Term 3 starts in April
        term3_end = datetime(academic_year_start + 1, 7, 31)  # Term 3 ends in July

        # Determine which term the provided term belongs to
        if term == 'Term 1':
            term_start_date, term_end_date = term1_start, term1_end
        elif term == 'Term 2':
            term_start_date, term_end_date = term2_start, term2_end
        elif term == 'Term 3':
            term_start_date, term_end_date = term3_start, term3_end
        else:
            return jsonify(error='Invalid term provided'), 400

        # Query the database to fetch classes for the specified assessment type within the term range
        cur.execute('''SELECT DISTINCT class_name FROM tblresults
                       WHERE EXTRACT(YEAR FROM result_date) BETWEEN %s AND %s
                       AND result_date BETWEEN %s AND %s
                       AND assessment_type = %s''',
                    (academic_year_start, academic_year_end, term_start_date, term_end_date, assessment_type))
        
        classes = [row[0] for row in cur.fetchall()]
        
        # Add an option to select all classes
        classes.append('All Classes')

        print("Classes:", classes)

        return jsonify(classes=classes)
    except Exception as e:
        print("Error:", e)
        return jsonify(error='An error occurred while fetching classes'), 500


# Route to render the HTML template
@app.route('/absentee_report')
def absentee_report():
    return render_template('absentee_report.html')





@app.route('/generate_absentee_report', methods=['POST'])
def generate_absentee_report():
    if request.method == 'POST':
        # Retrieve the start_date and end_date from the form
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Query to fetch absenteeism data from the database
        query = """
            SELECT class_name, student_name, student_number, COUNT(*) AS total_absent
            FROM tblattendance
            WHERE attendance_date BETWEEN %s AND %s
            AND attendance = 'Absent'
            GROUP BY class_name, student_name, student_number
            ORDER BY total_absent DESC
        """

        try:
            # Execute the query with the provided date range
            cur.execute(query, (start_date, end_date))
            absentee_report = cur.fetchall()

            # Convert absentee report data to a list of dictionaries
            absentee_report_data = []
            for record in absentee_report:
                absentee_report_data.append({
                    'class_name': record[0],
                    'student_name': record[1],
                    'student_number': record[2],
                    'total_absent': record[3]
                })

            # Return the absentee report data as JSON
            return jsonify({'absentee_report': absentee_report_data})

        except Exception as e:
            # Log any errors that occur during database query execution
            logging.error(f"Error generating absentee report: {str(e)}")
            return jsonify({'error': 'An error occurred while generating the absentee report'}), 500
    else:
        # If the request method is not POST, return an error response
        return jsonify({'error': 'Invalid request method'}), 405

# Route to render the HTML template
@app.route('/classwise_attendance_report')
def classwise_attendance_report():
    return render_template('classwise_attendance_report.html')


@app.route('/overall_attendance_percentage')
def overall_attendance_percentage():
    try:
        # Get the start date and end date from the request
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Check if both start date and end date are provided
        if start_date is None or end_date is None:
            return jsonify({'error': 'Please provide both start_date and end_date parameters.'}), 400
        
        # Query database to calculate overall attendance percentage for all classes within the date range
        cur.execute("""
            SELECT 
                AVG(CASE WHEN attendance IN ('Present', 'Late', 'Sleep') THEN 1 ELSE 0 END) * 100 AS overall_attendance_percentage
            FROM 
                tblattendance
            WHERE 
                attendance_date BETWEEN %s AND %s
        """, (start_date, end_date))
        
        overall_attendance_data = cur.fetchone()

        if overall_attendance_data:
            overall_attendance_percentage = overall_attendance_data[0]
            return jsonify({'overall_attendance_percentage': overall_attendance_percentage})
        else:
            return jsonify({'error': 'No attendance data available for the selected date range.'}), 404
    except Exception as e:
        logging.error("Error fetching overall attendance percentage: %s", str(e))
        return jsonify({'error': 'An error occurred while fetching overall attendance percentage.'}), 500


# Route to fetch class-wise attendance report data
@app.route('/get_classwise_attendance_report')
def get_classwise_attendance_report():
    try:
        # Query database to fetch class-wise attendance data
        cur.execute("""
            SELECT 
                class_name,
                SUM(CASE WHEN attendance NOT IN ('Absent', 'Excused') THEN 1 ELSE 0 END) AS total_present,
                SUM(CASE WHEN attendance = 'Absent' THEN 1 ELSE 0 END) AS total_absent,
                SUM(CASE WHEN attendance = 'Late' THEN 1 ELSE 0 END) AS total_late,
                SUM(CASE WHEN attendance = 'Sleep' THEN 1 ELSE 0 END) AS total_sleep,
                SUM(CASE WHEN attendance = 'Excused' THEN 1 ELSE 0 END) AS total_permission
            FROM 
                tblattendance
            GROUP BY 
                class_name
        """)
        classwise_attendance_data = cur.fetchall()

        # Prepare data for JSON response
        response_data = {}
        for row in classwise_attendance_data:
            class_name, total_present, total_absent, total_late, total_sleep, total_permission = row
            response_data[class_name] = {
                'total_present': total_present,
                'total_absent': total_absent,
                'total_late': total_late,
                'total_sleep': total_sleep,
                'total_permission': total_permission
            }

        return jsonify(response_data)
    except Exception as e:
        logging.error("Error fetching class-wise attendance data: %s", str(e))
        return jsonify({'error': 'An error occurred while fetching class-wise attendance data.'})


@app.route('/attendance_trends_data')
def attendance_trends_data():
    try:
        # Get the selected class, start date, and end date from the request
        selected_class = request.args.get('selected_class')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Check if all required parameters are provided
        if selected_class is None or start_date is None or end_date is None:
            return jsonify({'error': 'Please provide values for selected_class, start_date, and end_date.'}), 400
        
        # Query database to fetch attendance trends data for the selected class and date range
        cur.execute("""
            SELECT 
                attendance_date,
                AVG(CASE WHEN attendance IN ('Present', 'Late', 'Sleep') THEN 1 ELSE 0 END) * 100 AS attendance_percentage
            FROM 
                tblattendance
            WHERE 
                class_name = %s AND
                attendance_date BETWEEN %s AND %s
            GROUP BY 
                attendance_date
            ORDER BY 
                attendance_date
        """, (selected_class, start_date, end_date))
        
        attendance_trends_data = cur.fetchall()

        # Prepare data for JSON response
        response_data = {}
        for row in attendance_trends_data:
            attendance_date, attendance_percentage = row
            response_data[attendance_date.strftime('%Y-%m-%d')] = attendance_percentage

        return jsonify(response_data)
    except Exception as e:
        logging.error("Error fetching attendance trends data: %s", str(e))
        return jsonify({'error': 'An error occurred while fetching attendance trends data.'}), 500


































# Route to render the dashboard page
@app.route('/monthly_attendance_report')
def monthly_attendance_report():
    return render_template('monthly_attendance_report.html')

@app.route('/get_monthly_attendance_report', methods=['POST'])
def get_monthly_attendance_report():
    try:
        selected_month = request.form.get('selected_month')
        selected_class = request.form.get('selected_class')

        # Logging selected month and class for debugging
        logging.debug("Selected Month: %s", selected_month)
        logging.debug("Selected Class: %s", selected_class)

        # Validate input
        if not selected_month or not selected_class:
            raise ValueError("Selected month and class are required.")

        # Format the selected month to 'YYYY-MM-DD'
        formatted_month = f"{selected_month}-01"

        # Your SQL query here...
        cur.execute("""
            SELECT 
                student_name, 
                student_number,
                SUM(CASE WHEN attendance NOT IN ('Absent', 'Excused') THEN 1 ELSE 0 END) AS total_present,
                SUM(CASE WHEN attendance = 'Absent' THEN 1 ELSE 0 END) AS total_absent,
                SUM(CASE WHEN attendance = 'Late' THEN 1 ELSE 0 END) AS total_late,
                SUM(CASE WHEN attendance = 'Sleep' THEN 1 ELSE 0 END) AS total_sleep,
                SUM(CASE WHEN attendance = 'Excused' THEN 1 ELSE 0 END) AS total_permission
            FROM 
                tblattendance 
            WHERE 
                EXTRACT(MONTH FROM attendance_date) = EXTRACT(MONTH FROM %s::DATE) AND 
                EXTRACT(YEAR FROM attendance_date) = EXTRACT(YEAR FROM %s::DATE) AND
                class_name = %s
            GROUP BY 
                student_name, student_number
        """, (formatted_month, formatted_month, selected_class))

        # Fetch attendance data for the selected month and class
        data = cur.fetchall()

        # Prepare the data for the monthly report
        monthly_report_data = []
        for row in data:
            student_name, student_number, total_present, total_absent, total_late, total_sleep, total_permission = row
            monthly_report_data.append({
                'student_name': student_name,
                'student_number': student_number,
                'total_present': total_present,
                'total_absent': total_absent,
                'total_late': total_late,
                'total_sleep': total_sleep,
                'total_permission': total_permission
            })

        # Construct the response object
        response = {
            'monthly_report_data': monthly_report_data
        }

        return jsonify(response)
    
    except Exception as e:
        # Log the error for debugging
        logging.error("Error occurred: %s", str(e))
        return jsonify({'error': str(e)}), 500










# Route to render the dashboard page
@app.route('/daily_attendance_report')
def daily_attendance_report():
    return render_template('daily_attendance_report.html')

@app.route('/get_attendance_report', methods=['POST'])
def get_attendance_report():
    selected_date = request.form.get('selected_date')
    selected_class = request.form.get('selected_class')

    # Print all data in tblattendance based on the selected date and class
    cur.execute("""
        SELECT * 
        FROM tblattendance 
        WHERE attendance_date = %s AND class_name = %s
    """, (selected_date, selected_class))
    all_attendance_data = cur.fetchall()

    # Debugging SQL Query: Print the SQL query string with substituted parameters
    sql_query = """
        SELECT 
            student_name, 
            student_number,
            SUM(CASE WHEN attendance NOT IN ('Absent', 'Excused') THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN attendance = 'Absent' THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN attendance = 'Late' THEN 1 ELSE 0 END) AS late,
            SUM(CASE WHEN attendance = 'Sleep' THEN 1 ELSE 0 END) AS sleep,
            SUM(CASE WHEN attendance = 'Excused' THEN 1 ELSE 0 END) AS permission
        FROM 
            tblattendance 
        WHERE 
            attendance_date = %s AND class_name = %s
        GROUP BY 
            student_name, student_number
    """
    print("SQL Query:", cur.mogrify(sql_query, (selected_date, selected_class)))

    # Fetch attendance data for the selected date and class
    cur.execute(sql_query, (selected_date, selected_class))
    data = cur.fetchall()

    # Prepare the data for the report
    report_data = []
    for row in data:
        student_name, student_number, present, absent, late, sleep, permission = row
        report_data.append({
            'student_name': student_name,
            'student_number': student_number,
            'present': present,
            'absent': absent,
            'late': late,
            'sleep': sleep,
            'permission': permission
        })

    # Simulate calculation of attendance status
    # You can customize this part based on your actual logic
    attendance_status = {
        'report_data': report_data
    }

    # Construct the response object
    response = {
        'report_data': report_data,
        'attendance_status': attendance_status
    }

    return jsonify(response)





















@app.route('/classwise_result_summary')
def classwise_result_summary():
    cur.execute("SELECT class_name, AVG(marks) AS average_marks FROM tblresults GROUP BY class_name")
    data = cur.fetchall()
    return jsonify(data)



@app.route('/subjectwise_performance_report')
def subjectwise_performance_report():
    cur.execute("SELECT subject, AVG(marks) AS average_marks FROM tblresults GROUP BY subject")
    data = cur.fetchall()
    return jsonify(data)



@app.route('/comparative_analysis_report')
def comparative_analysis_report():
    cur.execute("SELECT class_name, AVG(marks) AS average_marks FROM tblresults GROUP BY class_name")
    class_data = cur.fetchall()
    cur.execute("SELECT subject, AVG(marks) AS average_marks FROM tblresults GROUP BY subject")
    subject_data = cur.fetchall()
    return jsonify({"class_data": class_data, "subject_data": subject_data})



@app.route('/progress_report')
def progress_report():
    cur.execute("SELECT * FROM tblresults WHERE student_name = 'StudentName' ORDER BY result_date DESC LIMIT 5")
    data = cur.fetchall()
    return jsonify(data)



@app.route('/behavioral_analysis_report')
def behavioral_analysis_report():
    cur.execute("SELECT * FROM tblresults WHERE behavior_notes IS NOT NULL")
    data = cur.fetchall()
    return jsonify(data)



@app.route('/actionable_insights_report')
def actionable_insights_report():
    cur.execute("SELECT * FROM tblresults WHERE action IS NOT NULL")
    data = cur.fetchall()
    return jsonify(data)

@app.route('/event_calendar')
def event_calendar():
    cur.execute("SELECT * FROM tblevents")
    data = cur.fetchall()
    return jsonify(data)

@app.route('/student_directory')
def student_directory():
    cur.execute("SELECT * FROM tblstudents")
    data = cur.fetchall()
    return jsonify(data)

@app.route('/class_roster')
def class_roster():
    cur.execute("SELECT * FROM tblclasses")
    data = cur.fetchall()
    return jsonify(data)

@app.route('/teacher_assignment_report')
def teacher_assignment_report():
    cur.execute("SELECT * FROM tblclasses")
    data = cur.fetchall()
    return jsonify(data)

@app.route('/administrative_reports')
def administrative_reports():
    cur.execute("SELECT * FROM tbladmins")
    data = cur.fetchall()
    return jsonify(data)




























































































































































































































def fetch_events():
    cur.execute("SELECT * FROM tblevents")
    events = cur.fetchall()
    
    return events

# Route to fetch events from the database and return as JSON
@app.route('/get_exist_events', methods=['GET'])
def get_exist_events():
    # Fetch events from the database using the fetch_events function
    events = fetch_events()
    print("Fetched events:", events)  # Add this line to print fetched events
    # Convert events to a JSON format
    events_json = [{'event': event[1], 'description': event[2], 'date': str(event[3])} for event in events]
    # Return events as JSON response
    return jsonify(events_json)
# Route to fetch events from the database and return as JSON
@app.route('/get_exist_events', methods=['GET'])
def get_events():
    # Fetch events from the database using the fetch_events function
    events = fetch_events()
    # Convert events to a JSON format
    events_json = [{'event': event[1], 'description': event[2], 'date': str(event[3])} for event in events]
    # Return events as JSON response
    return jsonify(events_json)

# Route to render the events page and handle adding new events
@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        # If the request method is POST, it means a new event is being added
        # Retrieve event data from the form
        event = request.form['event']
        description = request.form['description']
        date = request.form['date']
        # Insert event into the database
        cur.execute("INSERT INTO tblevents (event, description, date) VALUES (%s, %s, %s)", (event, description, date))
        conn.commit()
        # After adding the event, fetch all events from the database again
        existing_events = fetch_events()
        # Render the events.html template with existing events
        return render_template('events.html', events=existing_events)
    else:
        # Fetch existing events from the database
        existing_events = fetch_events()
        print("Existing events:", existing_events)
        # Render the events.html template with existing events
        return render_template('events.html', events=existing_events)

@app.route('/get_attendance_details/<emirates_id>', methods=['GET'])
def get_attendance_details(emirates_id):
    try:
        print('Emirates ID received in backend:', emirates_id)  # Debugging statement

        conn = psycopg2.connect(
            dbname='adel_mazouzi_qfv4',
    	    user='adel_mazouzi_qfv4_user',
	    password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
	    host='dpg-cpakbfn109ks73apokt0-a',
	    port='5432'
        )
        cur = conn.cursor()

        # Query to fetch student name based on the received Emirates ID
        cur.execute("SELECT full_name FROM tblstudents WHERE emirates_id = %s", (emirates_id,))
        student = cur.fetchone()

        if student:
            student_name = student[0]  # Extract the student name from the result
            print('Student name:', student_name)  # Debugging statement

            # Get the academic year to determine term start and end dates
            academic_year_start, academic_year_end = get_academic_year()
            print('Academic year start:', academic_year_start)  # Debugging statement
            print('Academic year end:', academic_year_end)  # Debugging statement

            # Determine the current date
            current_date = datetime.now().date()
            print('Current date:', current_date)  # Debugging statement

            # Determine the term based on the current date and attendance dates
            term = None
            if current_date.month >= 8 and current_date.month <= 12:
                term = 'term 1'
            elif current_date.month >= 1 and current_date.month <= 3:
                term = 'term 2'
            elif current_date.month >= 4 and current_date.month <= 7:
                term = 'term 3'

            print('Determined term:', term)  # Debugging statement

            if term:
                # Query to retrieve attendance records for the determined term and student name
                cur.execute("""
                    SELECT attendance_date, period, attendance 
                    FROM tblattendance 
                    WHERE student_name = %s
                """, (student_name,))
                attendance_records = cur.fetchall()
                print('Attendance records:', attendance_records)  # Debugging statement

                # Initialize variables to count attendance details
                total_days_attended = 0
                total_days_absent = 0

                # Initialize a dictionary to store attendance for each day
                attendance_by_day = defaultdict(list)

                # Loop through attendance records to count attended and absent days
                for record in attendance_records:
                    attendance_date = record[0]
                    period = record[1]
                    attendance = record[2]
                    # Store attendance for each day and period
                    attendance_by_day[attendance_date].append((period, attendance))

                # Initialize variables to count attendance details
                total_days_attended = 0
                total_days_absent = 0

                # Loop through attendance by day to calculate total days attended and absent
                for day, attendance_list in attendance_by_day.items():
                    # Initialize variables to track attendance for the day
                    periods_absent = sum(1 for period, att in attendance_list if att == 'Absent')
                    periods_present = any(att in ['Present', 'Late', 'Sleep', 'Excused'] for period, att in attendance_list)

                    # Determine if the day should be counted as attended or absent
                    if periods_absent >= 3:
                        total_days_absent += 1
                    elif periods_present:
                        total_days_attended += 1
                    elif periods_absent in (1, 2):
                        total_days_absent += 1
                # Count the unique dates for attendance calculation
                total_days_in_term = len(attendance_by_day)
                print('Total days attended:', total_days_attended)  # Debugging statement
                print('Total days absent:', total_days_absent)  # Debugging statement
                print('Total days in term:', total_days_in_term)  # Debugging statement

                # Ensure total_days_in_term is at least 1 to avoid division by zero error
                total_days_in_term = max(total_days_in_term, 1)

                # Calculate attendance percentage, rounded to one decimal place
                attendance_percentage = round(min((total_days_attended / total_days_in_term) * 100, 100), 1)
                print('Attendance percentage:', attendance_percentage)  # Debugging statement

                # Update the JSON response to include the term
                return jsonify({
                    'term': term,
                    'total_days_attended': total_days_attended,
                    'total_days_absent': total_days_absent,
                    'attendance_percentage': round(attendance_percentage, 1)  # Round to one decimal place
                })
            else:
                return jsonify({'error': 'Unable to determine term'}), 500
        else:
            return jsonify({'error': 'Student not found for the provided Emirates ID'}), 404

    except Exception as e:
        print('Error:', e)  # Add this line to print the specific error
        return jsonify({'error': str(e)}), 500

    finally:
        # Close cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

        
@app.route('/get_logged_in_student_id', methods=['GET'])
def get_logged_in_student_id():
    if 'student_parent_login' in session:
        # If the student/parent is logged in, return their Emirates ID
        return jsonify({'emirates_id': session['student_parent_login']})
    else:
        # If not logged in, return an error message
        return jsonify({'error': 'Not logged in'}), 401

@app.route('/get_results_data/<emirates_id>', methods=['GET'])
def get_results_data(emirates_id):
    try: 
        conn = psycopg2.connect(
            dbname='adel_mazouzi_qfv4',
	    user='adel_mazouzi_qfv4_user',
	    password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
	    host='dpg-cpakbfn109ks73apokt0-a',
	    port='5432'
        )
        cur = conn.cursor()

        # Check if the Emirates ID exists in the database
        cur.execute("SELECT * FROM tblstudents WHERE emirates_id = %s", (emirates_id,))
        student = cur.fetchone()

        if student:
            # Fetch results for the logged-in student using their emirates_id
            cur.execute("""
                SELECT subject, assessment_type, marks, result_date, behavior_notes, other_notes 
                FROM tblresults 
                WHERE emirates_id = %s AND action = 'explore'
            """, (emirates_id,))
            results = cur.fetchall()

            if results:
                print('Results data fetched from database:', results)  # Debugging statement
                # Return the fetched results as JSON
                return jsonify(results)
            else:
                return jsonify({'message': 'Results not available for exploration'}), 404
        else:
            return jsonify({'error': 'Invalid Emirates ID'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cur.close()
        conn.close()


@app.route('/student_parent_login', methods=['POST'])
def student_parent_login():
    if request.method == 'POST':
        emirates_id = request.form['emirates-id']

        # Check if the Emirates ID exists in the database
        cur.execute("SELECT * FROM tblstudents WHERE emirates_id = %s", (emirates_id,))
        student = cur.fetchone()

        if student:
            # Set session variable to store the logged-in student's Emirates ID
            session['emirates_id'] = emirates_id
            # Inside your Flask route after setting the session variable
            print('Emirates ID stored in session:', session['emirates_id'])
            # Redirect to student_reports route
            return redirect(url_for('student_reports'))
        else:
            return jsonify({'error': 'Invalid Emirates ID'}), 404
        

def get_academic_year():
    today = datetime.now()
    if today.month < 8:  # Academic year starts from August
        return today.year - 1, today.year
    else:
        return today.year, today.year + 1

def get_term_dates(term):
    academic_year_start, academic_year_end = get_academic_year()

    if term == 'term1':
        start_date = f"{academic_year_start}-08-01"  # Beginning of August of the academic year
        end_date = f"{academic_year_start}-12-31"  # End of December of the academic year
    elif term == 'term2':
        start_date = f"{academic_year_start + 1}-01-01"  # Beginning of January of the next year
        end_date = f"{academic_year_start + 1}-03-31"  # End of March of the next year
    elif term == 'term3':
        start_date = f"{academic_year_start + 1}-04-01"  # Beginning of April of the next year
        end_date = f"{academic_year_end}-07-31"  # End of July of the academic year

    print("Start date for", term, ":", start_date)  # Debug statement
    print("End date for", term, ":", end_date)  # Debug statement

    return start_date, end_date

@app.route('/update_action', methods=['POST'])
def update_action():
    try:
        # Get the selected assessment type and term from the request data
        selected_assessment_type = request.json.get('assessment_type')
        selected_term = request.json.get('term')

        print("Selected assessment type:", selected_assessment_type)  # Debug statement
        print("Selected term:", selected_term)  # Debug statement

        # Get the start and end dates for the selected term
        term_start_date, term_end_date = get_term_dates(selected_term)

        # Define the update query
        update_query = """
            UPDATE tblresults
            SET action = CASE 
                            WHEN assessment_type = %s AND result_date BETWEEN %s AND %s AND (action = 'hide' OR action IS NULL) THEN 'explore' 
                            WHEN assessment_type = %s AND result_date BETWEEN %s AND %s AND (action = 'explore' OR action IS NULL) THEN 'hide' 
                            ELSE action 
                        END
            WHERE assessment_type = %s AND result_date BETWEEN %s AND %s
        """

        # Fetch records count before updating
        cur.execute("SELECT COUNT(*) FROM tblresults WHERE assessment_type = %s AND result_date BETWEEN %s AND %s",
                    (selected_assessment_type, term_start_date, term_end_date))
        records_count_before = cur.fetchone()[0]
        print("Number of matching records before update:", records_count_before)

        # Execute the update query with parameters
        cur.execute(update_query, (selected_assessment_type, term_start_date, term_end_date, 
                                    selected_assessment_type, term_start_date, term_end_date,
                                    selected_assessment_type, term_start_date, term_end_date))

        # Commit the transaction
        conn.commit()

        # Fetch records count after updating
        cur.execute("SELECT COUNT(*) FROM tblresults WHERE assessment_type = %s AND result_date BETWEEN %s AND %s",
                    (selected_assessment_type, term_start_date, term_end_date))
        records_count_after = cur.fetchone()[0]
        print("Number of matching records after update:", records_count_after)

        # Return a success message
        return jsonify({'message': f'Action column updated successfully for term: {selected_term}. Updated results printed in console.'}), 200

    except Exception as e:
        # Return an error message if an exception occurs
        print("Error:", str(e))  # Debug statement
        return jsonify({'error': str(e)}), 500

@app.route('/explored_assessments', methods=['GET'])
def get_explored_assessments():
    try:
        print("Inside /explored_assessments route")  # Debug statement

        # Perform a query to fetch explored assessments from the results table where action = 'explore'
        cur.execute("SELECT DISTINCT assessment_type, result_date FROM tblresults WHERE action = 'explore'")
        explored_assessments = cur.fetchall()

        print("Explored assessments:", explored_assessments)  # Debug statement

        # Initialize an empty list to store mapped assessments
        mapped_assessments = []

        # Loop through each explored assessment, determine its term using the `determine_term` function, and append the assessment and its corresponding term to the `mapped_assessments` list
        for assessment in explored_assessments:
            assessment_type, result_date = assessment
            # Determine the term for the result_date
            term = determine_term(result_date)
            # Construct the string with assessment type and term
            assessment_with_term = f"{assessment_type} {term}"
            # Append the assessment with its corresponding term to the mapped_assessments list
            mapped_assessments.append(assessment_with_term)

        # Return the list of explored assessments along with their terms as JSON
        print("Mapped assessments:", mapped_assessments)  # Debug statement
        return jsonify({'explored_assessments': mapped_assessments}), 200

    except Exception as e:
        # Return an error message if an exception occurs
        print("Error:", str(e))  # Debug statement
        return jsonify({'error': 'An error occurred while fetching explored assessments'}), 500


def determine_term(result_date):
    # Determine the academic year for the given result_date
    academic_year_start, academic_year_end = get_academic_year()

    # Convert academic year start and end dates to datetime.date objects
    academic_year_start_date = datetime.strptime(f"{academic_year_start}-08-01", "%Y-%m-%d").date()
    academic_year_end_date = datetime.strptime(f"{academic_year_end}-07-31", "%Y-%m-%d").date()

    # Check which term the result_date falls into
    if academic_year_start_date <= result_date <= datetime.strptime(f"{academic_year_start}-12-31", "%Y-%m-%d").date():
        return 'term1'
    elif datetime.strptime(f"{academic_year_start + 1}-01-01", "%Y-%m-%d").date() <= result_date <= datetime.strptime(f"{academic_year_start + 1}-03-31", "%Y-%m-%d").date():
        return 'term2'
    elif datetime.strptime(f"{academic_year_start + 1}-04-01", "%Y-%m-%d").date() <= result_date <= academic_year_end_date:
        return 'term3'
    else:
        return None

# Route to render the dashboard page
@app.route('/dashboard')
def dashboard():
    print("Root route accessed.")
    return render_template('dashboard.html')

# Route to fetch data for the dashboard
@app.route('/dashboard_data')
def dashboard_data():
    try:
        

        # Count total students
        cur.execute("SELECT COUNT(*) FROM tblstudents")
        total_students = cur.fetchone()[0]

        # Count total classes
        cur.execute("SELECT COUNT(DISTINCT ClassName) FROM tblclasses")
        total_classes = cur.fetchone()[0]

        # Fetch daily attendance data for the first 3 periods
        cur.execute("SELECT COUNT(DISTINCT student_name) FROM tblattendance WHERE attendance_date = CURRENT_DATE AND period <= 3 AND attendance IN ('Present', 'Late', 'Sleep')")
        present_or_late_or_sleep_students_first_3_periods = cur.fetchone()[0]

        # Calculate the number of students who were late during the first 3 periods
        cur.execute("SELECT COUNT(DISTINCT student_name) FROM tblattendance WHERE attendance_date = CURRENT_DATE AND period <= 3 AND attendance = 'Late'")
        late_students_first_3_periods = cur.fetchone()[0]

        # Calculate the morning delay percentage for the first 3 periods
        morning_delay_percentage_first_3_periods = (late_students_first_3_periods / present_or_late_or_sleep_students_first_3_periods) * 100 if present_or_late_or_sleep_students_first_3_periods > 0 else 0


        # Fetch daily attendance data
        cur.execute("SELECT COUNT(*) FROM tblattendance WHERE attendance_date = CURRENT_DATE AND attendance IN ('Present', 'Late', 'Sleep')")
        present_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tblattendance WHERE attendance_date = CURRENT_DATE AND attendance IN ('Absent', 'Excused')")
        absence_count = cur.fetchone()[0]

        # Calculate daily attendance percentages
        total_attendance = present_count + absence_count
        daily_presence_percentage = round((present_count / total_attendance) * 100, 1) if total_attendance > 0 else 0
        daily_absence_percentage = round((absence_count / total_attendance) * 100, 1) if total_attendance > 0 else 0
        morning_delay_percentage_first_3_periods = round(morning_delay_percentage_first_3_periods, 1)


        # Construct the data to be sent to the dashboard template
        dashboard_data = {
            'total_students': total_students,
            'total_classes': total_classes,
            'daily_presence_percentage': daily_presence_percentage,
            'daily_absence_percentage': daily_absence_percentage,
            'morning_delay_percentage_first_3_periods': morning_delay_percentage_first_3_periods
        }

        print("Received data for dashboard:", dashboard_data)

        # Return the data as JSON to be consumed by the dashboard JavaScript
        return jsonify(dashboard_data)

    except Exception as e:
        print("Error fetching dashboard data:", e)
        return jsonify({'error': str(e)}), 500
    
# Route to render the dashboard page
@app.route('/student_reports')
def student_reports():
    
    return render_template('student_reports.html')



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_login'] = True
            # Call JavaScript function to display success message
            return redirect(url_for('index'))  # Redirect to index after successful login
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin_login.html')

@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == TEACHER_USERNAME and password == TEACHER_PASSWORD:
            session['teacher_login'] = True
            # Call JavaScript function to display success message
            return redirect(url_for('index'))  # Redirect to index after successful login
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin_login.html')



@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('admin_login'))  # Redirect to admin login page




# Route to handle creating a class
@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if request.method == 'POST':
        classname = request.form['classname']
        classnamenumeric = int(request.form['classnamenumeric'])  
        num_students = int(request.form['num_students'])  
        section = request.form['section']
        
        cur.execute("INSERT INTO tblclasses (ClassName, ClassNameNumeric, NumberOfStudents, Section) VALUES (%s, %s, %s, %s)", 
                    (classname, classnamenumeric, num_students, section))
        conn.commit()
        
        return redirect(url_for('index'))
    else:
        return render_template('create_class.html')

# Route to render the manage classes page
@app.route('/manage_classes')
def manage_classes():
    cur.execute("SELECT id, ClassName, ClassNameNumeric, NumberOfStudents, Section, CreationDate FROM tblclasses")
    classes_data = cur.fetchall()
    return render_template('manage_classes.html', class_data=classes_data)

# Route to update a class
@app.route('/update_class', methods=['POST'])
def update_class():
    if request.method == 'POST':
        class_id = request.form['class_id']  
        classname = request.form['classname']
        classnamenumeric = int(request.form['classnamenumeric'])  
        num_students = int(request.form['num_students'])  
        section = request.form['section']
        
        cur.execute("UPDATE tblclasses SET ClassName = %s, ClassNameNumeric = %s, NumberOfStudents = %s, Section = %s WHERE id = %s", 
                    (classname, classnamenumeric, num_students, section, class_id))
        conn.commit()
        
    return redirect(url_for('manage_classes'))

# Route to handle adding a student
@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        full_name = request.form['full_name']
        student_number = request.form['student_number']
        emirates_id = request.form['emirates_id']
        
        gender = request.form['gender']
        class_id = request.form['class']
        
        
        # Perform database insertion here
        try:
            cur.execute("INSERT INTO tblstudents (full_name, student_number, emirates_id, gender, class_id) VALUES (%s, %s, %s, %s, %s)", 
                        (full_name, student_number, emirates_id, gender, class_id))
            conn.commit()
            # Flash a success message
            flash('Student added successfully!', 'success')
        except Exception as e:
            # Flash an error message if the student addition fails
            flash('Error adding student: {}'.format(str(e)), 'error')

        # Render the add_students template regardless of success or failure
        return redirect(url_for('add_students'))

# Route to render the add students form
@app.route('/add_students')
def add_students():
    # Fetch class data from tblclasses
    cur.execute("SELECT id, ClassName, Section FROM tblclasses")
    classes_data = cur.fetchall()
    return render_template('add_students.html', classes_data=classes_data)


# Route to fetch students based on class ID
@app.route('/get_students', methods=['POST'])
def get_students():
    if request.method == 'POST':
        class_id = request.form['class_id']
        cur.execute("SELECT * FROM tblstudents WHERE class_id = %s", (class_id,))
        student_data = cur.fetchall()
        # Convert student data to a list of dictionaries for JSON serialization
        students = [{'id': row[0], 'full_name': row[1], 'student_number': row[2], 'emirates_id': row[3], 'gender': row[4]} for row in student_data]
        return jsonify(students)
    else:
        return jsonify([])  # Return an empty list if no data is found


# Route to render the manage students page
@app.route('/manage_students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        class_id = request.form['class']
        cur.execute("SELECT * FROM tblstudents WHERE class_id = %s", (class_id,))
        student_data = cur.fetchall()
        return render_template('manage_students.html', student_data=student_data)
    else:
        cur.execute("SELECT id, ClassName, Section FROM tblclasses")
        class_data = cur.fetchall()
        return render_template('manage_students.html', class_data=class_data)

@app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    if request.method == 'GET':
        # Fetch student data from the database
        cur.execute("SELECT s.*, c.ClassName FROM tblstudents s JOIN tblclasses c ON s.class_id::int = c.id WHERE s.id = %s", (student_id,))

        student_data = cur.fetchone()
        return jsonify(html=render_template('update_student.html', student_data=student_data))
    elif request.method == 'POST':
        # Process the form data for updating the student
        full_name = request.form.get('full_name')
        student_number = request.form.get('student_number')
        emirates_id = request.form.get('emirates_id')
        gender = request.form.get('gender')
        
        
        if full_name and student_number and emirates_id and gender:
            # Update student data in the database
            cur.execute("UPDATE tblstudents SET full_name = %s, student_number = %s, emirates_id = %s, gender = %s WHERE id = %s", 
                        (full_name, student_number, emirates_id, gender, student_id))
            conn.commit()
            return jsonify(success=True)
        else:
            flash('Error: Form data incomplete!', 'error')
            return jsonify(success=False, message='Form data incomplete')



# Route to delete a student
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    cur.execute("DELETE FROM tblstudents WHERE id = %s", (student_id,))
    conn.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('manage_students'))

# Route to render the attendance page
@app.route('/attendance')
def attendance():
    return render_template('attendance.html')
# Route to render the attendance page
@app.route('/manage_attendance')
def manage_attendance():
    return render_template('manage_attendance.html')

@app.route('/get_classes', methods=['GET'])
def get_classes():
    try:
        cur.execute("SELECT id, ClassName, Section FROM tblclasses")
        classes_data = cur.fetchall()
        classes = []
        for row in classes_data:
            class_info = {
                'id': row[0],
                'ClassName': row[1],
                'Section': row[2]
            }
            classes.append(class_info)
        return jsonify(classes)
    except psycopg2.Error as e:
        
        return jsonify({'error': 'Database error occurred'}), 500
    

@app.route('/get_attendance', methods=['POST'])
def get_attendance():
    if request.method == 'POST':
        try:
            # Retrieve the selected date and class name from the AJAX request
            attendance_date = request.json.get('attendanceDate')
            class_name = request.json.get('className')

            # Check if attendance_date is empty
            if not attendance_date:
                return jsonify({'error': 'Attendance date is required'}), 400

            # Query the database to fetch attendance data for the selected date and class
            cur.execute("""
                SELECT student_name, student_number, period, attendance, specialist_comments
                FROM tblattendance
                WHERE attendance_date = %s AND class_name = %s
            """, (attendance_date, class_name))

            # Fetch all the attendance records
            attendance_data = cur.fetchall()

            # Check if there is any data available for the selected class on the selected date
            if not attendance_data:
                # If no data available, return an empty attendance table body
                return jsonify({'attendance_table_body': {}}), 200

            # Construct a dictionary to store attendance data organized by student
            attendance_dict = {}

            for record in attendance_data:
                student_name = record[0]
                student_number = record[1]
                period = record[2]
                attendance = record[3]
                specialist_comments = record[4]

                
                if student_number not in attendance_dict:
                    attendance_dict[student_number] = {
                        'student_name': student_name,
                        'periods': {}
                    }

                attendance_dict[student_number]['periods'][period] = {
                    'attendance': attendance,
                    'specialist_comments': specialist_comments
                }

            # Return the attendance data as JSON
            return jsonify({'attendance_table_body': attendance_dict}), 200


        except Exception as e:
            error_msg = f'An error occurred: {str(e)}'
            logging.error("Error: %s", error_msg)  # Log the error
            return jsonify({'error': error_msg}), 500
        
        

# Route to handle saving attendance data for a specific period
@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    if request.method == 'POST':
        try:
            data = request.json
            attendance_date = data.get('attendanceDate')
            class_name = data.get('className')
            attendance_data = data.get('attendanceData')
            

            # Connect to the database
            with conn:
                with conn.cursor() as cur:
                    # Delete existing attendance data for the given date and class
                    cur.execute("""
                        DELETE FROM tblattendance 
                        WHERE attendance_date = %s AND class_name = %s
                    """, (attendance_date, class_name))

                    # Loop through attendance data and insert records into tblattendance
                    for record in attendance_data:
                        student_name = record['student_name']
                        student_number = record['student_number']
                        periods = record['periods']

                        for period, attendance in periods.items():
                            if attendance:
                                specialist_comments = record.get('specialist_comments', '') if attendance else ''
                                cur.execute("""
                                    INSERT INTO tblattendance 
                                    (attendance_date, period, class_name, student_name, student_number, attendance, specialist_comments)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                """, (attendance_date, period, class_name, student_name, student_number, attendance, specialist_comments))

            return jsonify({"message": "Attendance saved successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Route to handle saving attendance for a specific period
@app.route('/save_period_attendance', methods=['POST'])
def save_period_attendance():
    if request.method == 'POST':
        try:
            data = request.json
            logging.debug("Received data: %s", data)  # Log received data
            
            # Extract required fields from the request data
            attendance_date = data.get('attendanceDate')
            period = data.get('period')
            class_name = data.get('className')  # Changed from class_id to class_name
            attendance_data = data.get('attendanceData')
            
            # Check if any required field is missing
            if None in [attendance_date, period, class_name, attendance_data]:  # Changed class_id to class_name
                raise KeyError("One or more required fields are missing")
                
            # Validate the format of attendance data
            for record in attendance_data:
                if not all(key in record for key in ['studentName', 'studentNumber', 'attendance']):
                    raise KeyError("One or more required fields in the attendance record are missing")
                    
            # Loop through attendance data and save/update each record in tblattendance
            for record in attendance_data:
                student_name = record['studentName']
                student_number = record['studentNumber']
                attendance = record['attendance']
                specialist_comments = record.get('specialistComments', '')  # Handle missing specialistComments
                
                # Check if the record already exists in the database
                cur.execute("""
                    SELECT attendance, specialist_comments FROM tblattendance 
                    WHERE attendance_date = %s
                    AND period = %s
                    AND class_name = %s
                    AND student_name = %s
                    AND student_number = %s
                """, (attendance_date, period, class_name, student_name, student_number))
                
                existing_record = cur.fetchone()
                
                if existing_record:
                    # If the record exists, update attendance and specialist comments
                    if attendance != existing_record[0] or specialist_comments != existing_record[1]:
                        cur.execute("""
                            UPDATE tblattendance 
                            SET attendance = %s, specialist_comments = %s
                            WHERE attendance_date = %s
                            AND period = %s
                            AND class_name = %s
                            AND student_name = %s
                            AND student_number = %s
                        """, (attendance, specialist_comments, attendance_date, period, class_name, student_name, student_number))
                else:
                    # If the record doesn't exist, insert it
                    cur.execute("""
                        INSERT INTO tblattendance 
                        (attendance_date, period, class_name, student_name, student_number, attendance, specialist_comments)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (attendance_date, period, class_name, student_name, student_number, attendance, specialist_comments))
                
            # Commit the transaction
            conn.commit()
            
            # Return success response
            return jsonify({'success': True}), 200
            
        except KeyError as e:
            error_msg = f'Missing key: {e}'
            logging.error("Error: %s", error_msg)  # Log the error
            return jsonify({'error': error_msg}), 400
        except Exception as ex:
            error_msg = f'An error occurred: {str(ex)}'
            logging.error("Error: %s", error_msg)  # Log the error
            conn.rollback()  # Rollback the transaction in case of failure
            return jsonify({'error': error_msg}), 500



# Route to render the results form
@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        class_id = request.form.get('class')
        result_date = request.form.get('results_date')
        
        # Fetch students for the selected class
        cur.execute("SELECT id, full_name, emirates_id, student_number FROM tblstudents WHERE class_id = %s", (class_id,))
        students_data = cur.fetchall()
        
        # Render the results form with students' data
        return render_template('results.html', students_data=students_data, result_date=result_date)
    else:
        # Fetch class data from tblclasses
        cur.execute("SELECT id, ClassName, Section FROM tblclasses")
        classes_data = cur.fetchall()
        return render_template('results.html', classes_data=classes_data)

@app.route('/save_results', methods=['POST'])
def save_results():
    if request.method == 'POST':
        try:
            data = request.json
            logging.debug("Received data: %s", data)  # Log received data
            
            # Extract required fields from the request data
            result_date = data.get('resultsDate')  # Updated to match with the frontend
            class_name = data.get('className')
            assessment_type = data.get('assessmentType')  # Extract assessment type from the request data
            student_results = data.get('studentResults')

            # Check if any required field is missing
            if None in [result_date, class_name, assessment_type, student_results]:
                raise KeyError("One or more required fields are missing")
                
            # Loop through student results and save/update each record in tblresults
            for result in student_results:
                student_name = result.get('studentName')
                student_number = result.get('studentNumber')
                emirates_id = result.get('emiratesId')
                subject = data.get('subject')  # Extract subject from the main data, not from each student result
                marks = result.get('marks')
                behavior_notes = result.get('behaviorNotes')
                other_notes = result.get('otherNotes')
                
                # Check if the record already exists in the database
                cur.execute("""
                    SELECT * FROM tblresults 
                    WHERE result_date = %s
                    AND class_name = %s
                    AND student_name = %s
                    AND student_number = %s
                    AND subject = %s
                """, (result_date, class_name, student_name, student_number, subject))
                
                existing_record = cur.fetchone()
                
                if existing_record:
                    # Check if subject or assessment type has changed
                    if existing_record[7] != assessment_type or existing_record[6] != subject:
                        # Insert a new record
                        cur.execute("""
                            INSERT INTO tblresults 
                            (result_date, class_name, student_name, student_number, emirates_id, subject, marks, assessment_type,  behavior_notes, other_notes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (result_date, class_name, student_name, student_number, emirates_id, subject, marks, assessment_type, behavior_notes,  other_notes))
                    else:
                        # Update the existing record
                        cur.execute("""
                            UPDATE tblresults 
                            SET emirates_id = %s, assessment_type = %s, marks = %s,
                            behavior_notes = %s, other_notes = %s
                            WHERE result_date = %s
                            AND class_name = %s
                            AND student_name = %s
                            AND student_number = %s
                            AND subject = %s
                        """, (emirates_id, assessment_type, marks, behavior_notes, other_notes, result_date, class_name, student_name, student_number, subject))

                else:
                    # If the record doesn't exist, insert it as a new record
                    cur.execute("""
                        INSERT INTO tblresults 
                        (result_date, class_name, student_name, student_number, emirates_id, subject, assessment_type, marks, behavior_notes, other_notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (result_date, class_name, student_name, student_number, emirates_id, subject, assessment_type, marks, behavior_notes, other_notes))

            # Commit the transaction
            conn.commit()
            
            # Return success response
            return jsonify({'success': True}), 200
            
        except KeyError as e:
            error_msg = f'Missing key: {e}'
            logging.error("Error: %s", error_msg)  # Log the error
            return jsonify({'error': error_msg}), 400
        except Exception as ex:
            error_msg = f'An error occurred: {str(ex)}'
            logging.error("Error: %s", error_msg)  # Log the error
            # conn.rollback()  # Rollback the transaction in case of failure
            return jsonify({'error': error_msg}), 400
            
    else:
        return jsonify(success=False, message='Method not allowed'), 405


# Route to manage results
@app.route('/manage_results')
def manage_results():
    return render_template('manage_results.html')

# Route to fetch distinct class_name, subject, and assessment_type from tblresults
@app.route('/get_results_info', methods=['GET'])
def get_results_info():
    cur.execute("SELECT DISTINCT class_name, subject, assessment_type, marks FROM tblresults")
    results_info = cur.fetchall()
    print("Results Info:", results_info)  # Add print statement to see fetched data
    
    # Construct a list of dictionaries containing the fetched data
    results_info_formatted = []
    for result in results_info:
        result_info = {
            'class_name': result[0],
            'subject': result[1],
            'assessment_type': result[2],
            'marks': result [3]
        }
        results_info_formatted.append(result_info)
    
    return jsonify(results_info_formatted)


# Route to fetch results based on class, subject, and assessment type
@app.route('/get_results', methods=['GET'])
def get_results():
    class_name = request.args.get('class_name')
    subject = request.args.get('subject')
    assessment_type = request.args.get('assessment_type')

    # Perform database query to fetch results based on class, subject, and assessment type
    cur.execute("SELECT * FROM tblresults WHERE class_name = %s AND subject = %s AND assessment_type = %s",
                (class_name, subject, assessment_type))
    result_data = cur.fetchall()
    print("Result Data:", result_data)  # Add print statement to see fetched data

    # Return the result data as JSON
    return jsonify(result_data)

@app.route('/change_results', methods=['POST'])
def change_results():
    if request.method == 'POST':
        try:
            data = request.json
            logging.debug("Received data: %s", data)  # Log received data
            
            # Loop through the received data and update the corresponding records in the database
            for result in data:
                student_name = result.get('studentName')
                student_number = result.get('studentNumber')
                subject = result.get('subject')
                marks = result.get('marks')
                behavior_notes = result.get('behaviourNotes')
                other_notes = result.get('otherNotes')
                
                # Update the corresponding record in the database
                cur.execute("""
                    UPDATE tblresults 
                    SET marks = %s, behavior_notes = %s, other_notes = %s
                    WHERE student_name = %s 
                    AND student_number = %s 
                    AND subject = %s
                """, (marks, behavior_notes, other_notes, student_name, student_number, subject))
                
                # Commit the transaction
                conn.commit()
                
                logging.debug("Data for %s in %s updated successfully", student_name, subject)  # Log success message

            # Return success response
            return jsonify({'success': True}), 200
            
        except Exception as ex:
            error_msg = f'An error occurred: {str(ex)}'
            logging.error("Error: %s", error_msg)  # Log the error
            return jsonify({'error': error_msg}), 400
            
    else:
        return jsonify(success=False, message='Method not allowed'), 405


# Route to update a result
@app.route('/update_result/<int:result_id>', methods=['POST'])
def update_result(result_id):
    if request.method == 'POST':
        # Extract updated result data from the request
        # Perform database update based on the provided data
        # Return appropriate response
        
        return jsonify(success=True)  # Return success response
    else:
        return jsonify(success=False, message='Method not allowed'), 405

# Route to delete a result
@app.route('/delete_result/<int:result_id>', methods=['POST'])
def delete_result(result_id):
    if request.method == 'POST':
        # Perform database deletion of the specified result
        # Return appropriate response
        
        return jsonify(success=True)  # Return success response
    else:
        return jsonify(success=False, message='Method not allowed'), 405


# Route to render the report generation page
@app.route('/report_generation')
def report_generation():
    return render_template('report_generation.html')

# Route to render the communication tools page
@app.route('/communication_tools')
def communication_tools():
    return render_template('communication_tools.html')





STUDENTS_DATA = [
    ('BADER ALI ABDULLA SAEED AL GHAITHI', '790995', '784201337208405', 'male', '5A'),
('HAMAD AHMED ALI EISA ALKETBI', '791862', '784201390752430', 'male', '5A'),
('HAMED SULTAN MOHAMMED HUMAID AL KALBANI', '781352', '784201385703745', 'male', '5A'),
('HAMAD SAIF SALEM SAEED ALMEQBAALI', '791103', '784201332098595', 'male', '5A'),
('HAMDAN KHALID ALI KHAMIS AL MAAMARI', '791167', '784201396054195', 'male', '5A'),
('KHALED RASHED ALI RASHED ALMEQBAALI', '784436', '784201370854644', 'male', '5A'),
('KHALED MOHAMMED BAKHIT RASHED ALRASHDI', '788455', '784201390305981', 'male', '5A'),
('DHEYAB MATAR ISMAIL MATAR ALDARMAKI', '818724', '', 'male', '5A'),

('SALIM KHALID RASHID ALI ALNUAIMI', '20220039784', '784201319766347', 'male', '5A'),
('SALEM SAEED SAIF SAEED AL MEQBAALI', '791606', '784201342962483', 'male', '5A'),
('SALEM SAEED NASSER HAMAD ALDEREI', '795652', '784201321390946', 'male', '5A'),
('SULTAN AHMED ABDULLA MASOUD ALSHAMSI', '788792', '784201315924247', 'male', '5A'),
('ABDULRUHMAN KHALED SAOUD BADER ALSAWWAFI', '784266', '784201308314810', 'male', '5A'),
('ABDULAZIZ ALI SALEM ABDULLA AL KINDI', '786653', '784201396971703', 'male', '5A'),
('ALI AHMED ALI KHAMIS ALSHAMSI', '791938', '784201368537649', 'male', '5A'),
('ALI MOHAMMED AWAD ABDULLA SULTAN', '790357', '784201371827177', 'male', '5A'),
('ALI ABDULLAH SAID HUMAID AL KAABI', '846325', '784201392910390', 'male', '5A'),
('MOHAMMED SULTAN MOHAMMED HUMAID AL KALBANI', '781439', '784201353906197', 'male', '5A'),
('OMAR KHALID AWAD HAMAD ALZEIDI', '818551', '784201306107620', 'male', '5A'),
('OMAR ABDULLA MOHAMMED SHMAIL ALRASHDI', '783202', '784201361608595', 'male', '5A'),
('MUBARAK MUSABBEH MUBARAK SLAYEM ALKETBI', '788090', '784201362839215', 'male', '5A'),
('METREF SALEM MOHAMMED SUWAID AL MEQBAALI', '818863', '784201336046962', 'male', '5A'),
('MANSOUR AHMED MOHAMMED ABDULLAH AL KAABI', '819019', '784201361914308', 'male', '5A'),
('MANSOUR HAMAD ABDULLA AIL AL RASHDI', '782367', '784201310579491', 'male', '5A'),
('MANSOUR MOHAMMED RASHED KHALFAN', '784881', '784201341527253', 'male', '5A'),
('MANSOUR MOHAMMED SULTAN RASHED AL KETBI', '788632', '784201327527475', 'male', '5A'),
('HADEF ABDULRAHMAN KHAMIS MOHAMMED AL NEYADI', '20190030070', '784201329858167', 'male', '5A'),


('HAMED YOUSUF ABDALLAH SAID AL KAABI', '787857', '784201332757315', 'male', '5B'),
('HAMAD SAEED HAMAD SHEMAIL ALRASHDI', '20190013926', '784201342436496', 'male', '5B'),
('HAMDAN AHMED ABDUL KHAKEQ SAIF AHMED', '822590', '784201330947595', 'male', '5B'),
('HAMDAN RASHED ABDULLA NASSER ALKAABI', '781878', '784201318259294', 'male', '5B'),
('THEYAB SAEED SALEM OBAID AL KETBI', '784460', '784201392507543', 'male', '5B'),
('RASHED SAOUD SULAIMAN MOHAMMED AL NEYADI', '783575', '784201319138729', 'male', '5B'),
('RASHED MUSABBEH SALEM MUBARAK AL KETBI', '789407', '784201357938048', 'male', '5B'),
('RASHED NASSER ABDULLA NASSER AL KAABI', '781467', '784201330352838', 'male', '5B'),
('SALEM BADER HAMAD ALI ALRASHDI', '784554', '784201386463919', 'male', '5B'),
('SALEM MOHAMMED ALI JUMA ALRASHDI', '787327', '784201374279384', 'male', '5B'),
('SAOUD MOHAMMED SALIM RASHED AL MUKHAINI', '783223', '784201320639053', 'male', '5B'),

('SAIF AHMED HAREB ALRAEI ALKTEBI', '784187', '784201305926293', 'male', '5B'),
('SAIF KHALIFA SAID SABAYAH ALKAABI', '789948', '784201303804054', 'male', '5B'),
('SAIF TALAL KHALAF SULAIMAN ALAZEEZI', '788420', '784201392486391', 'male', '5B'),
('SAIF MUBARAK HAMAD MUBARAK ALNUAIMI', '844393', '784201328037623', 'male', '5B'),
('ABDULLA MOHAMMED SAIF AHMED ALKINDI', '20190025337', '784201327614356', 'male', '5B'),
('ABDULLAH SULTAN ABDULLAH SULIMAN AL SHAMSI', '785155', '784201310253147', 'male', '5B'),
('GHAITH SALIM KHALFAN SALIM ALHEBSI', '805561', '784201328048612', 'male', '5B'),
('MOHAMMED NASSER MUBARAK RASHID AL TAMIMI', '895942', '784201324047246', 'male', '5B'),
('MOHAMMED YASIR MOHAMMED SAID AL SHAMSI', '860218', '784201347251643', 'male', '5B'),
('MOHAMMED KHAMIS SALEM HAMAD AL RASHDI', '20200015508', '784201394327189', 'male', '5B'),
('MOHAMMED SALEM HAMDAN ALALAWI', '806670', '784201337509497', 'male', '5B'),
('MOHAMMED SALEM ALI JUMA ALRASHDI', '787344', '784201386871525', 'male', '5B'),
('MOHAMMED MATAR SALMEEN GHUMAIL ALWAHSHI', '789374', '784201369681933', 'male', '5B'),
('MUSABBEH SAEED MUSABBEH SAEED ALMEQBAALI', '782044', '784201315140646', 'male', '5B'),
('NAWAF SAEED RASHED HUMAID ALSENAANI', '792752', '784201392864613', 'male', '5B'),
('HAZAA SAEED KHAMIS MUHANNA ALHASSANI', '20220018397', '784201348602059', 'male', '5B'),
('HAZZA OMAR SUBAIH RASHED ALRASHDI', '787620', '784201307476263', 'male', '5B'),


('AHMED HAMDAN SALEM SAEED ALMEQBAALI', '790851', '784201375737075', 'male', '5C'),
('AHMED SAIF SALEM MUBARAK ALKHATERI', '791578', '784201364041570', 'male', '5C'),
('AHMAD SALEH AL NEKHAIARA BUTI ALSHAMSI', '790531', '784201392703837', 'male', '5C'),
('JUMA NASSER ABDEL AZIZ ISSA AL BALUSHI', '786900', '784201303287417', 'male', '5C'),
('HAMAD SALEM RASHID ALKAABI', '812780', '784201105949297', 'male', '5C'),
('HAMAD SOHAIL HAMAD MUFTAH ALNEYADI', '20210015301', '784201307054821', 'male', '5C'),
('HAMAD ABDULLA AHMED ALAZZANI ALNUAIMI', '790960', '784201314380292', 'male', '5C'),
('HAMDAN MOHAMMED SAIF SAEED ALNEYADI', '801674', '784201382653968', 'male', '5C'),
('KHALIFAH SALIM KHALFAN SAIF AL SHAMSI', '805886', '784201332646088', 'male', '5C'),
('KHALIFA SUHAIL DEHAI KHASSIB ALMEQBAALI', '788423', '784201310813874', 'male', '5C'),
('KHALIFA YAHYA MAL ALLA SAEED AL KHAMIRI', '788525', '784201314918091', 'male', '5C'),
('RASHED SAEED MOHAMMED KHAMIS ALNUAIMI', '787648', '784201313508422', 'male', '5C'),
('SALEM SAEED SALEM HUMAID ALALAWI', '783853', '784201324307384', 'male', '5C'),
('SALEM SAEED QANNON SAEED ALKTEBI', '789104', '784201353585066', 'male', '5C'),
('SULTAAN AHMED SABIH SAID ALKAABI', '20210043063', '784201337681809', 'male', '5C'),
('SALMAN YASER SUHAIL EISA', '20210014549', '784201396038313', 'male', '5C'),
('SALMAN YOUSEF ANBAR KHALFAN ALSENAANI', '818402', '784201363150836', 'male', '5C'),
('SAIF AHMED SULTAN MOHAMMED ALKAABI', '789187', '784201319131427', 'male', '5C'),
('MOHAMMED KHAMIS ALI SAEED ALKAABI', '781829', '784201357946496', 'male', '5C'),
('MOHAMMED ABDULLA SAEED KHALFAN ALNUAIMI', '901283', '784201329317602', 'male', '5C'),
('MOHAMMED WAHEEB SALEM ABDULLA ALKINDI', '789460', '784201348320520', 'male', '5C'),
('MANSOUR KHALED ABDULLA NASSER ALNUAIMI', '788577', '784201370304756', 'male', '5C'),
('MANSOUR ALI ABDULLA SAEED ALGHAITHI', '791001', '784201321707073', 'male', '5C'),
('MANSOUR MOHAMMED SAIF MUBARAK ALAMERI', '781260', '784201314181716', 'male', '5C'),
('MUHAYER NASSER ABDULLA NASSER ALNUAIMI', '788564', '784201370639094', 'male', '5C'),
('WASEEM ABDELHAMID ELSHAHAT MOUSTAFA ABOUEISHA', '807465', '784201391604739', 'male', '5C'),
('YOUSEF RASHED AMER HUMAID ALMAHROOQI', '781521', '784201353635267', 'male', '5C'),


('AHMED SAEED ABDULLA HUMAID AL GHAITHI', '784810', '784201318416290', 'male', '5D'),
('HUMAID SAID SAIF RASHID AL SHUKAILI', '899127', '784201391950280', 'male', '5D'),
('HUMAID MOHAMMED SALEM HUMAID ALALAWI', '833110', '784201391861693', 'male', '5D'),
('KHALIFA KHALED SALEM RASHED ALEISSAEE', '793528', '784201310935255', 'male', '5D'),
('THAYAB AHMED KHAMIS MOHAMMED ALNEYADI', '786083', '784201317218366', 'male', '5D'),
('RASHED ABDULLA SAEED SALEM ALRASHDI', '830861', '784201368714354', 'male', '5D'),
('ZAYD ALI MOHAMMED SAIF AL BADI', '787433', '784201380295820', 'male', '5D'),
('ZAYED SAEED SALEM SAEED ALAMRI', '786592', '784201365298385', 'male', '5D'),
('SALEM KHALIFA MOHAMMED ALKHADEM ALKAABI', '783039', '784201306476355', 'male', '5D'),
('SAOUD SALEM SULTAN ALI ALKINDI', '788180', '784201339754638', 'male', '5D'),
('SULTAN SAEED OBAID SALEM', '805370', '784201346825397', 'male', '5D'),
('SAIF SAEED HAMAD ALI ALSHAMSI', '788585', '784201396251809', 'male', '5D'),
('ABDULLAH SAID MOHAMMED ALSALF ALNUAIMI', '786060', '784201375724321', 'male', '5D'),
('ALI ABDULLA MOHAMMED SAIF ALSHAMSI', '785973', '784201372106811', 'male', '5D'),
('ALI MUBARAK ALI HAMAD ALSHAMSI', '791144', '784201350959538', 'male', '5D'),
('ALI HAMAD MATAR HAMAD ALSHAMISI', '817745', '784201304863901', 'male', '5D'),
('ALI FAISAL ALI SALEM ALGHAITHI', '20200009525', '784201365952510', 'male', '5D'),
('OMAR HUMAID HAKIM ALI ALMEQBAALI', '786684', '784201361826593', 'male', '5D'),
('MOHAMMED HAMAD ABDULLA ALI AL RASHDI', '782310', '784201380376943', 'male', '5D'),
('MOHAMMED SAEED ABDULLA HUMAID AL GHAITHI', '784836', '784201362513976', 'male', '5D'),
('MOHAMMED SAEED FADEL ABDULLA ALSHAMSI', '20190013460', '784201304640481', 'male', '5D'),
('MOHAMMED SULTAN MOHAMMED SAIF ALNEYADI', '20200014969', '784201302080201', 'male', '5D'),
('MOHAMMED EID HAMAD SALEM ALHANAEE', '782903', '784201372592507', 'male', '5D'),
('MOHAMMED MASOUD SAIF ALI AL MEQBAALI', '783466', '784201337915967', 'male', '5D'),
('MOHAMMED YOUSEF ALTHEEB MOHAMMED ALKETBI', '792291', '784201368746141', 'male', '5D'),
('NASSER MOHAMMED AHMED MOHAMMED ALNUAIMI', '787855', '784201381858766', 'male', '5D'),
('NAYED SAEED SALMEEN HAMAD ALNUAIMI', '787030', '784201391039043', 'male', '5D'),
('YASER MOHAMMED ALI SULTAN AL KAABI', '790064', '784201385717539', 'male', '5D'),



('AHMED QURAISH ABDULLA QURAISH AL NUAIMI', '789691', '784201395209477', 'male', '5E'),
('AHMED MOHAMMED OBAID THAALOUB ALKETBI', '791471', '784201351813098', 'male', '5E'),
('BUTTI ALI RASHED MATAR ALNUAIMI', '783055', '784201396108314', 'male', '5E'),
('HAMED HASHEM ABDULKARIM MOHAMMED AL BALOOSHI', '781904', '784201390370746', 'male', '5E'),
('HAMDAN MOHAMMED HAMED SAID AL SAADI', '781436', '784201346213297', 'male', '5E'),
('HAMDAN RASHED ABDULLA NASSER ALKAABI', '781878', '784201318259294', 'male', '5E'),
('HAMDAN ALI SAEED ALI ALMEQBAALI', '834489', '784201373193610', 'male', '5E'),
('HAMDAN AHMED ABDALLAH HAMDAN ALALAWI', '809342', '784201304194257', 'male', '5E'),
('RASHED SAEED RASHED MUBARAK ALKETBI', '20200024050', '784201313541092', 'male', '5E'),
('RASHED ALI SAIF LEKHRAIBANI AL NUAIMI', '815969', '784201316426481', 'male', '5E'),
('RASHED MOHAMMED SAEED HAMDAN AL NUAIMI', '781303', '784201331982641', 'male', '5E'),
('ZAYED SULTAN MOHAMMED SAIF ALKAABI', '783758', '784201360428615', 'male', '5E'),
('SALEM TALAL SALEM SAEED ALSHAMSI', '836112', '784201315148383', 'male', '5E'),
('SAEED ABDULLA YOUSEF AHMED ALBLOOSHI', '840094', '784201347973659', 'male', '5E'),
('SAEED NASSER MOHAMMED MUSALLEM AL YAHYAEE', '784621', '784201302962838', 'male', '5E'),
('SULTAN KHAMIS SAID MOHAMMED ALKAABI', '20230033703', '784201346937622', 'male', '5E'),
('ABDULRAHMAN MOHAMMED AWAD OBAID ALNUAIMI', '789030', '784201359249170', 'male', '5E'),
('ABDUAZIZ ABDULLA SAEED KHALFAN ALSHAMSI', '790127', '784201308083167', 'male', '5E'),
('ALI KHALED ALI OBAID ALSHAMSI', '788442', '784201328508136', 'male', '5E'),
('ALI MOHAMMED KHALIFA MOHAMMED AL KAABI', '784237', '784201384026825', 'male', '5E'),
('ALI ABDULLA ALI ABDULLA ALMEQBAALI', '786707', '784201398085973', 'male', '5E'),
('ALI KHALED HAMAD SALEM ALKETBI', '781746', '784201386062810', 'male', '5E'),
('OMAR MOHAMMED OBAID THAALOUB ALKETBI', '791476', '784201319315426', 'male', '5E'),
('MOHAMMED KHALED SALEM ABDULLA ALARYANI', '783835', '784201310379041', 'male', '5E'),
('MANSOUR QATAMI SAEED MUBARAK ALKTEBI', '824134', '784201373514062', 'male', '5E'),
('MOHAMMED MUFTAH FARAJ MUBARAK ALNUAIMI', '783549', '784201363585700', 'male', '5E'),
('NAHYAN SAIF SANQOUR SAEED ALEFARI', '785592', '784201397091758', 'male', '5E'),







('AHMAD SAID MOHAMMED SAID ALNAIMI', '903535', '784201370820256', 'male', '5F'),
('JUMUAH FAHAD JUMA SAID AL KAABI', '783400', '784201338029826', 'male', '5F'),
('HAMAD RASHID HAMAD RASHID ALNUAIMI', '781724', '784201359076979', 'male', '5F'),
('HAMAD SALEM SAIF ALKHAMISI AL AMERI', '781377', '784201363095924', 'male', '5F'),
('HAMAD SAIF KHAMIS ALTHEEB ALNUAIMI', '20200017559', '784201379437607', 'male', '5F'),
('HAMAD SAIF SAEED SAIF ALNUAIMI', '781271', '784201316970975', 'male', '5F'),
('HAMAD ABDULQADER KHALED ABDULAZIZ AL DOUSARI', '20190032955', '784201316057096', 'male', '5F'),
('HUMAID BADER HUMAID HMOUD ALALAWI', '787276', '784201348295722', 'male', '5F'),
('HUMAID SULTAN HUMAID KHADOUM AL NUAIMI', '788966', '784201353297639', 'male', '5F'),
('HUMAID ALI SAEED ALI ALSAEDI', '782617', '784201353605435', 'male', '5F'),
('KHALID SULTAN JUMA SALIM AL GHAITHI', '904477', '784201365082847', 'male', '5F'),
('KHALIFA MOHAMMED ALI MUBARAK ALKETBI', '783096', '784201385705146', 'male', '5F'),
('THEYAB MOHAMMED SAEED JUMA ALKAABI', '791435', '784201368042434', 'male', '5F'),
('RASHED SALEM ABDULLA SAEED ALNUAIMI', '788986', '784201319431694', 'male', '5F'),
('SAID MOHAMMED JUMA SAID ALKAABI', '783401', '784201349170403', 'male', '5F'),
('SALEM SUHAIL KHAMIS MUBARAK AL NAEIMI', '902092', '784201382653943', 'male', '5F'),
('SAOUD MATAR SALEM OBAID ALKETBI', '788152', '784201339857613', 'male', '5F'),
('SAEED ABDULLA HAMAD SAEED ALARYANI', '790068', '784201361750389', 'male', '5F'),
('SAEED ABDULLA ALI JUMA ALRASHDI', '787307', '784201349054862', 'male', '5F'),
('SULTAN AHMED SALEM MUBARAK ALKETBI', '823628', '784201321581684', 'male', '5F'),
('SALEH ALI SALEH MUSAD ALNUAIMI', '790495', '784201316106489', 'male', '5F'),
('OMAR SAEED MOHAMMED MUSALLAM ALYAHYAEE', '787201', '784201309826549', 'male', '5F'),
('MUBARAK SAEED HAMAD NASSER AL SHAMSI', '790062', '784201330929627', 'male', '5F'),
('MOHAMMED NAIF JUMA SAID ALNAAIMI', '901311', '784201351361767', 'male', '5F'),
('MOHAMMED HAMAD HMOUD HAMAD AL KETBI', '814507', '784201310396524', 'male', '5F'),
('MOHAMMED HAMAD MOHAMMED ALI ALGHAITHI', '782283', '784201390272900', 'male', '5F'),
('MOHAMMED HAMAD MOHAMMED MUSALLEM ALYAHYAEE', '783985', '784201320946953', 'male', '5F'),
('MOHAMMED ADEEL MOHAMMED HAMED ALERYANI', '789394', '784201359219629', 'male', '5F'),
('HAZZA TAHNOUN MUSABBEH TARESH ALAMEEMI', '790009', '784201361739101', 'male', '5F'),



('AHMED RASHED MAKTOUM ALI AL SHAMSI', '835863', '784201352919597', 'male', '5G'),
('AHMED ALI MOHAMMED ARHAMA', '825991', '784201324138201', 'male', '5G'),
('AHMED HAZZA HAREB MOHAMMED ALSAEDI', '813187', '784201352065912', 'male', '5G'),
('HAMED BADAR KHALIFA MOHAMMED AL RUMHI', '790730', '784201351697251', 'male', '5G'),
('HAMED SALIM MOHAMMED SAEED ALKETBI', '20200010440', '784201309319610', 'male', '5G'),
('HAMAD SALEM MOHAMMED MUSALLEM AL YAHYAEI', '784562', '784201365365267', 'male', '5G'),
('HAMAD SAEED DHBAIB SALEM ALSHAMSI', '783925', '784201351764283', 'male', '5G'),
('HAMAD SULTAN SAEED SALEM ALSHAMSI', '784292', '784201375060205', 'male', '5G'),
('HAMAD ALI RASHED SULTAN ALKETBI', '782212', '784201365291323', 'male', '5G'),
('HAMAD MOHAMMED SAEED MUBARAK AL SHANDOURI', '785480', '784201304052711', 'male', '5G'),
('HAMDAN HUSSEIN HAMDAN MOHAMMED AL BALUSHI', '20190017727', '784201369428590', 'male', '5G'),

('HMOUD DAWOUD SAEED ALI ALNUAIMI', '788574', '784201303096529', 'male', '5G'),
('HUMAID SULAIMAN HUMAID OBAID AL NAAIMI', '902807', '784201348146479', 'male', '5G'),
('KHALED SAEED HAMAD HMOUD AL KETBI', '786604', '784201387602986', 'male', '5G'),
('KHALED ALI AMER SAIF ALEISSAEE', '790355', '784201369183872', 'male', '5G'),
('KHALIFA KHALID SAIF SALEM ALAZEEZI', '784166', '784201342651359', 'male', '5G'),
('THEYAB MOHAMMED HUMAID MOHAMMED ALFARSI', '783118', '784201329298752', 'male', '5G'),
('SALEM MATAR SALEM RASHED', '802645', '784201370598597', 'male', '5G'),
('SAEED SULTAN AHMED ABDULLA AL KETBI', '790638', '784201365276092', 'male', '5G'),
('SAEED ALI MUSABBEH SAEED AL KETBI', '787966', '784201365307988', 'male', '5G'),
('SAEED MUSABBEH MOHAMMED ALI ALRASHDI', '786624', '784201336542465', 'male', '5G'),
('ABDULRAHMAN ABDULLA ALI ALSALF ALNUAIMI', '791089', '784201393581596', 'male', '5G'),
('ALI SAEED SALEM ALKHAYALI ALKETBI', '20190018105', '784201309857254', 'male', '5G'),
('MAYED FAISAL SAEED SALEM', '803101', '784201318719149', 'male', '5G'),
('MOAHMMED KHALID KHALIFA JUMA ALKHAMISANI', '20210016144', '784201309376511', 'male', '5G'),
('MOHAMMED SAEED DHBAIB SALEM ALSHAMSI', '783936', '784201317361968', 'male', '5G'),
('MOHAMMED SULTAN MOHAMMED HAMED ALARYANI', '784702', '784201387027143', 'male', '5G'),
('MOHAMED MAHMOUD ABDELFATTAH MOHAMED HASSAN', '876048', '784201337306977', 'male', '5G'),
('MOHAMMED MATAR ABDULLA SALEH ALARYANI', '785494', '784201326176852', 'male', '5G'),
('MOHAMMED MOUSA SAEED ALI ALSAEDI', '782690', '784201379030592', 'male', '5G'),
('MATAR KHAMIS RASHED SAEED ALSAEDI', '791148', '784201353610765', 'male', '5G'),
('MANSOUR AHMED ABDULLA SAEED ALSAEDI', '783381', '784201302140930', 'male', '5G'),
('MANSOOR ADNAN TALIB MOHAMMED AL BALUSHI', '20190018734', '784201391716954', 'male', '5G'),



('AHMED MUFTAH FARAJ MUBARAK ALNUAIMI', '783569', '784201397983160', 'male', '5H'),
('HAMAD SULTAN DHBAYEB SALEM ALSHAMSI', '20190016222', '784201397107034', 'male', '5H'),
('HAMAD MOHAMMED ALI RUWAISHED ALNEYADI', '787315', '784201337925966', 'male', '5H'),
('HAMDAN SULTAN NEHAIL ABDULLA ALARYANI', '20210016434', '784201332506142', 'male', '5H'),
('HAMDAN MOHAMMED KHAMIS KHALFAN ALYAHYAEE', '788278', '784201326298433', 'male', '5H'),
('HAMDAN MOHAMMED MUBARAK SAIF AL KALBANI', '800871', '784201395248103', 'male', '5H'),
('ZAYED KHAMIS FARHAN EID ALNUAIMI', '783138', '784201241415021', 'male', '5H'),
('SALEM AHMED SALEM MOHAMMED ALNUAIMI', '785582', '784201352865733', 'male', '5H'),
('SALEM RASHED SAIF ALI AL NEYADI', '782184', '784201362519189', 'male', '5H'),
('SALEM SULTAN RASHED ALI AL AZEEZI', '782143', '784201352525071', 'male', '5H'),
('SULTAN KHALIFA AWAD SALEH ALWAHSHI', '785040', '784201336272741', 'male', '5H'),
('SULTAN ABDULLA RASHED MOHAMMED ALKALBANI', '782663', '784201394257311', 'male', '5H'),
('SUHAIL KHALED KHAMIS RASHED ALSAEDI', '793020', '784201327217135', 'male', '5H'),
('ABDULLA AHMED SALEM SULTAN ALSALMI', '789344', '784201337936039', 'male', '5H'),
('ABDALLAH HAMED SHAHIN WAJDAL ALBLOUSHI', '784236', '784201324796826', 'male', '5H'),
('ABDULLA HAMDAN ABDULLA HAMDAN AL SHAMSI', '784854', '784201330429354', 'male', '5H'),
('ABDULLA SALEM SAEED KHALFAN ALNUAIMI', '790949', '784201309572879', 'male', '5H'),
('ABDALLA MOHAMED SAEED MOHAMED TAHIR', '20210008638', '784201262692029', 'male', '5H'),

('ALI KHALFAN MOHAMMED MEERIN AL BLOOSHI', '786036', '784201379749027', 'male', '5H'),
('OMAR KHALIFA KHAMIS SALIM AL YAHYAEE', '783967', '784201381473616', 'male', '5H'),
('OMAR KASHOUN HAMAD HMOUD ALKTEBI', '785889', '784201316520721', 'male', '5H'),
('OMAR MUFTAH MUBARAK NASSIB AL NUAIMI', '784960', '784201360859181', 'male', '5H'),
('MANEA MUSABBEH MANEA MUSABBEH ALAZEEZI', '785801', '784201330207917', 'male', '5H'),
('MOHAMMED SAOUD MOHAMMED BAKHIT ALRASHDI', '786047', '784201304247519', 'male', '5H'),
('MOHAMMED AMER MOHAMMED MUSABBEH AL AZEEZI', '20190020631', '784201303828202', 'male', '5H'),
('MOHAMMED FAISAL ALI KHALFAN ALNUAIMI', '818576', '784201376427429', 'male', '5H'),

('MOHAMMED NASSER SAEED MUBARAK ALKETBI', '784818', '784201375363922', 'male', '5H'),
('MOHAMMED YOUSEF MASOUD QURAISH ALNUAIMI', '815873', '784201316043096', 'male', '5H'),
('MANSOOR HUMAID SALEM MLAIFI ALAZEEZI', '785535', '784201398170841', 'male', '5H'),
('NASSER JAMAL KHALIFA MOHAMMED AL MARBOUI', '794195', '784201319191488', 'male', '5H'),
('HAZZA IBRAHIM MARHOUN KHAMIS ALSAEDI', '783228', '784201340851761', 'male', '5H'),
('YOUSSIF AHMAD ALKHANOUS', '843330', '784201343510406', 'male', '5H'),



('BAKHIT HAMAD BAKHIT RASHED ALRASHDI', '869328055', '784200837213642', 'male', '11A1'),
('HAMED ABDALLAH SALIM AL SHAMSI', '609029', '784200709650947', 'male', '11A1'),
('RASHID NASSER JAMIL ALI AL QATBI', '570841', '784200725907586', 'male', '11A1'),
('SALEM SAIF ABDULLA KHALFAN AL AZEEZI', '189771', '784200757921505', 'male', '11A1'),
('SULTAN TALAL KHAMIS ALMARBOOEI', '609200', '784200886028263', 'male', '11A1'),
('SULAIMAN MOHAMMED SULAIMAN HAREB ALSHAMSI', '869350657', '784200782693608', 'male', '11A1'),
('SAIF MATTAR KHALFAN AL SHAMSI', '563928', '784200732524069', 'male', '11A1'),
('SAIF KHALID SAIF SALEM ALAZEEZI', '519071', '784200875942177', 'male', '11A1'),
('SAIF RASHED SAIF SAEED MURSHED ALMEQBAALI', '190925', '784200741647182', 'male', '11A1'),
('ABADALLAH KHALID ABADALLAH MUBARAK ALSENAANI', '316229', '784200714357256', 'male', '11A1'),
('OMAR AHMED AHMED AL HAMELI', '585152', '784200729682086', 'male', '11A1'),
('FAISAL SAEED SALEM JARWAN ALSHAMSI', '260217', '784200562481968', 'male', '11A1'),
('MUBARAK MOHAMMED SUBAIH RASHED AL RASHDI', '194194', '784200740408362', 'male', '11A1'),
('MOHAMMED KHAMIS SAIF KHAMIS ALKETBI', '571533', '784200691593659', 'male', '11A1'),
('MOHAMMED SAEED SALMEEN HAMAD RASHED AL NUAIMI', '618487', '784200759043761', 'male', '11A1'),
('MOHAMMED HELAL GHDAYER AL AJEED ALKETBI', '442136', '784200748183710', 'male', '11A1'),
('MANSOUR MOHAMMED TAMIM MOHAMMED AL KETBI', '189740', '784200724070741', 'male', '11A1'),
('NAHYAN NASSER HAMAD HELAL AL AMERI', '539352', '784200831753643', 'male', '11A1'),
('HAZZA AHMED HASAN SOURI', '194199', '784200779205259', 'male', '11A1'),
('HAZZA EID RUBAYEA SAEED ALSHAMSI', '192754', '784200717028185', 'male', '11A1'),
('YOUSEF WALEED SALEM ABDULLAH AL KENDI', '188897', '784200798151872', 'male', '11A1'),
('IBRAHIM ZAYED ALWAN ALI BAAZAB', '317747', '784200708738578', 'male', '11A2'),
('BADOR WAHEEB AHMAD', '530199', '784200735869743', 'male', '11A2'),
('HAMAD RASHED MUBARAK MOHAMMED ALMANSOORI', '256315', '784200706365036', 'male', '11A2'),
('HAMAD ALI ABDULLA SALEM AL NUAIMI', '317796', '784200717151839', 'male', '11A2'),
('HAMDAN NASSER ISMAIL ALZAROONI', '400303', '784200819358241', 'male', '11A2'),
('HAMDOUN KHAMIS KHALIFA HAMDOUN ALSHAMSI', '192768', '784200703647907', 'male', '11A2'),
('RASHED HAMED RASHED HAMED AL SAEDI', '444242', '784200749681845', 'male', '11A2'),
('RASHED NASSER RASHED SHAIBAN AL AHBABI', '193365', '784200785921766', 'male', '11A2'),
('SAEED MOHAMMED NASSER ALI AL HBABI', '405358', '784200881740219', 'male', '11A2'),
('SULTAN AHMED SALEM SAEED ALSAEDI', '150601', '784200631365820', 'male', '11A2'),
('SULTAN HAZZA SULTAN RASHED ALKAABI', '253178', '784200819491489', 'male', '11A2'),
('SAIF AHMED SAIF AL MUR ALNUAIMI', '191756', '784200879602520', 'male', '11A2'),
('ABDULLA SALEM SAEED KHAMIS ALKETBI', '189075', '784200775094285', 'male', '11A2'),
('ABDULLA SAWAYEH ALI SALEM ALKETBI', '257258', '784200782150799', 'male', '11A2'),
('ABDUALLA ABDULRAHMAN ABDULLA HUMAID ALGHAITHI', '308706', '784200724925290', 'male', '11A2'),
('ABDULLA MOHAMMED ALI RASHID ALNUAIMI', '191582', '784200736257492', 'male', '11A2'),
('MAYED ABDULLA HAMAD HAZZA ALNUAIMI', '197786', '784200750749382', 'male', '11A2'),
('MOHAMMED RASHED MUBARAK MOHAMMED ALMANSOORI', '256288', '784200760503050', 'male', '11A2'),
('YUOSIF SAAD ZAMEL NASSER ALAHBABI', '288564', '784200775163619', 'male', '11A2'),
('HAMAD KHALFAN SAEED MOHAMMED ALSHAMSI', '189360', '784200770854840', 'male', '11A3'),
('HAMDAN MUSALLAM SULTAN OBAID ALKETBI', '191695', '784200837475191', 'male', '11A3'),
('HAMDAN NASSER ALI MUSFER AL AHBABI', '191066', '784200769358159', 'male', '11A3'),
('KHALIFA HAMAD SAIF ABDULLA ALNUAIMI', '32108HQMC', '784200798246060', 'male', '11A3'),
('THEYAB RASHED ALI ALSALAF AL NUAIMI', '193507', '784200826876524', 'male', '11A3'),
('SAIF SALEM RASHED KHALFAN ALKETBI', '192149', '784200703527638', 'male', '11A3'),
('ABDULJALIL FAHAD ABDULJALIL ALI ALI ALSAAD', '430711', '784200814107189', 'male', '11A3'),
('ABDULLA KHALFAN SAEED MOHAMMED ALNEYADI', '194852', '784200842094870', 'male', '11A3'),
('ALI HUMAID FADHIL SAEED ALKETBI', '255617', '784200894183829', 'male', '11A3'),
('EISA MOHAMMED SALEM THAALOUB ALKETBI', '193135', '784200769528546', 'male', '11A3'),
('MOHAMMED AHMED ALI SAEED ALSHAMSI', '197206', '784200887373148', 'male', '11A3'),
('MOHAMMED SAEED ALI ALSALF ALNUAIMI', '192157', '784200832461055', 'male', '11A3'),
('MOHAMED ADEL RASHAD IBRAHIM', '398866', '784200841790692', 'male', '11A3'),
('MOHAMMED MUBARAK MOHAMMED MUBARAK AL KETBI', '20190021388', '784200896360268', 'male', '11A3'),
('NASSER MOHAMMED HUMAID NAYEA SALEM ALKETBI', '188957', '784200715930432', 'male', '11A3'),
('NAYEF GHALIB HUMAID RASHED AL WAHSHI', '442050', '784200706021803', 'male', '11A3'),
('AHMED ALI BLAISH ALI ALKETBI', '149687', '784200629697176', 'male', '11G1'),
('AHMED MANSOUR GHEDAYER ALEJAID ALKETBI', '442151', '784200798470801', 'male', '11G1'),
('AHMED NAYEF AWAD ALSABEA ALKETBI', '254891', '784200570615938', 'male', '11G1'),
('HAMAD SAEED SAIF RASHED', '152483', '784200705159315', 'male', '11G1'),
('HAMED MOHAMMED KHALFAN ALI AL NAAIMI', '193192', '784200836370575', 'male', '11G1'),
('HAMDAN MOHAMMED SAIF ALABED ALNUAIMI', '191857', '784200851036358', 'male', '11G1'),
('HAMDAN MOHAMMED MUSABBEH KHAMIS ALKETBI', '188703', '784200748168141', 'male', '11G1'),
('KHALIFA HAMAD KHALIFA ALTHEEB ALNUAIMI', '568008', '784200792438598', 'male', '11G1'),
('SALIM MOHAMMED SALIM ALKALBANI', '424488', '784200751795202', 'male', '11G1'),
('SALEM HAMAD SALEM THAALOUB', '193543', '784200759358151', 'male', '11G1'),
('SALEM ALI OBAID SALEM ALRASHDI', '189752', '784200726914169', 'male', '11G1'),
('SAEED SULTAN SAEED SALEM ALNUAIMI', '189756', '784200819419464', 'male', '11G1'),
('SAEED ALI ABDULLA MOHAMMED ALARYANI', '869365206', '784200757043524', 'male', '11G1'),
('SAIF HUMAID SALEM MOHAMMED ALNEYADI', '192790', '784200786207918', 'male', '11G1'),
('SAIF ALI SAAD ABDULLA ALARYANI', '20190021392', '784200717141871', 'male', '11G1'),
('SAIF MANSOUR QASEM GHULAM QASEM', '306114', '784200726954165', 'male', '11G1'),
('ABDULLA SAIF SALEM SHEMAIL ALRASHDI', '456017', '784200709215873', 'male', '11G1'),
('OBAID ALI OBAID SAEED ALKETBI', '444253', '784200763698378', 'male', '11G1'),
('MAYED SUHAIL AWAD ALHAIRI', '188708', '784200710579200', 'male', '11G1'),
('MUBARAK HUSSEIN HAMDAN AL BALUSHI', '569202', '784200781098403', 'male', '11G1'),
('MUBARAK NAYEF MUBARAK ALI ALAZEEZI', '255973', '784200893629434', 'male', '11G1'),
('MOHAMMED ANTAR ALI MOHAMMED ALREMEITHI', '307687', '784200627297136', 'male', '11G1'),
('MUSALLAM HASAN DHAFER HAMAD ALQAHTANI', '266663', '784200830241756', 'male', '11G1'),
('MANSOUR AHMED ALI MASOUD ALSAEDI', '192355', '784200737658607', 'male', '11G1'),
('MANSOOR ABDALLAH SAID HUMAID AL KAABI', '767255', '784200783080722', 'male', '11G1'),
('MANSOUR ALI MOHAMMED RASHED ALARYANI', '194373', '784200703086072', 'male', '11G1'),
('HUWAISHEL SULTAN HUWAISHEL HUMAID ALSHAMSI', '190669', '784200749364632', 'male', '11G1'),
('AHMED HAMDAN MOHAMMED HAMAD AL KTEBI', '424510', '784200763147905', 'male', '11G2'),
('AHMED SAEED ABDULLA MUSABBEH ALSHAMSI', '409173', '784200797202403', 'male', '11G2'),
('AHMED ALI MURAD ALI ALMAZAM', '152882', '784200617162910', 'male', '11G2'),
('HAMAD SAEED SALEM SAIF SAEED AL NAQBI', '189409', '784200717391310', 'male', '11G2'),
('HAMAD NASSER MOHAMMED BALABDA ALSHAMSI', '189202', '784200757327323', 'male', '11G2'),
('HAMDAN MOHAMMED RASHED MATAR ALNUAIMI', '192454', '784200854606595', 'male', '11G2'),
('HUMAID HAMAD OBAID SALEM ALRASHDI', '540052', '784200818461517', 'male', '11G2'),
('HUMAID ABDULLA MOHAMMED KHAMIS ALKAABI', '192107', '784200740806953', 'male', '11G2'),
('KHALED SAIF SAEED SAIF ALSHAMSI', '570836', '784200771384623', 'male', '11G2'),
('KHALIFA ALI RASHED SULTAN ALASHKHARI', '188986', '784200779540515', 'male', '11G2'),
('KHALIFA MOHAMMED KHALIFA RASHED ALWAHSHI', '289781', '784200836029270', 'male', '11G2'),
('RASHED ALABED ABDULLA SAEED ALEBRI', '193191', '784200718283722', 'male', '11G2'),
('SALIM DAGHISH OBAID SAID ALKALBANI', '308314', '784200615159652', 'male', '11G2'),
('SALEM ALI MUSABAH ABDULLA ALKAABI', '194256', '784200897042824', 'male', '11G2'),
('SALEM MOHAMMED SAEED RASHED AL NUAIMI', '308719', '784200752576973', 'male', '11G2'),
('SAOUD ALHUMAIDI HAMAD AL HUMAIDI AL KETBI', '191604', '784200798498182', 'male', '11G2'),
('SAUD KHALED MASAAOD AL AISAEE', '564842', '784200760908630', 'male', '11G2'),
('SAEED ABDULLA ALI ALSALF ALNUAIMI', '190740', '784200895179172', 'male', '11G2'),
('SULTAN MOHAMMED SULTAN NASSER AL MEQBAALI', '20190021438', '784200718280462', 'male', '11G2'),
('ABDULLA HAZZA ABDULLA SALEM ALSHAMSI', '606965', '784200839865753', 'male', '11G2'),
('AMMAR HELAL ALI KHALFAN ALNUAIMI', '190673', '784200751659580', 'male', '11G2'),
('MUBARAK ANWAR MUBARAK AL NAHDI', '190775', '784200848320816', 'male', '11G2'),
('MOHAMMED KHALED MOHAMMED KHALFAN ALKETBI', '189596', '784200770682688', 'male', '11G2'),
('MOHAMMED SAIF HAMAD ALBADI', '188734', '784199586315790', 'male', '11G2'),
('MANSOUR SALEM SAEED SAIF AL HASSANI', '444387', '784200839629365', 'male', '11G2'),
('MUHANAD SAEED RASHED SALEM ALSAEDI', '497607', '784200663690749', 'male', '11G2'),
('NAHYAN RASHED SAEED SAIF ALSHAMSI', '192711', '784200716907033', 'male', '11G2'),
('YOUSEF SALEM SAEED KHALFAN ALNUAIMI', '193268', '784200727582932', 'male', '11G2'),
('HAMAD ALI HMOUD SALEM ALSAEDI', '191637', '784200770624151', 'male', '11G3'),
('HAMAD QURAISH ABDULLA QURAISH', '256336', '784200781828767', 'male', '11G3'),
('HAMAD MUFTAH FARAJ MUBARAK ALNUAIMI', '304487', '784200850352814', 'male', '11G3'),
('DHIYAD HAMED KHAMIS AL SAADI', '188963', '784200757528177', 'male', '11G3'),
('THEYAB KHAMIS SALEM NASSIB AL NEYADI', '304548', '784200879687935', 'male', '11G3'),
('SALEM ABDULLA MOHAMMED SALEM ALKAABI', '409209', '784200761395316', 'male', '11G3'),
('SAEED HELAL OBAID MOHAMMED AL KAABI', '189509', '784200768598102', 'male', '11G3'),
('SULTAN HAMAD ALI MLAIFI ALAZEEZI', '197452', '784200762708756', 'male', '11G3'),
('AMER MUSABBEH OBAID ALI ALRASHDI', '444310', '784200879637930', 'male', '11G3'),
('ABDULLA SAIF ABDULLA ALI ALKALBANI', '190169', '784200805417134', 'male', '11G3'),
('ABDULLA ASHRAF ABDULLA HUMAID ALEBRI', '189478', '784200780980387', 'male', '11G3'),
('ABDULLA HUMAID SAIF KHAMIS ALKETBI', '316676', '784200757697204', 'male', '11G3'),
('ABDULLA SAEED SALEM ABDULLA AL NUAIMI', '190200', '784200748215405', 'male', '11G3'),
('ABDULLA MOHAMMED HAMAD SAEED ALKETBI', '444215', '784200680487384', 'male', '11G3'),
('ABDULLA MOHAMMED MUBARAK RUWAISHED ALNEYADI', '196973', '784200781368434', 'male', '11G3'),
('AMMAR YASIR MOHAMMED AL SHAMSI', '258225', '784200706365150', 'male', '11G3'),
('OMAR ABDULLA MARASH HADID ALKETBI', '405581', '784200853658704', 'male', '11G3'),
('FALAH HAMAD KHAMIS HAMAD ALSHAMSI', '254681', '784200716292162', 'male', '11G3'),
('MOHAMMED KHALED SALEM FADEL ALKETBI', '533321', '784200763615208', 'male', '11G3'),
('MOHAMMED SAEED MOHAMMED ALI ALSAEDI', '189906', '784200783279522', 'male', '11G3'),
('MOHAMMED SULAIMAN NASSER SULAIMAN ALSAEDI', '188619', '784200759350646', 'male', '11G3'),
('MOHAMMED ALI KHALIFA ALTHEEB', '191446', '784200737594042', 'male', '11G3'),
('MOHAMMED MUDHAFFAR MOHAMMED SAEED ALSHAMSI', '20190021437', '784200738768322', 'male', '11G3'),
('MOHAMMED NAJI MOHAMMED ALI ALKETBI', '571519', '784200825064247', 'male', '11G3'),
('NAHYAN SAOUD SAEED OBAID ALAZEEZI', '191602', '784200780637144', 'male', '11G3'),
('NAHIAN SUHAIL SAIF KHAMIS ALKETBI', '193722', '784200793579390', 'male', '11G3'),
('HAZZA SAEED MOHAMMED SAEED ALSAEDI', '189009', '784200780205975', 'male', '11G3'),
('HAREB WALEED HAREB ALRAEI ALKETBI', '192073', '784200857594095', 'male', '11G4'),
('HAMID AHMED JUMA AL GHAITHI', '502581', '784200735938142', 'male', '11G4'),
('HAMDAN MUBARAK SALEH MUBARAK ALNUAIMI', '190875', '784200716946080', 'male', '11G4'),
('HMOUD ABDULLA SLAYEM AYED AL KTEBI', '195985', '784200758148413', 'male', '11G4'),
('KHALED NASSER AHMED MSHARY ALSHAMSI', '835198', '784200731586978', 'male', '11G4'),
('KHAMIS HADI KHAMIS HADI MANEA AL AHBABI', '553785', '784200840374605', 'male', '11G4'),
('RASHID IBRAHIM RASHID ALBADI', '188971', '784200739532164', 'male', '11G4'),
('SALEM SAEED SALEM ABDULLA ALARYANI', '190823', '784200775043266', 'male', '11G4'),
('SALEM MOHAMMED SALEM SALUMA ALNUAIMI', '564797', '784200787372901', 'male', '11G4'),
('SAEED IBRAHIM JUMA ALI', '496551', '784200705814760', 'male', '11G4'),
('SAEED SULAIMAN SAEED ALI ALFARSI', '191220', '784200871021620', 'male', '11G4'),
('SULAIMAN MOHAMMED ALI SULAIMAN ALSAEDI', '188861', '784200786869253', 'male', '11G4'),
('SAIF SAEED MURAD ALI ALMAZAM', '191701', '784200783502915', 'male', '11G4'),
('ABDULRAHMAN SALEM OBAID GHUMAIL ALNUAIMI', '869392160', '784200876926047', 'male', '11G4'),
('ABDULAZIZ KHALID KHAMIS ABDULLA ALSHAMSI', '528283', '784200750764738', 'male', '11G4'),
('ABDULLA AHMED ABDULLA HUMAID ALGHAITHI', '308709', '784200686072818', 'male', '11G4'),
('ABDULLA SALEM ABDULLA SAEED ALNUAIMI', '443892', '784200729295855', 'male', '11G4'),
('ALI SULAIMAN MOHAMMED NASSER ALSHAMSI', '869376993', '784200818474189', 'male', '11G4'),
('GHANEM SAEED GHANEM ALI ALNUAIMI', '521537', '784200795105913', 'male', '11G4'),
('FAHED MOHAMMED RASHED SULIMAN ALBADI', '188680', '784200748153713', 'male', '11G4'),
('MANE SAEED SALEM SAEED ALSAEDI', '191707', '784200805925813', 'male', '11G4'),
('MUBARAK ALI NASSER ALI ALSAEDI', '191856', '784200864313737', 'male', '11G4'),
('MOHAMMED HAMDAN ABDULLAH ALSAEDI', '190083', '784200737985968', 'male', '11G4'),
('MOHAMMED SALEM ALGHABSHI MOHAMMED ALKETBI', '190315', '784200865304719', 'male', '11G4'),
('HAZZA KHALED MOHAMMED HAMAD ALSHAMSI', '191090', '784200732503253', 'male', '11G4'),
('YOUSIF ALI SAEED ALI ALMEQBAALI', '189489', '784200749831424', 'male', '11G4'),
('AHMED KHAMIS GHARIB MOHAMMED ALKUWAITI', '317897', '784200759215161', 'male', '11G5'),
('HMOUD HAMDAN RUBAYEA AL KETBI', '408070', '784200747042636', 'male', '11G5'),
('HMOUD KHALED MOHAMMED KHAMIS ALSHAMSI', '713169', '784200730794201', 'male', '11G5'),
('KHALED SAEED ABADALLA NASSER ALKAABI', '267861', '784200715498612', 'male', '11G5'),
('SALEM SULTAN DRAIBI ALI ALKETBI', '157501', '784200698291935', 'male', '11G5'),
('SALEM MATAR SALEM OBAID ALKTEBI', '190661', '784200821509179', 'male', '11G5'),
('SULTAN SAADOUN SAID AL AMRI', '568540', '784200741061749', 'male', '11G5'),
('SULTAN KHALED ALI MOHAMMED ALRASHEDI', '496429', '784200847462742', 'male', '11G5'),
('SULTAN MANSOUR AWAD MUBARAK ALNEYADI', '191474', '784200857204182', 'male', '11G5'),
('SUHAIL AHMED AWAD SAIF ALSAEDI', '570332', '784200748486824', 'male', '11G5'),
('SAIF AHMED SALEM MOHAMMED ALHASSANI', '496512', '784200727152686', 'male', '11G5'),
('ABDULRAHMAN ABDULLA YOUSEF AHMED ALBLOOSHI', '197210', '784200631860838', 'male', '11G5'),
('ABDULAZIZ NASSER MOHD SAEED MUSABBEH ALKAABI', '397659', '784200893680908', 'male', '11G5'),
('ABDULLA AHMED ALI MOHAMMED ALSAEDI', '189079', '784200752941748', 'male', '11G5'),
('ABDULLA KHALED MOHAMMED OBAID ALJABERI', '191045', '784200754072195', 'male', '11G5'),
('ABDULLA SAIF ALABED SALMEEN ALNUAIMI', '189342', '784200728080506', 'male', '11G5'),
('ABDULLA SHAIKHAN ALI ALAMERI ALAMERI', '188978', '784200765250657', 'male', '11G5'),
('ABDULLA ALI MOHAMMED HUWAIDEN ALKETBI', '258206', '784200790815029', 'male', '11G5'),
('OBAID SALEM KHALFAN RASHED ALNUAIMI', '191100', '784200765284102', 'male', '11G5'),
('GHANEM SALEM SAEED MUSALLEM ALMUHARRAMI', '258705', '784200765137318', 'male', '11G5'),
('FALLAH AHMED MATOUQ AL NAAIMI', '567078', '784200713063640', 'male', '11G5'),
('MUBARAK AHMED MOHAMMED MUBARAK ALKETBI', '190798', '784200880295975', 'male', '11G5'),
('MOHAMMED HAMDAN HUMAID RASHED ALAZEEZI', '190664', '784200765070931', 'male', '11G5'),
('MOHAMMED KHALIFA ABDULLA KHALFAN ALAZEEZI', '189816', '784200803549094', 'male', '11G5'),
('MOHAMMED SAEED MOHAMMED SAEED ALNUAIMI', '197737', '784200746495868', 'male', '11G5'),
('AHMED SAIF HAMAD KHAMIS ALKTEBI', '308195', '784200727246058', 'male', '11G6'),
('AHMED MOHAMED EBRAHEIM MOHAMED ALBLOOSHI', '194323', '784200725479867', 'male', '11G6'),
('HAMED ABDALLAH HAMDAN SAID AL ALAWI', '595106', '784200717461857', 'male', '11G6'),
('HAMAD SAEED HAMAD HMOUD ALKETBI', '444278', '784200827615855', 'male', '11G6'),
('HAMDAN ALI KHALFAN AL MARBOUAI', '20200018146', '784200794268159', 'male', '11G6'),
('HMOUD HAMDAN HAMAD MOHAMMED ALKETBI', '192354', '784200757214182', 'male', '11G6'),
('KHALED JUMA FAHED SALEM ALAZEEZI', '192239', '784200810372613', 'male', '11G6'),
('KHALFAN JUMA KHALFAN ALI ALSHAMSI', '177215', '784200746282852', 'male', '11G6'),
('KHALIFA SULTAN KHAMIS ZUHAIR ALKAABI', '317208', '784200817359621', 'male', '11G6'),
('RASHED SULTAN RASHED SULTAN ALKETBI', '190873', '784200721827309', 'male', '11G6'),
('SALEM HAMAD SALEM ALI ALKETBI', '190335', '784200896830716', 'male', '11G6'),
('SAOUD FAHED MUBARAK ALI ALAZEEZI', '258460', '784200727420208', 'male', '11G6'),
('SAEED THANI OBAID BELKEDAIDA ALFALASI', '596379', '784200718218710', 'male', '11G6'),
('SAEED SAIF ALI SAEED SHMAIL AL RASHEDI', '496557', '784200715463806', 'male', '11G6'),
('SAEED MUBARAK KHALFAN SAEED ALNEYADI', '189563', '784200746061496', 'male', '11G6'),
('SAEED MOHAMMED SAEED JUMA ALRASHDI', '306941', '784200682461965', 'male', '11G6'),
('SUHAIL MUTAB HUMAID SUHAIL ALMEQBAALI', '192429', '784200761381647', 'male', '11G6'),
('SUHAIL MOHAMMED SALEM MUBARAK ALKETBI', '188585', '784200715746150', 'male', '11G6'),
('AMER SALEM SAEED MOHAMMED ALNEYADI', '194850', '784200838718680', 'male', '11G6'),
('ABDULLAH KHALID ALSHADID TAEEB AL NAIMI', '593865', '784200736498708', 'male', '11G6'),
('ABDULLA KHAMIS SALEM SAEED ALSAEDI', '193918', '784200748025218', 'male', '11G6'),
('MOHAMMED KHALIFA ALI SAEED ALNUAIMI', '444385', '784200858765769', 'male', '11G6'),
('MOHAMMED SALEM HAMAD SALEM ALRASHDI', '869338100', '784200762198594', 'male', '11G6'),
('MOHAMMED SAEED MOHAMMED ALI ALRASHDI', '20200023702', '784200727062802', 'male', '11G6'),
('MOHAMMED ABDULLA AWAD MUBARAK ALNEYADI', '496533', '784200737270908', 'male', '11G6'),
('NASSER KHALED ABDULKAREM AL HEMYARI', '450464', '784200749807945', 'male', '11G6'),
('BADER KHALED ABDULLA QURAISH ALNUAIMI', '193729', '784200782928301', 'male', '11G7'),
('JUMA RASHED JUMA TANNAF ALNUAIMI', '165110', '784200618494189', 'male', '11G7'),
('HAMAD MOHAMMED OBAID SALEM ALRASHDI', '20200024399', '784200739181939', 'male', '11G7'),
('HAMDAN EISA MOHAMMED HMOUD HAMAD AL KETBI', '190311', '784200869062420', 'male', '11G7'),
('KHALAF AHMED MOHAMMED RASHED', '195819', '784200893025351', 'male', '11G7'),
('KHALIFA SULTAN ABDULLA SALEM SAEED AL ZAIDI', '188702', '784200797647243', 'male', '11G7'),
('KHALIFA FAISAL OMAR ABDULLA AL JAEEDI', '197741', '784200779291614', 'male', '11G7'),
('RASHED SULTAN RASHED MOHAMMED ALKETBI', '521084', '784200735873653', 'male', '11G7'),
('RAKAN NASSER BAKHIT HAMDAN ALAMERI', '193374', '784200786258242', 'male', '11G7'),
('ZAYED SAEED HAMAD SAEED ALSHAMSI', '409531', '784200886160462', 'male', '11G7'),
('SALEM ALI SALEM RASHED AL KETBI', '264949', '784200839387923', 'male', '11G7'),
('SAEED SULTAN HAMAD SAEED ALRASHDI', '869385958', '784200738658267', 'male', '11G7'),
('SULAIMAN KHAMIS SULAIMAN MUSABBEH ALSHAMSI', '192785', '784200881360984', 'male', '11G7'),
('SAIF SALIM KHALFAN SALIM ALHEBSI', '571906', '784200859381848', 'male', '11G7'),
('ABDULLAH RASHED ABDULLA RASHED AL NUAIMI', '192451', '784200779607280', 'male', '11G7'),
('ABDULRAHMAN MUSABBEH MATAR SAIF ALNEYADI', '190672', '784200839827613', 'male', '11G7'),
('ABDULLA BUTI SAIF SEBAA ALKETBI', '260688', '784200840847519', 'male', '11G7'),
('ABDULLA KHALED ALI KHARBASH ALSAEDI', '256337', '784200704361490', 'male', '11G7'),
('ABDALLAH SALIM ALI SALIM ALORAIMI', '496541', '784200782657389', 'male', '11G7'),
('ALI SAEED ALI SAEED ALMEQBAALI', '192043', '784200798242630', 'male', '11G7'),
('OMAR AHMED SAEED ALI AL SHAMSI', '20200022577', '784200724282064', 'male', '11G7'),
('AWAD MOHAMMED AWAD SAEED ALNUAIMI', '189956', '784200784903583', 'male', '11G7'),
('MANSOOR ALI MATOUQ AL NAAIMI', '818842', '784200828526200', 'male', '11G7'),
('NAYEF RASHED KHAMIS SULAIMAN ALSHAMSI', '196135', '784200732469547', 'male', '11G7'),
('AL THEEB YOUSEF AL THEEB MOHAMMED SALEM AL KETBI', '172571', '784200669498501', 'male', '12A1'),
('AL MUR SAEED KHALIFA AL MUR ALNEYADI', '444452', '784200696381985', 'male', '12A1'),
('BADER MUSABBEH SAEED SALEM ALSAEDI', '20200019844', '784200661586287', 'male', '12A1'),
('HAMDAN MOHAMMED RASHED HAMAD AL SHAMISI', '151851', '784200691646531', 'male', '12A1'),
('ZAYED SAEED ZAID ALKHANBOULI', '151889', '784200730928379', 'male', '12A1'),
('SALEM SAOUD MOHAMMED JUMA ALRASHDI', '441692', '784200754617247', 'male', '12A1'),
('SALEM HELAL SALEM KHALFAN', '149659', '784200615951363', 'male', '12A1'),
('SAIF NASSER ALI MESFER AL AHBABI', '151069', '784200674192958', 'male', '12A1'),
('ABDUL AZIZ RASHED AMER MOHAMMED AMER AL KHANBASHI', '152301', '784200608149140', 'male', '12A1'),
('ABDULLA AHMED HAMAD SHEMAIL ALRASHDI', '869353416', '784200725718215', 'male', '12A1'),
('ABDULLA HAMAD BAKHIT RASHED BAKHIT AL RASHEDI', '306491', '784200638593580', 'male', '12A1'),
('OBAID AHMED OBAID SALIM ALKAABI', '318010', '784200628163519', 'male', '12A1'),
('MANEA MOHAMMED NASSER ALI AL AHBABI', '174152', '784200609026438', 'male', '12A1'),
('MOHAMMED IBRAHIM ABDULLA IBRAHIM ALDHAHERI', '187756', '784200626285462', 'male', '12A1'),
('MOHAMMED AHMED KHAMIS SALEM ALMEQBAALI', '20200013670', '784200682643943', 'male', '12A1'),
('MOHAMMED KHALED SALEM SAEED ALMEQBAALI', '165137', '784200683640641', 'male', '12A1'),
('MOHAMMED ABDULRAHMAN KHAMIS MOHAMMED ALNEYADI', '177237', '784200790574030', 'male', '12A1'),
('MANSOUR FADEL MOHAMMED OBAID AL SHAMISI', '151082', '784200525414643', 'male', '12A1'),
('MANSOUR HELAL GHDAYER HAMAD ALDEREI', '197222', '784200780207195', 'male', '12A1'),
('HAZZA SULTAN AL JAUAAN SALEM AL SHAMISI', '153137', '784200697474185', 'male', '12A1'),
('ALTHEEB MOHAMEED SALEM MOHAMMED AL MEQBALI', '193178', '784200681830806', 'male', '12A2'),
('HAREB MOHAMMED SAEED ALI AL SHAMISI', '152504', '784200695970655', 'male', '12A2'),
('HAMED ABDULLA ALI SULTAN ALKAABI', '148007', '784200603627272', 'male', '12A2'),
('HAMAD AHMED MOHAMMED SARHAN SALEM AL TAMEEMI', '149696', '784200626136541', 'male', '12A2'),
('HAMDAN HMOUD SALEM SAEED ALMEQBAALI', '165136', '784200660398288', 'male', '12A2'),
('HAMDAN MOHAMMED OBAID SALEM ALI AL NEYADI', '150461', '784200775020736', 'male', '12A2'),
('ZAYAD KHALED RASHED MATAR SAEED AL NUAIMI', '147392', '784200694793769', 'male', '12A2'),
('SALEM KHALIFA AMER KHAMIS ALNUAIMI', '869327345', '784200668731688', 'male', '12A2'),
('SAOUD MOHAMMED SALEM NASSER ALNUAIMI', '153456', '784200691394058', 'male', '12A2'),
('SAOUD MOHAMMED AWAD OBAID ALNUAIMI', '177224', '784200604097616', 'male', '12A2'),
('SAEED MOHAMMED SAEED HAMAD AL NUAIMI', '496114', '784200636079277', 'male', '12A2'),
('SULTAN JUMA MOHAMMED ALI ALRASHDI', '20200027542', '784200602174292', 'male', '12A2'),
('ALI HAMAD RASHED HAMED AL SAEDI', '306976', '784200628285411', 'male', '12A2'),
('MUBARAK HAMAD KHALFAN JUMAIE AL YAHYAEI', '147222', '784200693031872', 'male', '12A2'),
('MOHAMMED RASHID MOHAMMED RASHID AL MANAI', '441790', '784200665321988', 'male', '12A2'),
('MOHAMMED SALEM BUTI ALEBRI', '168728', '784200720610656', 'male', '12A2'),
('MOHAMMED TALAL MUSALLEM SALEM ALSEYABI', '165802', '784200720705902', 'male', '12A2'),
('MOHAMMED ABDULLA MOHAMMED AL SHAMISI', '167936', '784200779654613', 'male', '12A2'),
('HAZZA ABDULLA RASHED MOHAMMED ALKALBANI', '20190021387', '784200605161718', 'male', '12A2'),
('AHMED SALEM RASHED SAEED ALKAABI', '157243', '784200665814321', 'male', '12G1'),
('BUTI SULTAN SAEED BUTI AL KETBI', '173103', '784200738652484', 'male', '12G1'),
('HASSAN SAIF KHAMIS MUHANNA ALHASSANI', '722686', '784200762031878', 'male', '12G1'),
('HAMAD MOHAMMED SALEM ALI AL SHAMISI', '151061', '784200680493242', 'male', '12G1'),
('HAMAD NAYEF HAMAD DAEN ALRASHDI', '20190021389', '784200785249259', 'male', '12G1'),
('KHALED SALEM HAMAD SAEED KHUWAIDEM AL KETBI', '152446', '784200685190611', 'male', '12G1'),
('RASHED SULTAN ALI SAEED AL NUAIMI', '152775', '784200794075851', 'male', '12G1'),
('RASHED OBAID RASHED ALI RASHED AL MUQBALI', '175927', '784200686983089', 'male', '12G1'),
('RASHED ABDULLA MOHAMMED HMOUD ALKALBANI', '869362644', '784200637108745', 'male', '12G1'),
('SALEM RASHED BAKHIT SHMAIL DAEN AL RASHEDI', '152212', '784200713609103', 'male', '12G1'),
('SAEED HUMAID FADEL SAEED ALKETBI', '152334', '784200626165862', 'male', '12G1'),
('SULTAN AHMED ABDUL KHALEQ SAIF AHMED ABDUL RAB', '168439', '784200631742424', 'male', '12G1'),
('SAIF MATAAB HUMAID ALMEQBAALI', '444118', '784200563736279', 'male', '12G1'),
('ABDULLA KHALFAN SAEED MOHAMMED ALNEYADI', '451284', '784200630921516', 'male', '12G1'),
('ABDULLA ALI RASHED ALI ALKETBI', '152198', '784200738579653', 'male', '12G1'),
('ABDULLA MOHAMMED RUBEEA MATAR AL KETBI', '165790', '784200625498215', 'male', '12G1'),
('ALI MUSABBEH SAEED AYED AL KETBI', '151916', '784200716416191', 'male', '12G1'),
('OMAER SULTAN SUWAIDAN MOHAMMED SAEED AL MEQBALI', '176773', '784200770249868', 'male', '12G1'),
('AWAD MANSOUR AWAD MUBARAK ALNEYADI', '20200018203', '784200662969292', 'male', '12G1'),
('MAYED SAEED OBAID SAEED BAKHIT AL RASHEDI', '484136', '784200775472028', 'male', '12G1'),
('MOHAMMED SULTAN SALEM HAMAD AL KETBI', '167416', '784200742437575', 'male', '12G1'),
('MOHAMMED ABDALLAH HUMAID SUHAIL ALMEQBAALI', '444121', '784200503970947', 'male', '12G1'),
('MOHAMMED YOUSEF MOHAMMED SALEH ALKAABI', '165099', '784200646053072', 'male', '12G1'),
('MANSOOR ABDULLAH ALI MOHAMMED ALSAEDI', '150678', '784200674961089', 'male', '12G1'),
('MANSOUR ALI RASHED SULTAN ALKETBI', '149650', '784200603204916', 'male', '12G1'),
('HADAF SAEED HADEF MOHAMMED AL NUAIMI', '147397', '784200614306981', 'male', '12G1'),
('HAZZA SULTAN GHDAYER MUSABBEH BUTI AL KETBI', '151795', '784200663060356', 'male', '12G1'),
('BUTI AHMAD BUTI MUSABBEH BUTI AL KETBI', '165103', '784200785831684', 'male', '12G2'),
('HAMDAN HMOUD SALEM OBAID GHANEM AL KETBI', '153439', '784200725108540', 'male', '12G2'),
('HMOUD RASHED HMOUDA MUSABBEH AL KITBI', '151559', '784200686540707', 'male', '12G2'),
('HMOUD SAEED SAIF SAEED AL RUMAITHI', '149775', '784200710973155', 'male', '12G2'),
('KHALIFA SUHAIL MOHAMMED ALI SEED AL SHAMISI', '165351', '784200664308309', 'male', '12G2'),
('RASHED SALEM AL AZIZI', '146560', '784200673736581', 'male', '12G2'),
('RASHED ABDULLA AWAD MUBARAK ALNEYADI', '496146', '784200662079761', 'male', '12G2'),
('RASHED MOHAMMED RASHED MUBARAK AL AKETBI', '315978', '784200626252199', 'male', '12G2'),
('RASHED MOHAMMED ABDULLA ALNUAIMI', '49999', '784200524838305', 'male', '12G2'),
('ZAYED FAISAL OMAR ABDULLA AL JAEEDI', '197233', '784200640909873', 'male', '12G2'),
('SALIM HAMED SALIM HAMED AL RASHDI', '316740', '784200797387022', 'male', '12G2'),
('SAEED MUADED HUWAIDEN THAIBAN ALKETBI', '466806', '784200637495936', 'male', '12G2'),
('SULTAN SALEM MUSABBEH SAEED AL KETBI', '151876', '784200680205315', 'male', '12G2'),
('SULTAN SAIF MOHAMMED KHALFAN ALSHAMSI', '174990', '784200705060984', 'male', '12G2'),
('SAIF RASHED MOHAMMED SALEM ALKETBI', '194756', '784200716135734', 'male', '12G2'),
('ABDULRAHMAN ABDULLA AHMED MOHAMMED ALNUAIMI', '61173', '784200575969462', 'male', '12G2'),
('ABDULLA JASEM ABDULLA HAMDAN ALSHAMSI', '484116', '784200681042089', 'male', '12G2'),
('ABDULLA MOHAMMED OBAID SALEM AL RASHDI', '452477', '784200684918699', 'male', '12G2'),
('ALI AHMED ALI SAEED ALKAABI', '245160', '784200642130643', 'male', '12G2'),
('ALI AHMED HUWAIDEN THAIBAN AL KETBI', '147450', '784200698320627', 'male', '12G2'),
('MUBARAK MOHAMMED MUBARAK SUWAID RASHED AL KETBI', '442145', '784200683059438', 'male', '12G2'),
('MOHAMMED HAMDAN HUWAIDEN THAIBAN ALKETBI', '444197', '784200713148425', 'male', '12G2'),
('MOHAMMED ABDULLA SALEM ALKETBI', '49992', '784200582963920', 'male', '12G2'),
('MOHAMEED ABDULLA MARASH HADID ALKETBI', '318220', '784200626402604', 'male', '12G2'),
('MOHAMMED MUSABBEH OBAID ALI ALRASHDI', '869395149', '784200604805174', 'male', '12G2'),
('MANSOUR KHALED ALI MOHAMMED AL RASHEDI', '496204', '784200669515205', 'male', '12G2'),
('MANSOUR NOKHAIRA ABDULLA ALSAEDI', '149323', '784200619385055', 'male', '12G2'),
('AHMED SALEM MOHAMMED AHMED SAEED', '17397', '784200546535954', 'male', '12G3'),
('HAMAD HUMAID ALI MOHAMMED ALKHATERI', '28141', '784200582626162', 'male', '12G3'),
('HAMAD SULTAN SAAD ABDULLA ALARYANI', '20190046299', '784200673616254', 'male', '12G3'),
('HAMAD SULTAN ALI MOHAMMED ALNEYADI', '173095', '784200757387269', 'male', '12G3'),
('KHALED KHAMIS RASHED OBAID RASHED AL GHAITHI', '192018', '784200797903190', 'male', '12G3'),
('KHALIFA KHALED SAEED ALI AL EISAEI', '484106', '784200660390434', 'male', '12G3'),
('KHALIFA KHALED SALEM KHALED SALEM AL KETBI', '147739', '784200652864909', 'male', '12G3'),
('RASHED AHMED SAEED ALI ALMEQBAALI', '149677', '784200749518187', 'male', '12G3'),
('SAID KHALID SAID AL HARTHI', '154722', '784200516574876', 'male', '12G3'),
('SAEED JUMA SALEM JUMA ALKAABI', '151417', '784200659758070', 'male', '12G3'),
('SAEED HAITHAM SAEED HUWAIDEN ALKETBI', '175791', '784200616549612', 'male', '12G3'),
('SULTAN HAMAD SAEED HUWAIDEN THAIBAN AL KETBI', '165621', '784200769139724', 'male', '12G3'),
('TALAL BADAR YAQOOB AL AMRI', '189620', '784200629505395', 'male', '12G3'),
('OBAID ABDULLA OBAID ABDULLA ALBLOOSHI', '165358', '784200791694696', 'male', '12G3'),
('ALI SAIF AL ABED SALMEEN ALNUAIMI', '153575', '784200665815286', 'male', '12G3'),
('ALI MUBARAK ALI MELAIFI AL AZEEZI', '146551', '784200615904396', 'male', '12G3'),
('OMAR MOHAMMED ALTHEEB SAEED GHUMAIL AL NUAIMI', '150232', '784200647982980', 'male', '12G3'),
('EISA AHMED MUTAEB SAEED AL KETBI', '149617', '784200653283612', 'male', '12G3'),
('MOHAMMED BUTI SALEM MOHAMMED AYED AL KTEBI', '258216', '784200686243070', 'male', '12G3'),
('MOHAMMED KHALIFA SAEED ALKAABI', '165567', '784200739359519', 'male', '12G3'),
('MOHAMMED RASHED MOHAMMED SAIF ALKETBI', '151842', '784200665324719', 'male', '12G3'),
('MOHAMMED SALEM KHAMIS SLAYEM ALKETBI', '165105', '784200610390203', 'male', '12G3'),
('MOHAMMED SALEM ABDULLA MOHAMMED ALKAABI', '168397', '784200592729030', 'male', '12G3'),
('MOHAMMED SAEED MOHAMMED MUSALLLEM AL YAHYAEI', '151713', '784200658619737', 'male', '12G3'),
('MOHAMMED AZIZ MOHAMMED ALSHAMSI', '455821', '784200652693712', 'male', '12G3'),
('HAZZA SALEM HUMAID RASHED AL AZIZI', '150414', '784200741047516', 'male', '12G3'),
('HAZZA SAEED MELFI ALI ALKETBI', '146559', '784200692109463', 'male', '12G3'),
('AHMED GHANEM ALI GHANEM AL NUAIMI', '193712', '784200662730272', 'male', '12G4'),
('AHMED NASSER ALI HAMAD ALNUAIMI', '166620', '784200604210300', 'male', '12G4'),
('HAMAD KHALFAN ABDULLA SULTAN AL SHAMISI', '153239', '784200605416872', 'male', '12G4'),
('HAMAD MOHAMMED HASAN RASHED HASN ALNUAIMI', '429582', '784200602958793', 'male', '12G4'),
('KHALED ABDULLA HAREB ABDULLA AL SHAMISI', '175915', '784200660358399', 'male', '12G4'),
('KHALED ABDULLA AWAD AZIZ ABDULLA AL KETBI', '154628', '784200625987373', 'male', '12G4'),
('RASHED ABDULLA MOHAMMED SALEM ALKETBI', '252478', '784200553648708', 'male', '12G4'),
('SALEM RASHED SALEM MOHAMMED ALHANAEE', '195942', '784200720269180', 'male', '12G4'),
('SALEM AIL SAEED KHAMIS AL KETBI', '151056', '784200625020944', 'male', '12G4'),
('SAOUD AWAD KHAMIS SAEED ALSHAMSI', '151410', '784200624761837', 'male', '12G4'),
('ABDUL RAHMAN ALI MOHAMMED SAEED ALSAEDI', '150219', '784200774152951', 'male', '12G4'),
('ABDULLA RASHED ABDULLA SALEM ALNUAIMI', '151879', '784200609274293', 'male', '12G4'),
('ABDULLA ALI AWAD MOHAMMED AL AHBABI', '153424', '784200516524723', 'male', '12G4'),
('ABDULLA ALI MOHAMMED SAEED ALSAEDI', '150231', '784200765250855', 'male', '12G4'),
('OBAID HELAL OBAID SAEED ALRASHDI', '242693', '784200692086083', 'male', '12G4'),
('ALI KHAMIS JUMA FARHAN AL FALAHI', '174047', '784200736463199', 'male', '12G4'),
('ALI GHDAYER ALI SAEED TUWAIRESH AL KETBI', '444355', '784200741625204', 'male', '12G4'),
('ALI KHALFAN ALI ALALAWI', '304923', '784200738485166', 'male', '12G4'),
('AMAR SALEM ALI KHAMIS ALKAABI', '253915', '784200703254910', 'male', '12G4'),
('OMAR SAIF SAEED KALFOUT AL SHAMISI', '152870', '784200687062859', 'male', '12G4'),
('MUBARAK GHABESH OBAID GHUMAIL ALNUAIMI', '150303', '784200606808283', 'male', '12G4'),
('MOHAMMED AHMED ALI EISA AL KETBI', '151924', '784200685943902', 'male', '12G4'),
('MUHAMMAD ALSHAMSI', '20230021897', '784200417802665', 'male', '12G4'),
('MOHMMED KHALED KHAMIS ABDULLA ALSHAMSI', '451810', '784200536065301', 'male', '12G4'),
('MOHAMMED SALEM MOHAMMED MUSABBEH ALAZEEZI', '157521', '784200743060319', 'male', '12G4'),
('MOHAMMED ALI NASSER HAREB ABDULLA AL SHAMISI', '156176', '784200708290646', 'male', '12G4'),
('MOHAMMED EISA MOHAMMED HMOUD ALKETBI', '147293', '784200671830428', 'male', '12G4'),
('MOHAMMED NASSER AL JAWAAN SALEM AL SHAMISI', '174437', '784200795051653', 'male', '12G4'),
('MANSOUR HAMAD ABDULLA KHAMIS ALKAABI', '156216', '784200664146311', 'male', '12G4'),
('HAZZA SAEED SALEM SAIF SALEM RASHED AL SHAMISI', '150697', '784200654258415', 'male', '12G4'),
('HAZZA MUSALLEM MASOUD QURAISH ALNUAIMI', '489217', '784200638713964', 'male', '12G4'),
('AHMED MOHAMMED SAEED SAIF ABBOUD AL SHAMISI', '165552', '784200617046410', 'male', '12G5'),
('AHMED MOHAMMED SALEH HAMAD AHMED AL ALAWI', '147652', '784200681850861', 'male', '12G5'),
('BATI TANAF MUBARAK TANAFA ALNUAIMI', '192364', '784200672903943', 'male', '12G5'),
('HAMAD JUMAA YOUSEF IBRAHEEM ALSENAANI', '168443', '784200625865181', 'male', '12G5'),
('HAMAD SALEM ABDULLA JUMA ALRASHDI', '869370715', '784200684861931', 'male', '12G5'),
('KHAED MOHAMMED HADEED MUFTAH HADEED AL SHAMISI', '151391', '784200779315801', 'male', '12G5'),
('THEYAB ALI SLAYEM MUBARAK ALNUAIMI', '869357190', '784200662647211', 'male', '12G5'),
('SALEM SAEED MOHAMMED SULTAN ALKAABI', '497713', '784200636920603', 'male', '12G5'),
('SAOUD SUBAIH ABDULLA SUBAIH ALKAABI', '151848', '784200660910694', 'male', '12G5'),
('SAEED ABDULLA SAEED SALEM ALNUAIMI', '401784', '784200531638102', 'male', '12G5'),
('SAEED ALI SALEM ALI ALSHAMSI', '152688', '784200797592936', 'male', '12G5'),
('SULTAN ABDULLA SAEED MUSABBEH SAIF AL NUAIMI', '496200', '784200710397421', 'male', '12G5'),
('SULAIMAN SALEM SAEED HUMAID ALSAEDI', '156054', '784200698721469', 'male', '12G5'),
('ABDULLA SALEM KHALFAN AL SHAMISI', '308385', '784200664039094', 'male', '12G5'),
('ABDULLA SAIF ALI AL SAEED', '147366', '784200715306252', 'male', '12G5'),
('ABDULLA AWADH MUBARAK SAEED ALSAEDI', '152476', '784200761476587', 'male', '12G5'),
('ALI SALEM JUMA NASSER AL MANTHARI', '175898', '784200780547962', 'male', '12G5'),
('ALI MOHAMMED HAMAD ALSALF ALNUAIMI', '307797', '784200748273503', 'male', '12G5'),
('ALI NASSER ALI BLAISH ALIEID AL KETBI', '151255', '784200619580838', 'male', '12G5'),
('FAYYAD SAEED KHALFAN MUSABBEH ALSHAMSI', '472654', '784200684039736', 'male', '12G5'),
('FAISAL AHMED ALI JUMA AL RASHDI', '444208', '784200746471075', 'male', '12G5'),
('MANEA MOHAMMED MANEA MUSABBEH AL AZIZI', '152579', '784200775732546', 'male', '12G5'),
('MUBARAK MUFTAH MUBARAK TANNAF ALNUAIMI', '20210014551', '784200697029401', 'male', '12G5'),
('MOHAMMED SEHMI MOHAMMED HUSAIN AL AHBABI', '147876', '784200636137612', 'male', '12G5'),
('MOHAMMED MATAR HAMAD MOHAMMED M QRAIN AL KETBI', '152546', '784200614160487', 'male', '12G5'),
('MOHAMMED NASSER MOHAMMED NASSER MOHAMMED AL NASSER', '152319', '784200613919073', 'male', '12G5'),
('MANSOUR SULTAN SALEM MOHAMMED SHKAIL AL NUAIMI', '156254', '784200702468388', 'male', '12G5'),
('NASSER ALI ABOOD HUMAID AL DARII', '307289', '784200619163932', 'male', '12G5'),
('HAZZA HAMAD MOHAMMED SAEED ALSAEDI', '165175', '784200621950243', 'male', '12G5'),
('AHMED RASHED SAEED MOHAMMED NHAIL', '20190026685', '784200525963706', 'male', '12G6'),
('AHMAD SAEED ISMAIL SAEED AL KETBI', '152317', '784200609413263', 'male', '12G6'),
('HAMDAN SAEED HAMDAN SAEED ALI AL SAEDI', '153199', '784200698724687', 'male', '12G6'),
('HUMAID RASHED MUSABBEH SAEED AL KETBI', '152218', '784200792064139', 'male', '12G6'),
('SALEM MUBARAK SAIF ALKTEBI', '193532', '784200786420263', 'male', '12G6'),
('SAOUD HAMAD HUWAISHEL HUMAID ALSHAMSI', '189818', '784200765937204', 'male', '12G6'),
('SAEED KHALIFA MOHAMMED KHALIFA ALI AL KETBI', '147727', '784200774617052', 'male', '12G6'),
('SAEED KHAMIS SAEED AL YAHYAEI', '283526', '784200754386173', 'male', '12G6'),
('SULTAN KHALED KHALFAN MOHAMMED ALARYANI', '484230', '784200624949739', 'male', '12G6'),
('SULTAN SALEM ALGHABSHI MOHAMMED ALKTEBI', '152390', '784200685074062', 'male', '12G6'),
('SUHAIL JUMA HASSAN JUMA ALKAABI', '524835', '784200671809695', 'male', '12G6'),
('SUHAIL ALI SAIF ALI AL MEZAINI', '153144', '784200648587408', 'male', '12G6'),
('SUHAIL MOHAMMED SUHAIL ALI AL NUAIMI', '150722', '784200620541704', 'male', '12G6'),
('SAIF SAQER SAIF SAEED SAIF ALRUMAITHI', '149532', '784200692064270', 'male', '12G6'),
('SHEHAB ABDULLA RASHED ABDULLA ALNUAIMI', '151454', '784200668606849', 'male', '12G6'),
('ABDULAZIZ RASHED KHALFAN ALI ALSHAMSI', '157405', '784200665103212', 'male', '12G6'),
('ABDULLA KHALIFA KHAMIS SALEM ALYAHYAEE', '155145', '784200657374904', 'male', '12G6'),
('ABDULLA SAEED RASHED HUMAID ALSENAANI', '156340', '784200605850856', 'male', '12G6'),
('ABDULLA MUSBBEH SULTAN RASHED ALKETBI', '165708', '784200604957637', 'male', '12G6'),
('OBAID HASAN DHAFER HAMAD ALQAHTANI', '256346', '784200715043285', 'male', '12G6'),
('ALI SALEM ALI RASHED ALSAEDI', '150246', '784200610742635', 'male', '12G6'),
('MOHAMMED SAID MUSABAH AL QATABI', '302837', '784200698598412', 'male', '12G6'),
('MOHAMMED KHALED ABDULLA MUBARAK ALYAHYAEE', '165657', '784200665850754', 'male', '12G6'),
('MOHAMMED KHALED OBAID ABDULLA ALKETBI', '152042', '784200748280581', 'male', '12G6'),
('MOHAMMED KHALIFA NASSER MOHAMMED NASSER AL ABDUL SALAM', '150442', '784200605426814', 'male', '12G6'),
('MOHAMMED AMER MOHAMMED AMER ALSHAMSI', '256291', '784200538651710', 'male', '12G6'),
('MOHAMMED GHEADAYER MUSABBEH BUTI AL KETBI', '151726', '784200651376871', 'male', '12G6'),
('MANSOUR ALI ABDULLA ALI ALKALBANI', '149639', '784200713085270', 'male', '12G6'),
('HAZZA MANEA MESFER MANEA MOHAMEED AL AHBABI', '153268', '784200640464879', 'male', '12G6'),
('AHMED SULTAN HAMED AL SALF ALNUAIMI', '304333', '784200681463616', 'male', '12G7'),
('BAKHIT ABDULLA BAKHIT ALI ALKETBI', '17436', '784200586517060', 'male', '12G7'),
('HUSSEIN MOHAMMED MURAD AL BALUSHI', '157073', '784200664964648', 'male', '12G7'),
('HAMAD AHMED MOHAMMED SALLEH AL NUAIMI', '165624', '784200709203531', 'male', '12G7'),
('HAMAD KHALFAN HUMAID KHALFAN ALNUAIMI', '165877', '784200660859610', 'male', '12G7'),
('KHALED HAMAD SALEM ALI ALKETBI', '147735', '784200665854327', 'male', '12G7'),
('KHALED SAEED HUMAID SUHAIL ALMEQBAALI', '189290', '784200520790476', 'male', '12G7'),
('KHALED ALI SAEED SAIF AL SHAMISI', '255494', '784200679504389', 'male', '12G7'),
('KHALIFA JUMA YAQOUB SAEED AL WAHSHI', '444485', '784200648084299', 'male', '12G7'),
('RASHED SAEED RASHED SALEM ALSAEDI', '486504', '784200737262483', 'male', '12G7'),
('RASHID SHAFA MOHAMED SALEH ABDALLA', '193147', '784200603846492', 'male', '12G7'),
('ZAYED KHALIFA SALEM AL SAEDI', '147631', '784200609036163', 'male', '12G7'),
('ZAYED ALI NASSER ALI NASSER AL SAEDI', '157510', '784200648406823', 'male', '12G7'),
('SAEED SALEH KHAMIS RASHED SAIF AL KALBANI', '147527', '784200652549070', 'male', '12G7'),
('SAEED ABDULLA SAIF KHAMIS ALKETBI', '192363', '784200597307352', 'male', '12G7'),
('SAEED YASER SAEED NASSER ALSHAMSI', '424861', '784200769690353', 'male', '12G7'),
('SAIF KHALIFA MOHAMMED SALEM AL NUAIMI', '315986', '784200660242940', 'male', '12G7'),
('ABDUL RAHMAN RAHMAN SAEED MUSABBEH AL MEQBALI', '156067', '784200658021769', 'male', '12G7'),
('ABDUL AZIZ KHAMIS JUMA SALIM AL GHAITHI', '444114', '784200704874872', 'male', '12G7'),
('OBAID SAIF MATAR OBAID ALNUAIMI', '192911', '784200531836169', 'male', '12G7'),
('AZAYEZ MOHAMMED SAEED GEDAD AL MUHARRAMI', '250419', '784200593802950', 'male', '12G7'),
('OMER SAID MOHAMMED AL KAABI', '20220010778', '784200666145303', 'male', '12G7'),
('FAISAL SAEED SALMEEN SAEED ALNUAIMI', '150419', '784200759573577', 'male', '12G7'),
('MOHAMMED AHMED SAIF EID AL KETBI', '408897', '784200658583925', 'male', '12G7'),
('MOHAMMED MUADED RASHED ALI EID AL KETBI', '153021', '784200696298536', 'male', '12G7'),
('MANSOUR MOHAMMED RASHED AL BADI', '28177', '784200607307020', 'male', '12G7'),
('MUHAYER ALI MUHAYER MUBARAK ALKETBI', '190670', '784200754248415', 'male', '12G7'),
('NASSER ABDULLAH SAIF KHAMIS ALKETBI', '401013', '784200696203585', 'male', '12G7'),
('HAZZA AHMED SALEM MUBARAK ALKTEBI', '156138', '784200643815762', 'male', '12G7'),
('HAZAA DAWOOD SULAIMAN KHALFAN AL KALBANI', '308442', '784200627541590', 'male', '12G7')
]


def initialize_database():
    try:
        # Database connection
        print("Connecting to the database...")
        with psycopg2.connect(
            dbname='adel_mazouzi_qfv4',
	    user='adel_mazouzi_qfv4_user',
	    password='B69vNlkwbvaTdqBYS8GhPerRCPk0G4i3',
	    host='dpg-cpakbfn109ks73apokt0-a',
	    port='5432'
        ) as conn:
            print("Connected to the database.")
            with conn.cursor() as cursor:
                # Check if the table exists
                print("Checking if table 'tblstudents' exists...")
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'tblstudents')")
                table_exists = cursor.fetchone()[0]

                # If the table doesn't exist, create it
                if not table_exists:
                    print("Creating table 'tblstudents'...")
                    cursor.execute("""
                        CREATE TABLE tblstudents (
                            id SERIAL PRIMARY KEY,
                            full_name VARCHAR(255) NOT NULL,
                            student_number VARCHAR(50) NOT NULL,
                            emirates_id VARCHAR(50) NOT NULL,
                            gender VARCHAR(10) NOT NULL,
                            class_id INT NOT NULL,
                            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # Define a mapping between class identifiers and their integer representations
                    class_mapping = {
                        '5A': 1, '5B': 2, '5C': 3, '5D': 4, '5E': 5, '5F': 6, '5G': 7, '5H': 8,
                        '11A1': 9, '11A2': 10, '11A3': 11, '11G1': 12, '11G2': 13, '11G3': 14, '11G4': 15, '11G5': 16, '11G6': 17, '11G7': 18,
                        '12A1': 19, '12A2': 20, '12G1': 21, '12G2': 22, '12G3': 23, '12G4': 24, '12G5': 25, '12G6': 26, '12G7': 27
                    }

                    # Insert initial data with class identifiers mapped to integer representations
                    print("Inserting initial data...")
                    for student_data in STUDENTS_DATA:
                        class_identifier = student_data[4]  # Assuming class identifier is at index 4 in STUDENTS_DATA
                        class_id = class_mapping.get(class_identifier, None)
                        if class_id is not None:
                            cursor.execute("""
                                INSERT INTO tblstudents (full_name, student_number, emirates_id, gender, class_id)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (student_data[0], student_data[1], student_data[2], student_data[3], class_id))
                        else:
                            print(f"Warning: Class identifier '{class_identifier}' not found in mapping. Skipping record {student_data[0]}.")

                    # Commit changes
                    conn.commit()
                    print("Table 'tblstudents' created and initial data inserted successfully.")
                else:
                    print("Table 'tblstudents' already exists. Skipping creation and data insertion.")

    except Exception as e:
        print("Error initializing database:", e)

# Run the database initialization function when the application starts
initialize_database()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

