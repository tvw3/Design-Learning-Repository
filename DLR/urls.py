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
    url(r'^admin/', include(admin.site.urls)),
)
