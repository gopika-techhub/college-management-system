from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateField, FloatField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('Admin', 'Admin'), ('Faculty', 'Faculty'), ('Student', 'Student')])
    department = StringField('Department (for Student)')
    semester = IntegerField('Semester (for Student)')
    subject = StringField('Subject (for Faculty)')
    submit = SubmitField('Create User')

class AttendanceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent')])
    submit = SubmitField('Mark Attendance')

class MarksForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    marks = FloatField('Marks', validators=[DataRequired()])
    submit = SubmitField('Upload Marks')

class ExamScheduleForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = StringField('Time (e.g. 10:00 AM)', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired()])
    submit = SubmitField('Schedule Exam')

class StaffAttendanceForm(FlaskForm):
    faculty_id = SelectField('Staff/Faculty', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent')])
    submit = SubmitField('Mark Attendance')

class SalaryForm(FlaskForm):
    faculty_id = SelectField('Staff/Faculty', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    month = SelectField('Month', choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')])
    year = IntegerField('Year', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Paid', 'Paid'), ('Pending', 'Pending')])
    submit = SubmitField('Process Salary')
