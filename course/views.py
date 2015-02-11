from django.shortcuts import render_to_response

from django.template import RequestContext, loader

from django.utils import timezone

import datetime

from django.core.mail import send_mail
from django.core.context_processors import csrf

from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group

from django.contrib.auth.decorators import login_required, user_passes_test

from django.http import HttpResponse, HttpResponseRedirect

from course.models import Course

# Days in a semester based off of 16 weeks with approximately a 2 week buffer
DAYS_IN_SEMESTER = 125
# Days in a quarter, based off roughly have of a semester with approximately a 2 week buffer
DAYS_IN_QUARTER = 70
# message to be send to students, notifying them that a class has been created
EMAIL_STRING = '%s %s has created the course %s and listed you as a student. Please go to www.dlr-relics.rhcloud.com' \
    'to login and sign up. If you have not used dlr before, be sure that you register as a student prior to attempting' \
    'to sign up for the course'


def is_instructor(user):
    """
    Checks whether or not a user is an instructor
    :param user: the user being verified
    :return: A boolean indicating whether or not the user is an instructor.
    """
    return user.groups.filter(name='instructor').exists()


def is_correct_user(user, correct_username):
    """
    Verifies that user is in fact the correct user to access specific resources
    :param user: The user object that is trying to access resources
    :param correct_username: the valid username for accessing this content
    :return: a boolean indicating whether user's username matches the correct username
    """
    return user.username == correct_username

# obviously /permission-denied isn't a login url, but it is better to direct users to a page
# that gives them actual information as to why they cannot view a page, rather than just show them a
# login page with no useful info


@user_passes_test(is_correct_user(request.user, username), login_url='/permission-denied')
@user_passes_test(is_instructor(request.user), login_url='/permission-denied')
@login_required()
def add_course(request, username):
    """
    Allows instructors to create a new course
    :param request: an http request
    :param username: the username of the instructor that is creating the course
    :return: For get requests, the add course form. For  post, redirects the user to the success page
    """
    if request.method == 'GET':
        template = loader.get_template('course/AddCourse.html')
        context = RequestContext(request, {'csrf_token': csrf(request)})
        return HttpResponse(template.render(context))
    elif request.method == 'POST':
        # create a new course
        course = Course()
        # set course fields based on the input and creating instructor
        course.course_ID = request.POST['courseID']
        course.instructor = request.user
        course.institution = request.user.userprofile.institution
        # set term length
        if request.POST['term'] == 'semester':
            term_length = DAYS_IN_SEMESTER
        else:
            term_length = DAYS_IN_QUARTER
        # set the end date for the course
        course.date_ending = timezone.now() + datetime.timedelta(days=term_length)
        course.save()
        # send an email to all emails entered into the text area, notifying them that they have been
        # invited to a course
        send_mail(
            'DLR Course Registration',
            EMAIL_STRING % (request.user.first_name, request.user.last_name, course.course_ID),
            request.user.email,
            request.POST.get('emails').split(),
            fail_silently=False)
        return HttpResponseRedirect('/instructor/%s/course-add-successful' % request.user.username)


def course_add_successful(request, username):
    """
    Page that notifies the user that they have successfully created a course
    :param request: an http request
    :param username: the username of the user creating the course
    :return: an http response, serving the static page
    """
    return render_to_response('course/AddCourseSuccessful.html')


