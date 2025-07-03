from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField




class RegisterEmployeeManager(BaseUserManager):
    def create_user(self, emp_gmail, emp_name, emp_password=None, **extra_fields):
        if not emp_gmail:
            raise ValueError('Email is required')
        email = self.normalize_email(emp_gmail)
        user = self.model(emp_gmail=email, emp_name=emp_name, **extra_fields)
        user.set_password(emp_password)
        user.save(using=self._db)
        return user

    def create_superuser(self, emp_gmail, emp_name, emp_password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(emp_gmail, emp_name, emp_password, **extra_fields)

class Register_Employee(AbstractBaseUser, PermissionsMixin):
    emp_name = models.CharField(max_length=100)
    emp_gmail = models.EmailField(unique=True)
    emp_phoneNumber = PhoneNumberField(region='IN', unique=True)
    emp_isActive = models.BooleanField(default=True)

    # Required by Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    objects = RegisterEmployeeManager()

    USERNAME_FIELD = 'emp_gmail'
    REQUIRED_FIELDS = ['emp_name']  # Mandatory for create_superuser

    def __str__(self):
        return self.emp_name





class Room(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    amenities = models.TextField(help_text="Comma-separated (e.g. AC, Projector)")

    def __str__(self):
        return self.name

class Equipment(models.Model):  # Rename from 'amenities' for clarity
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Room_Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    employee = models.ForeignKey(Register_Employee, on_delete=models.CASCADE)
    meeting_title = models.CharField(max_length=255)
    participants = models.PositiveIntegerField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    equipment = models.ManyToManyField(Equipment, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meeting_title} - {self.room.name} on {self.date}"
