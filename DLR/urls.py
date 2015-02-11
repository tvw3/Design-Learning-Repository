from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^$', 'DLR.views.home', name='home'),
    url(r'^login/', 'registration_login.views.user_login', name='login'),
    url(r'^logout/', 'registration_login.views.user_logout', name='logout'),
    url(r'^forgot-password/', 'registration_login.views.forgot_password', name='forgot-password'),
    url(r'^reset-password/(?P<username>\w+)/', 'registration_login.views.reset_password', name='reset-password'),
    url(r'^reset-password-success/', 'registration_login.views.reset_password_success', name='reset-success'),
    url(r'^student-registration/', 'registration_login.views.student_registration', name='student-registration'),
    url(r'^instructor-registration/', 'registration_login.views.instructor_registration', name='instructor-registration'),
    url(r'^student-registration-success/', 'registration_login.views.student_registration_success', name='student-registration-success'),
    url(r'^instructor-registration-success/', 'registration_login.views.instructor_registration_success', name='instructor-registration-success'),
    url(r'^approval-pending/', 'registration_login.views.approval_pending', name='approval-pending'),
    url(r'^redirect/', 'registration_login.views.login_redirect' ,name='redirect'),
    url(r'^admin/', include(admin.site.urls)),
)
