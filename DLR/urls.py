from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'DLR.views.home', name='home'),
    url(r'^login/', 'registration_login.views.userLogin', name='login'),
    url(r'^logout/', 'registration_login.views.userLogout', name='logout'),
    url(r'^forgot-password/', 'registration_login.views.forgotPassword', name='forgot-password'),
    url(r'^recover-password/(?P<username>\w+)/', 'registration_login.views.recoverPassword', name='recover-password'),
    url(r'^admin/', include(admin.site.urls)),
)
