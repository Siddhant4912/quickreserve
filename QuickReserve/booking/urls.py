from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('', views.home_view, name='home'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('booking_form/', views.book_room, name='booking_form'),
    path('add_room/', views.add_room, name='add_room'),
    path('logout/', views.logout_view, name='logout'),
    # for delete
    path('delete-booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    # book slot
    path('api/booked-slots/', views.get_booked_slots, name='booked_slots'),
    # delte room admin
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),

    



    # Employee registration 
    path('register/', views.register_employee, name='register_employee'),


    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path('admin/add-amenity/', views.add_amenity, name='add_amenity'),

]
