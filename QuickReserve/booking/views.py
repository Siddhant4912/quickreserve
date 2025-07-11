from datetime import date, timedelta
from email import errors
import email
from functools import wraps
from django.contrib import messages  
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Equipment, Room, Register_Employee
from .forms import RoomForm, RegisterEmployeeForm
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError, DataError
from .models import EmailOTP
from django.utils.crypto import get_random_string


from django.views.decorators.cache import never_cache
from .models import Room_Booking, Register_Employee, Room, Equipment  # ✅ include these if not already
from datetime import date
from .models import Room_Booking, Register_Employee, Room, Equipment
# verification
from django.core.mail import send_mail
from django.utils import timezone  # ✅ Correct import

# room booking
from django.shortcuts import render, redirect
from .forms import RoomBookingForm
from .models import Register_Employee, Room_Booking

from django.utils.html import format_html_join

# ------------------------------
# HOME
# ------------------------------

def home_view(request):
    if request.session.get('employee_id'):
        return redirect('admin_dashboard' if request.session.get('is_admin') else 'employee_dashboard')

    form = RegisterEmployeeForm()
    return render(request, 'home.html', {'register_form': form})


# ------------------------------
# EMPLOYEE LOGIN + LOGOUT + DASHBOARD
# ------------------------------
def login_view(request):
    # 🚫 Already logged in
    if request.session.get('employee_id'):
        is_admin = request.session.get('is_admin', False)
        return redirect('admin_dashboard' if is_admin else 'employee_dashboard')

    if request.method == 'POST':
        email = request.POST.get('emp_email')
        password = request.POST.get('emp_password')

        try:
            employee = Register_Employee.objects.get(emp_gmail=email)

            if employee.check_password(password):
                # Set session
                request.session['employee_id'] = employee.id
                request.session['employee_name'] = employee.emp_name
                request.session['is_admin'] = employee.is_admin

                return redirect('admin_dashboard' if employee.is_admin else 'employee_dashboard')
            else:
                return render(request, 'home.html', {'login_error': 'Incorrect password'})
        except Register_Employee.DoesNotExist:
            return render(request, 'home.html', {'login_error': 'Email not registered'})

    return redirect('home')




def logout_view(request):
    request.session.flush()
    return redirect('login')

# ------------------------------
# ADMIN DASHBOARD (OPTIONAL)
# ------------------------------
#  Shared admin check
# admin dashboard view







def is_admin_session(request):
    return request.session.get('is_admin', False)



@never_cache
def add_room(request):
    
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        room_id = request.POST.get("room_id")
        room_name = request.POST.get("roomName")
        room_location = request.POST.get("roomLocation")
        capacity = request.POST.get("capacity")
        amenities_ids = request.POST.getlist("amenities")  # this will still be list of IDs

        # Get names from IDs
        selected_amenities = Equipment.objects.filter(id__in=amenities_ids)
        amenity_names = [a.name for a in selected_amenities]
        amenities_string = ", ".join(amenity_names)

        if room_id:
            try:
                room = Room.objects.get(id=room_id)
                room.name = room_name
                room.location = room_location
                room.capacity = capacity
                room.amenities = amenities_string
                room.save()
                return JsonResponse({"success": True, "updated": True})
            except Room.DoesNotExist:
                return JsonResponse({"success": False, "errors": "Room not found."})
        else:
            room = Room.objects.create(
                name=room_name,
                location=room_location,
                capacity=capacity,
                amenities=amenities_string,
            )
            return JsonResponse({"success": True, "updated": False})

    return JsonResponse({"success": False, "errors": "Invalid request"})



def delete_room(request, room_id):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            room = Room.objects.get(id=room_id)
            room.delete()
            return JsonResponse({'success': True})
        except Room.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Room not found.'})

    # fallback for non-AJAX deletion (optional)
    try:
        room = Room.objects.get(id=room_id)
        room.delete()
        return HttpResponseRedirect(reverse('admin_dashboard'))  # redirect to your dashboard
    except Room.DoesNotExist:
        return HttpResponseRedirect(reverse('admin_dashboard'))
