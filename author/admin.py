from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import User

class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        phone_number = cleaned_data.get('phone_number')
        age = cleaned_data.get('age')

        if role == 'pupil':
            cleaned_data.pop('email', None)  # Emailni o'chiramiz
            if not phone_number:
                self.add_error('phone_number', 'Oʻquvchilar uchun telefon raqami kiritilishi shart!')
            if not age:
                self.add_error('age', 'Oʻquvchilar uchun yosh kiritilishi shart!')
        else:
            if not cleaned_data.get('email'):
                self.add_error('email', 'Email kiritilishi shart!')

        return cleaned_data


# User modelini unregister qilish
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    list_display = ("id",'username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'role')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy maʼlumotlar', {'fields': ('first_name', 'last_name', 'email', 'bio', 'role', 'phone_number', 'age')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'role', 'phone_number', 'age', 'is_staff', 'is_active'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.role == 'pupil':
            fieldsets = list(fieldsets)
            fieldsets[1] = (fieldsets[1][0], {'fields': tuple(f for f in fieldsets[1][1]['fields'] if f != 'email')})
        return fieldsets
    

# Proxy modellar
class Pupil(User):
    class Meta:
        proxy = True
        verbose_name = 'Pupil'
        verbose_name_plural = 'Pupils'

class Teacher(User):
    class Meta:
        proxy = True
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

class Developer(User):
    class Meta:
        proxy = True
        verbose_name = 'Developer'
        verbose_name_plural = 'Developers'


# Har bir `proxy` model uchun maxsus admin klasslar
@admin.register(Pupil)
class PupilAdmin(CustomUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='pupil')

@admin.register(Teacher)
class TeacherAdmin(CustomUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='teacher')

@admin.register(Developer)
class DeveloperAdmin(CustomUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='developer')
