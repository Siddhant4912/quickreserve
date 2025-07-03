from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('', views.home_view, name='home'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('booking_form/', views.book_room, name='booking_form'),  # ✅ fixed here
    path('logout/', views.logout_view, name='logout'),

    # Room Management for Admin
    path('admin/room_list/', views.room_list_admin, name='room_list_admin'),
    path('admin/rooms/add/', views.add_room, name='add_room'),
    path('admin/rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('admin/rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),

    # Employee registration 
    path('register/', views.register_employee, name='register_employee'),
]