# ------------------------------
#  REGISTRATION
# ------------------------------


# register with otp 

def register_employee(request):
    if request.method == "POST":
        name     = request.POST.get("emp_name")
        gmail    = request.POST.get("emp_gmail")
        phone    = request.POST.get("emp_phoneNumber")
        password = request.POST.get("emp_password")
        confirm_password = request.POST.get("confirm_password")

        errors = {}

        if Register_Employee.objects.filter(emp_gmail=gmail).exists():
            errors["emp_gmail"] = "Email already exists."
        if Register_Employee.objects.filter(emp_phoneNumber=phone).exists():
            errors["emp_phoneNumber"] = "Phone number already exists."


        if errors:
            return render(request, "home.html", {"register_errors": errors})

        # Save user data temporarily in session
        request.session["temp_user"] = {
            "emp_name": name,
            "emp_gmail": gmail,
            "emp_phoneNumber": phone,
            "password": password
        }

        # Send OTP to email
        otp_code = get_random_string(length=6, allowed_chars="0123456789")
        EmailOTP.objects.filter(email=gmail).delete()  # clear any old OTPs
        EmailOTP.objects.create(email=gmail, code=otp_code)

        send_mail(
            subject="Verify your email",
            message=f"Hello {name}, your OTP is: {otp_code}",
            from_email="syitsd20if002@gmail.com",
            recipient_list=[gmail]
        )

        return redirect("verify_otp")

    return redirect("home")


# verfiy otp
def verify_otp_view(request):
    if request.method == "POST":
        code = request.POST.get("otp")
        temp_user = request.session.get("temp_user")

        if not temp_user:
            messages.error(request, "Session expired. Please register again.")
            return redirect("home")

        otp = EmailOTP.objects.filter(email=temp_user["emp_gmail"]).order_by("-created_at").first()

        if otp and otp.is_valid(code):
            # Create user now
            user = Register_Employee.objects.create_user(
                emp_name=temp_user["emp_name"],
                emp_gmail=temp_user["emp_gmail"],
                emp_phoneNumber=temp_user["emp_phoneNumber"],
                password=temp_user["password"],
                is_active=True
            )

            # Clean up
            del request.session["temp_user"]
            EmailOTP.objects.filter(email=temp_user["emp_gmail"]).delete()

            # Log in
            request.session["employee_id"] = user.id
            request.session["employee_name"] = user.emp_name
            request.session["is_admin"] = user.is_admin

            return redirect("employee_dashboard")

        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "verify_otp.html")




def get_booked_slots(request):
    room_id = request.GET.get('room_id')
    date = request.GET.get('date')

    if room_id and date:
        bookings = Room_Booking.objects.filter(room_id=room_id, date=date)
        slots = [
            {'start': str(b.start_time)[:5], 'end': str(b.end_time)[:5]}
            for b in bookings
        ]
        return JsonResponse({'slots': slots})
    return JsonResponse({'slots': []})

def book_room(request):
    if request.method == 'POST':
        emp_id = request.session.get('employee_id')
        if not emp_id:
            return redirect('login') 

        employee = Register_Employee.objects.get(id=emp_id)

        # Get POST data
        booking_id = request.POST.get('booking_id')  # ✅ ID for update
        meeting_title = request.POST.get('meeting_title')
        room_id = request.POST.get('room')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        participants = request.POST.get('participants')
        amenities = request.POST.getlist('amenities')

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            messages.error(request, "Selected room does not exist.")
            return redirect('employee_dashboard')

        equipment_objs = Equipment.objects.filter(name__in=amenities)

        if booking_id:
            # ✅ UPDATE existing booking
            try:
                booking = Room_Booking.objects.get(id=booking_id, employee=employee)
                booking.meeting_title = meeting_title
                booking.room = room
                booking.date = date
                booking.start_time = start_time
                booking.end_time = end_time
                booking.participants = participants
                booking.equipment.set(equipment_objs)
                booking.save()
                messages.success(request, "Booking updated successfully!")
            except Room_Booking.DoesNotExist:
                messages.error(request, "Booking not found.")
        else:
            # ✅ CREATE new booking
            booking = Room_Booking.objects.create(
                room=room,
                meeting_title=meeting_title,
                participants=participants,
                date=date,
                start_time=start_time,
                end_time=end_time,
                employee=employee
            )
            booking.equipment.set(equipment_objs)
            booking.save()
            messages.success(request, "Room booked successfully!")

        return redirect('employee_dashboard')

    return redirect('employee_dashboard')




