from django.contrib import admin

# Register your models here.
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'User role',
            {
                'fields':(
                    'phone_No',
                    'profile_pic',
                    'is_member',
                    'stripe_customer_id',
                    'Api_Key',
                )
            }
        )
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Inventory)
admin.site.register(Membership)
admin.site.register(Payment)
