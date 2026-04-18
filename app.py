from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Student, Faculty, Attendance, Mark, ExamSchedule, StaffAttendance, StaffSalary
from forms import LoginForm, UserForm, AttendanceForm, MarksForm, ExamScheduleForm, StaffAttendanceForm, SalaryForm
from config import Config
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# RBAC Decorators
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash(f'Access denied. {role} role required.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'Faculty':
            return redirect(url_for('faculty_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Admin Dashboard
@app.route('/admin')
@login_required
@role_required('Admin')
def admin_dashboard():
    students_count = Student.query.count()
    faculty_count = Faculty.query.count()
    users_count = User.query.count()
    exams_count = ExamSchedule.query.count()
    return render_template('admin_dashboard.html', students_count=students_count, faculty_count=faculty_count, users_count=users_count, exams_count=exams_count)

@app.route('/admin/manage-users', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_users():
    form = UserForm()
    users = User.query.all()
    if form.validate_on_submit():
        new_user = User(name=form.name.data, email=form.email.data, role=form.role.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.flush() # Get user_id

        if form.role.data == 'Student':
            student = Student(user_id=new_user.user_id, department=form.department.data, semester=form.semester.data)
            db.session.add(student)
        elif form.role.data == 'Faculty':
            faculty = Faculty(user_id=new_user.user_id, subject=form.subject.data)
            db.session.add(faculty)
        
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('manage_users.html', form=form, users=users)

@app.route('/admin/exams', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_exams():
    form = ExamScheduleForm()
    exams = ExamSchedule.query.all()
    if form.validate_on_submit():
        exam = ExamSchedule(
            subject=form.subject.data,
            date=form.date.data,
            time=form.time.data,
            department=form.department.data,
            semester=form.semester.data
        )
        db.session.add(exam)
        db.session.commit()
        flash('Exam scheduled successfully!', 'success')
        return redirect(url_for('manage_exams'))
    return render_template('manage_exams.html', form=form, exams=exams)

@app.route('/admin/staff-attendance', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def staff_attendance():
    form = StaffAttendanceForm()
    faculty_list = Faculty.query.all()
    form.faculty_id.choices = [(f.faculty_id, f.user.name) for f in faculty_list]
    
    recent_attendance = StaffAttendance.query.order_by(StaffAttendance.date.desc()).limit(10).all()
    
    if form.validate_on_submit():
        att = StaffAttendance(faculty_id=form.faculty_id.data, date=form.date.data, status=form.status.data)
        db.session.add(att)
        db.session.commit()
        flash('Staff attendance marked!', 'success')
        return redirect(url_for('staff_attendance'))
    return render_template('staff_attendance.html', form=form, attendance=recent_attendance)

@app.route('/admin/salary', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_salary():
    form = SalaryForm()
    faculty_list = Faculty.query.all()
    form.faculty_id.choices = [(f.faculty_id, f.user.name) for f in faculty_list]
    
    salaries = StaffSalary.query.order_by(StaffSalary.year.desc(), StaffSalary.month.desc()).all()
    
    if form.validate_on_submit():
        salary = StaffSalary(
            faculty_id=form.faculty_id.data,
            amount=form.amount.data,
            month=form.month.data,
            year=form.year.data,
            status=form.status.data
        )
        db.session.add(salary)
        db.session.commit()
        flash('Salary processed!', 'success')
        return redirect(url_for('manage_salary'))
    return render_template('manage_salary.html', form=form, salaries=salaries)

# Faculty Dashboard
@app.route('/faculty')
@login_required
@role_required('Faculty')
def faculty_dashboard():
    faculty_profile = Faculty.query.filter_by(user_id=current_user.user_id).first()
    students = Student.query.all()
    students_count = len(students)
    return render_template('faculty_dashboard.html', faculty=faculty_profile, students=students, students_count=students_count)

@app.route('/faculty/attendance', methods=['GET', 'POST'])
@app.route('/faculty/attendance/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def mark_attendance(student_id=None):
    form = AttendanceForm()
    students = Student.query.all()
    form.student_id.choices = [(s.student_id, f"{s.user.name} ({s.department})") for s in students]
    
    if request.method == 'GET' and student_id:
        form.student_id.data = student_id
    
    if form.validate_on_submit():
        attendance = Attendance(student_id=form.student_id.data, date=form.date.data, status=form.status.data)
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))
    return render_template('mark_attendance.html', form=form)

@app.route('/faculty/my-attendance')
@login_required
@role_required('Faculty')
def faculty_my_attendance():
    faculty_profile = Faculty.query.filter_by(user_id=current_user.user_id).first()
    attendance = StaffAttendance.query.filter_by(faculty_id=faculty_profile.faculty_id).all()
    return render_template('faculty_my_attendance.html', attendance=attendance)

@app.route('/faculty/my-salary')
@login_required
@role_required('Faculty')
def faculty_my_salary():
    faculty_profile = Faculty.query.filter_by(user_id=current_user.user_id).first()
    salaries = StaffSalary.query.filter_by(faculty_id=faculty_profile.faculty_id).all()
    return render_template('faculty_my_salary.html', salaries=salaries)

@app.route('/faculty/marks', methods=['GET', 'POST'])
@app.route('/faculty/marks/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('Faculty')
def upload_marks(student_id=None):
    form = MarksForm()
    students = Student.query.all()
    form.student_id.choices = [(s.student_id, f"{s.user.name} ({s.department})") for s in students]
    
    if request.method == 'GET' and student_id:
        form.student_id.data = student_id
    
    if form.validate_on_submit():
        mark = Mark(student_id=form.student_id.data, subject=form.subject.data, marks=form.marks.data)
        db.session.add(mark)
        db.session.commit()
        flash('Marks uploaded successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))
    return render_template('upload_marks.html', form=form)

# Student Dashboard
@app.route('/student')
@login_required
@role_required('Student')
def student_dashboard():
    student_profile = Student.query.filter_by(user_id=current_user.user_id).first()
    attendance = Attendance.query.filter_by(student_id=student_profile.student_id).all()
    marks = Mark.query.filter_by(student_id=student_profile.student_id).all()
    
    total_days = len(attendance)
    present_days = len([a for a in attendance if a.status == 'Present'])
    attendance_perc = (present_days / total_days * 100) if total_days > 0 else 0
    
    return render_template('student_dashboard.html', student=student_profile, attendance=attendance, marks=marks, attendance_perc=attendance_perc)

@app.route('/student/exams')
@login_required
@role_required('Student')
def student_exams():
    student_profile = Student.query.filter_by(user_id=current_user.user_id).first()
    exams = ExamSchedule.query.filter_by(department=student_profile.department, semester=student_profile.semester).all()
    return render_template('student_exams.html', exams=exams, date=date)

# Database Initialization Utility
def init_db():
    with app.app_context():
        db.create_all()
        # Check if admin exists, if not seed data
        if not User.query.filter_by(email='admin@college.com').first():
            seed_data()
            print("Database initialized and seeded.")

def seed_data():
    # Admin
    admin = User(name='Admin Kumar', email='admin@college.com', role='Admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Faculty
    f1_user = User(name='Dr. Ravi', email='ravi@college.com', role='Faculty')
    f1_user.set_password('faculty123')
    db.session.add(f1_user)
    
    f2_user = User(name='Dr. Meena', email='meena@college.com', role='Faculty')
    f2_user.set_password('faculty123')
    db.session.add(f2_user)
    
    db.session.flush()
    
    f1 = Faculty(user_id=f1_user.user_id, subject='Database Systems', base_salary=65000.0)
    f2 = Faculty(user_id=f2_user.user_id, subject='Web Technologies', base_salary=60000.0)
    db.session.add_all([f1, f2])
    
    # Students
    student_data = [
        ('Arun', 'arun@college.com', 'CSE', 5),
        ('Priya', 'priya@college.com', 'CSE', 5),
        ('Karthik', 'karthik@college.com', 'IT', 3),
        ('Divya', 'divya@college.com', 'IT', 3),
        ('Suresh', 'suresh@college.com', 'ECE', 6),
        ('Anitha', 'anitha@college.com', 'ECE', 6),
        ('Manoj', 'manoj@college.com', 'CSE', 1),
    ]
    
    for name, email, dept, sem in student_data:
        u = User(name=name, email=email, role='Student')
        u.set_password('student123')
        db.session.add(u)
        db.session.flush()
        s = Student(user_id=u.user_id, department=dept, semester=sem)
        db.session.add(s)
        
    db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