def delete_booking(request, booking_id):
    emp_id = request.session.get('employee_id')
    if not emp_id:
        return redirect('login')

    try:
        booking = Room_Booking.objects.get(id=booking_id, employee_id=emp_id)

        # ✅ Prevent deletion if the booking date is in the past
        if booking.date < date.today():
            messages.error(request, "You cannot delete past bookings.")
            return redirect('employee_dashboard')

        booking.delete()
        messages.success(request, "Booking deleted successfully.")
    except Room_Booking.DoesNotExist:
        messages.error(request, "Booking not found or unauthorized.")

    return redirect('employee_dashboard')


def delete_room(request, room_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            room = Room.objects.get(id=room_id)
            room.delete()
            return JsonResponse({'success': True})
        except Room.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Room not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# admin dashboard view
@never_cache
def admin_dashboard(request):
    filter_option = request.GET.get('filter', 'upcoming')
    emp_id = request.session.get('employee_id')

    if not request.session.get('is_admin'):
        return redirect('login')

    employee = Register_Employee.objects.get(id=emp_id)
    today = date.today()

    all_rooms = Room.objects.all()
    all_amenities = Equipment.objects.all()

    # Handle filtered bookings
    if filter_option == 'past':
        filtered_bookings = Room_Booking.objects.filter(date__lt=today)
    elif filter_option == 'upcoming':
        filtered_bookings = Room_Booking.objects.filter(date__gte=today)
    elif filter_option == 'all':
        filtered_bookings = Room_Booking.objects.all()
    else:
        filtered_bookings = None  # For "rooms" and "amenities", don't show bookings

    context = {
        'filter_option': filter_option,
        'rooms': all_rooms,
        'amenities': all_amenities,
        'total_amenities': all_amenities.count(),
        'total_rooms': all_rooms.count(),
        'employee': employee,
        'today': today,
        'total_bookings': Room_Booking.objects.count(),
        'employee_bookings': filtered_bookings,

        # Flags to control template rendering
        'show_rooms': filter_option == 'rooms',
        'show_amenities': filter_option == 'amenities',
    }

    return render(request, 'admin/admin_dashboard.html', context)

@never_cache
def add_amenity(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            return JsonResponse({'success': False, 'errors': '<div class="alert alert-danger">Name is required.</div>'})

        if Equipment.objects.filter(name__iexact=name).exists():
            return JsonResponse({'success': False, 'errors': '<div class="alert alert-warning">Amenity already exists.</div>'})

        Equipment.objects.create(name=name)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'errors': '<div class="alert alert-danger">Invalid request.</div>'})

#employee dashboard view
@never_cache
def employee_dashboard(request):
    filter_option = request.GET.get('filter', 'upcoming')
    emp_id = request.session.get('employee_id')
    if not emp_id:
        return redirect('login')

    employee = Register_Employee.objects.get(id=emp_id)
    today = date.today()

    # Apply filter
    if filter_option == 'past':
        bookings = Room_Booking.objects.filter(employee=employee, date__lt=today)
    elif filter_option == 'all':
        bookings = Room_Booking.objects.filter(employee=employee)
    else:  # upcoming
        bookings = Room_Booking.objects.filter(employee=employee, date__gte=today)

    context = {
        'filter_option': filter_option,
        'bookings': bookings,
        # any other data you're passing like:
        'rooms': Room.objects.all(),
        'equipment': Equipment.objects.all(),
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.exclude(
            id__in=Room_Booking.objects.filter(date=today).values_list('room_id', flat=True)
        ).count(),
        'my_bookings': Room_Booking.objects.filter(employee=employee).count(),
        'employee': employee,
        'today': today,
    }

    return render(request, 'employee/employee_dashboard.html', context)
