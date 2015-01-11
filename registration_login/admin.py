from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from registration_login.models import UserProfile, Institution

#Define and create the admin interface for the user profiles
class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

'''
Did not see need for additional admin interface features for institutions. If that changes
insert it here
'''

#register the Institution
admin.site.register(Institution)

#Unregister and re-register UserAdmin to account for the user profile
admin.site.unregister(User)
admin.site.register(User,UserAdmin)