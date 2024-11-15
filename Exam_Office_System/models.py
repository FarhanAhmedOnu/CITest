from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from datetime import date
from django.utils import timezone
default=timezone.now


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not role:
            raise ValueError('The Role field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, role='Exam_Office', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if role not in ['Exam_Office', 'Teacher','Department','Student']:
            raise ValueError('Superuser must have a valid role')
        return self.create_user(username, email, password, role, **extra_fields)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Exam_Office', 'Exam Office'),
        ('Department', 'Department'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # For admin site access

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']

    def __str__(self):
        return self.username

# Department Model
class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='department_profile')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_number = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    session = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    hall_clearance = models.BooleanField(default=False,null=True)
    library_clearance = models.BooleanField(default=False,null=True)
    expelled = models.BooleanField(default=False,null=True)

    def __str__(self):
        return self.name

# Teacher Model
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Exam Office or Admin Model
class ExamOfficeOrAdmin(models.Model):
    OFFICE_ROLE_CHOICES = [
        ('Exam_Office', 'Exam Office'),
        ('Admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='exam_office_profile')
    office_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.office_name

# Course Model
class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=50, unique=True)
    course_title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course_code} - {self.course_title}"

# Exam Model
class Exam(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='exams')
    batch = models.CharField(max_length=50)
    session = models.CharField(max_length=50)
    exam_date = models.DateField()
    courses = models.ManyToManyField(Course, related_name='exams')
    invigilator = models.ManyToManyField(Teacher, related_name='invigilated_exams',blank=True)
    examiner1 = models.ManyToManyField(Teacher,   related_name='exam1_exams',blank=True)
    examiner2 = models.ManyToManyField(Teacher,  related_name='exam2_exams',blank=True)
    examiner3 = models.ManyToManyField(Teacher, related_name='exam3_exams',blank=True)
    question_creator = models.ManyToManyField(Teacher, related_name='question_created_exams',blank=True)
    moderator = models.ManyToManyField(Teacher,  related_name='moderated_exams',blank=True)
    translator = models.ManyToManyField(Teacher, related_name='translated_exams',blank=True)

# Exam Schedule Model
class ExamSchedule(models.Model):
    STATUS_CHOICES = [
        ('Published', 'Published'),
        ('Modified', 'Modified'),
    ]

    exam = models.OneToOneField(Exam, on_delete=models.CASCADE, related_name='schedule')
    published_date = models.DateField()
    modified_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Schedule for {self.exam}"

# Exam Registration Model
class ExamRegistration(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CreditCard', 'Credit Card'),
        ('BankTransfer', 'Bank Transfer'),
        ('MobilePayment', 'Mobile Payment'),
    ]

    REGISTRATION_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Retake', 'Retake'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_registrations')
    exams = models.ManyToManyField(Exam, related_name='registrations')
    registration_type = models.CharField(max_length=20, choices=REGISTRATION_TYPE_CHOICES)
    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    ineligibility_reasons = models.TextField(null=True, blank=True)
    admit_card_generated = models.BooleanField(default=False)

    def __str__(self):
        return f"Registration {self.id} by {self.student.name}"

# Results Model
class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    marks = models.IntegerField()

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"Result {self.id} - {self.student.name}: {self.marks} marks"

# Marksheet Application Model
class MarksheetApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CreditCard', 'Credit Card'),
        ('BankTransfer', 'Bank Transfer'),
        ('MobilePayment', 'Mobile Payment'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marksheet_applications')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marksheet_applications')
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    token = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Marksheet Application {self.id} by {self.student.name}"

