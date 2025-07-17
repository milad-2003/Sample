from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import *


User = get_user_model()


def index(request):
    print(request.user)
    return render(request, 'index.html', {'user': request.user})

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'نام کاربری قبلاً استفاده شده.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'ایمیل قبلاً استفاده شده.')
            return redirect('signup')

        if password != password2:
            messages.error(request, 'رمز عبورها یکسان نیستند.')
            return redirect('signup')

        if len(password) < 8:
            messages.error(request, 'رمز باید حداقل ۸ کاراکتر داشته باشد.')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)

        if role == 'student':
            Student.objects.create(user=user)
        elif role == 'teacher':
            Teacher.objects.create(user=user)
        else:
            messages.error(request, 'نقش انتخاب نشده است.')
            user.delete()
            return redirect('signup')

        messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
        return redirect('login')



    # GET request
    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')

        messages.error(request, "اطلاعات وارد شده اشتباه است!")
        return redirect('login')

    # GET request
    return render(request, 'login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    user = request.user

    # Teacher
    if hasattr(user, 'teacher'):
        teacher = user.teacher
        if not teacher.is_authenticated:
            return render(request, 'dashboard/teacher_pending.html', {'user': user})
        
        courses = Course.objects.filter(teacher=teacher)
        return render(request, 'dashboard/teacher_dashboard.html', {
            'user': user,
            'teacher': teacher,
            'courses': courses
        })

    # Student
    elif hasattr(user, 'student'):
        student = user.student
        taken_courses = TakeCourse.objects.filter(student=student).select_related('course')
        all_courses = Course.objects.all()
        return render(request, 'dashboard/student_dashboard.html', {
            'user': user,
            'student': student,
            'taken_courses': taken_courses,
            'all_courses': all_courses
        })
    
    # Not teacher or student
    return render(request, 'dashboard/no_role.html', {'user': user})
    

@login_required(login_url='login')
def create_course(request):
    if not hasattr(request.user, 'teacher'):
        messages.error(request, "فقط اساتید می‌توانند دوره بسازند.")
        return redirect('dashboard')

    teacher = request.user.teacher
    if not teacher.is_authenticated:
        messages.error(request, "اکانت شما هنوز تایید نشده است.")
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not title or not description:
            messages.error(request, "همه فیلدها الزامی هستند.")
        else:
            Course.objects.create(title=title, description=description, teacher=teacher)
            return redirect('dashboard')

    return render(request, 'dashboard/create_course.html')


from .models import Course, Student, TakeCourse

@login_required(login_url='login')
def enroll_in_course(request, course_id):
    if not hasattr(request.user, 'student'):
        messages.error(request, "فقط دانشجویان می‌توانند در دوره ثبت‌نام کنند.")
        return redirect('dashboard')

    student = request.user.student
    course = Course.objects.get(id=course_id)

    if TakeCourse.objects.filter(student=student, course=course).exists():
        messages.error(request, "شما قبلاً در این دوره ثبت‌نام کرده‌اید.")
    else:
        TakeCourse.objects.create(student=student, course=course)

    return redirect('dashboard')
