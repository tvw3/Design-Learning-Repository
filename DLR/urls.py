from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'DLR.views.home', name='home'),
    url(r'^login/', 'registration_login.views.userLogin', name='login'),
    url(r'^logout/', 'registration_login.views.userLogout', name='logout'),
    url(r'^forgot-password/', 'registration_login.views.forgotPassword', name='forgot-password'),
    url(r'^reset-password/(?P<username>\w+)/', 'registration_login.views.resetPassword', name='reset-password'),
    url(r'^reset-password-success/', 'registration_login.views.resetPasswordSuccess', name='reset-success'),
    url(r'^student-registration/', 'registration_login.views.studentRegistration', name='student-registration'),
    url(r'^instructor-registration/', 'registration_login.views.instructorRegistration', name='instructor-registration'),
    url(r'^student-registration-success/' ,'registration_login.views.studentRegistrationSuccess', name='student-registration-success'),
    url(r'^instructor-registration-success/', 'registration_login.views.instructorRegistrationSuccess', name='instructor-registration-success'),
    url(r'^approval-pending/', 'registration_login.views.approvalPending', name='approval-pending'),
    url(r'^redirect/', 'registration_login.views.loginRedirect',name='redirect'),
    url(r'^admin/', include(admin.site.urls)),
)