# Certificate Application Model
class CertificateApplication(models.Model):
    DEGREE_CHOICES = [
        ('Honours', 'Honours'),
        ('Regular Masters', 'Regular Masters'),
        ('Professional Masters', 'Professional Masters'),
        ('PhD', 'PhD'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CreditCard', 'Credit Card'),
        ('BankTransfer', 'Bank Transfer'),
        ('MobilePayment', 'Mobile Payment'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificate_applications')
    degree = models.CharField(max_length=30, choices=DEGREE_CHOICES)
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    token = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Certificate Application {self.id} by {self.student.name}"

# Teacher Remuneration Model
class TeacherRemuneration(models.Model):
    ROLE_CHOICES = [
        ('Invigilator', 'Invigilator'),
        ('Examiner', 'Examiner'),
        ('QuestionSetter', 'Question Setter'),
        ('Moderator', 'Moderator'),
        ('Translator', 'Translator'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='remunerations')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='remunerations')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Remuneration {self.id} for {self.teacher.name} as {self.role}"

# Exam Materials Model
class ExamMaterials(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('AnswerScripts', 'Answer Scripts'),
        ('LooseSheets', 'Extra Loose Sheets'),
    ]
    
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='materials')
    material_type = models.CharField(max_length=50, choices=MATERIAL_TYPE_CHOICES)
    quantity = models.IntegerField()
    issued_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.material_type} for {self.exam}"
        
# Inventory Management Model for Stock Tracking and Alerts
class MaterialInventory(models.Model):
    material_type = models.CharField(max_length=50, choices=ExamMaterials.MATERIAL_TYPE_CHOICES, unique=True)
    stock_quantity = models.IntegerField()
    threshold_quantity = models.IntegerField(default=200)  # Set a default threshold for alerts
    
    def __str__(self):
        return f"{self.material_type} - Stock: {self.stock_quantity}"
    
    def is_below_threshold(self):
        return self.stock_quantity < self.threshold_quantity
    
    def update_stock(self, used_quantity):
        self.stock_quantity -= used_quantity
        if self.is_below_threshold():
            # Code to generate an alert to Exam Office Representative
            print(f"Alert: {self.material_type} stock is below threshold!")
        self.save()

# Exam Office Representative Activity Log for Auditing
class MaterialDistributionLog(models.Model):
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='distribution_logs')
    material_type = models.CharField(max_length=50, choices=ExamMaterials.MATERIAL_TYPE_CHOICES)
    quantity_issued = models.IntegerField()
    distribution_date = models.DateField(default=date.today)
    
    def __str__(self):
        return f"{self.quantity_issued} {self.material_type} issued for {self.exam} on {self.distribution_date}"


class StudentAttendance(models.Model):
    """
    Represents the attendance record of a student for a specific exam.

    Attributes:
        attendance (ForeignKey): A reference to the `Attendance` model, representing the specific attendance record.
        student (ForeignKey): A reference to the `Student` model, representing the student whose attendance is recorded.
        is_present (BooleanField): Indicates whether the student was present (True) or absent (False).
    """
    attendance = models.ForeignKey('Attendance', on_delete=models.CASCADE, related_name='student_attendance_records')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='attendance_records')
    is_present = models.BooleanField(default=False)


class TeacherAttendance(models.Model):
    """
    Represents the attendance record of a teacher for a specific exam.

    Attributes:
        attendance (ForeignKey): Reference to the `Attendance` model, representing the specific attendance record.
        teacher (ForeignKey): Reference to the `Teacher` model, representing the teacher whose attendance is recorded.
        is_present (BooleanField): Indicates whether the teacher was present (True) or absent (False).
    """
    attendance = models.ForeignKey('Attendance', on_delete=models.CASCADE, related_name='teacher_attendance_records')
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='attendance_records')
    is_present = models.BooleanField(default=False)


class Attendance(models.Model):
    """
    Represents an attendance record for an exam.

    Attributes:
        exam (ForeignKey): A reference to the `Exam` model, representing the specific exam for which attendance is recorded.
        student (ManyToManyField): A many-to-many relationship to the `Student` model through `StudentAttendance`, representing students attending the exam.
        teacher (ManyToManyField): A many-to-many relationship to the `Teacher` model through `TeacherAttendance`, representing teachers attending the exam.
        attendance_date (DateField): The date of the attendance record.

    Methods:
        update_teachers_from_exam: This method updates the list of teachers associated with the exam based on roles like invigilators, question creators, and moderators.
    """

    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Invigilator', 'Invigilator'),
    ]

    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='attendances')
    student = models.ManyToManyField('Student', through=StudentAttendance, related_name='attendances', blank=True)
    teacher = models.ManyToManyField('Teacher', through=TeacherAttendance, related_name='attendances', blank=True)
    attendance_date = models.DateField()

    def update_teachers_from_exam(self):
        """
        Updates the list of teachers associated with this exam.

        This method fetches teachers associated with the exam in roles like invigilators, question creators,
        and moderators, and updates the `teacher` field.
        """
        # Retrieve all teachers associated with this exam through various roles
        associated_teachers = Teacher.objects.filter(
            models.Q(invigilated_exams=self.exam) |
            models.Q(exam1_exams=self.exam) |
            models.Q(exam2_exams=self.exam) |
            models.Q(exam3_exams=self.exam) |
            models.Q(question_created_exams=self.exam) |
            models.Q(moderated_exams=self.exam) |
            models.Q(translated_exams=self.exam)
        ).distinct()

        # Update the 'teacher' field with these associated teachers
        self.teacher.set(associated_teachers)