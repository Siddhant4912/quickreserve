from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Register_Employee
from .forms import RoomForm, RegisterEmployeeForm
from django.contrib.auth.hashers import check_password, make_password

# ------------------------------
# HOME
# ------------------------------

def home_view(request):
    return render(request, 'home.html')

# ------------------------------
# EMPLOYEE LOGIN + LOGOUT + DASHBOARD
# ------------------------------

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Step 1: Find employee by email
            employee = Register_Employee.objects.get(emp_gmail=email)

            # Step 2: Verify password
            if check_password(password, employee.password):
                # Step 3: Store employee in session
                request.session['employee_id'] = employee.id
                request.session['employee_name'] = employee.emp_name

                # Step 4: Redirect to home/dashboard
                return redirect('room_booking_form')  # or 'employee_dashboard'
            else:
                return render(request, 'login.html', {'error': 'Incorrect password'})
        except Register_Employee.DoesNotExist:
            return render(request, 'login.html', {'error': 'Email not registered'})
    
    return render(request, 'login.html')




def logout_view(request):
    request.session.flush()
    return redirect('login')

def employee_dashboard(request):
    emp_id = request.session.get('employee_id')
    if not emp_id:
        return redirect('login')
    employee = Register_Employee.objects.get(id=emp_id)
    return render(request, 'employee_dashboard.html', {'employee': employee})

# ------------------------------
# ADMIN DASHBOARD (OPTIONAL)
# ------------------------------

def admin_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'role') or request.user.role != 'admin':
        return redirect('login')
    return render(request, 'admin_dashboard.html')

# ------------------------------
# ROOM MANAGEMENT (ADMIN ONLY)
# ------------------------------

def room_list_admin(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    rooms = Room.objects.all()
    return render(request, 'admin/room_list.html', {'rooms': rooms})

def add_room(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_list_admin')
    else:
        form = RoomForm()
    return render(request, 'admin/add_room.html', {'form': form})

def edit_room(request, room_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('room_list_admin')
    else:
        form = RoomForm(instance=room)
    return render(request, 'admin/edit_room.html', {'form': form, 'room': room})

def delete_room(request, room_id):
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('login')
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('room_list_admin')

# ------------------------------
# EMPLOYEE REGISTRATION
# ------------------------------

def register_employee(request):
    if request.method == 'POST':
        form = RegisterEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterEmployeeForm()
    return render(request, 'register_employee.html', {'form': form})


# room booking
from django.shortcuts import render, redirect
from .forms import RoomBookingForm
from .models import Register_Employee, Room_Booking

def book_room(request):
    if request.method == 'POST':
        form = RoomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Get employee ID from session
            emp_id = request.session.get('employee_id')
            if not emp_id:
                return redirect('login')  # No session means not logged in

            # Get the employee object
            employee = Register_Employee.objects.get(id=emp_id)
            booking.employee = employee
            booking.save()
            form.save_m2m()
            return redirect('employee_dashboard')
    else:
        form = RoomBookingForm()
    
    return render(request, 'booking_form.html', {'form': form})

