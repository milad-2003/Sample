from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/create_course/', create_course, name='create_course'),
    path('dashboard/enroll/<int:course_id>', enroll_in_course, name='enroll_in_course'),
]
