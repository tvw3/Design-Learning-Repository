from django.shortcuts import render

from djang.template import RequestContext, loader

import timezone
import datetime

from django.core.mail import send_mail
from django.core.context_processors import csrf

from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group

from django.contrib.auth.decorators import login_required, user_passes_test

from django.http import HttpResponse, HttpResponseRedirect

from course.models import Course

#Days in a semester based off of 16 weeks with approximately a 2 week buffer
DAYS_IN_SEMESTER = 125
#Days in a quarter, based off roughly have of a semester with approximately a 2 week buffer
DAYS_IN_QUARTER = 70
#message to be send to students, notifying them that a class has been created
EMAIL_STRING = '%s %s has created the course %s and listed you as a student. Please go to www.dlr-relics.rhcloud.com' \
	'to login and sign up. If you have not used dlr before, be sure that you register as a student prior to attempting' \
	'to sign up for the course'

def isInstructor(user):
	'''
	isInstructor(user,validUsername) - returns whether or not the user is an instructor
	Arguments:
		user - A user object to verify for instructor status
	'''
	return user.groups.filter(name='instructor').exists()

def isCorrectUser(user, correctUsername):
	'''
	isCorrectUser(user, correctUsername) - verifies the user is indeed the person that the content belongs to
	Arguements:
		user - A user object to verify
		correctUsername - The username the content being requested belongs to
	'''
	return user.username == correctUsername

#obviously /permission-denied isn't a login url, but it is better to direct users to a page
#that gives them actual information as to why they cannot view a page, rather than just show them a 
#login page with no useful info

@user_passes_test(isCorrectUser(request.user, username), login_url='/permission-denied')
@user_passes_test(isInstructor(request.user), login_url='/permission-denied')
@login_required()
def addCourse(request, username):
	'''
	addCourse(request, username) - allows instructors to create a new course and email all students
		to notify them that the course has been created
	Arguments:
		request - an http request
		username - the username of the user that this content belongs to
	'''
	if request.method == 'GET':
		template = loader.get_template('course/AddCourse.html')
		context = RequestContext(request,{'csrf_token':csrf(request)})
		return HttpResponse(template.redner(context))
	elif request.method == 'POST':
		#create a new course
		course = Course()
		#set course fields based on the input and creating instructor
		course.course_ID = request.POST['courseID']
		course.instructor = request.user
		course.institution = request.user.userprofile.institution
		#set term length
		if request.POST['term'] == 'semester':
			term_length = DAYS_IN_SEMESTER
		else:
			term_length = DAYS_IN_QUARTER
		#set the end date for the course
		course.date_ending = timezone.now() + datetime.timedelta(days=term_length)
		course.save()
		#send an email to all emailsentered into the text area, notifying them that they have been
		#invited to a course
		send_mail('DLR Course Registration',
			EMAIL_STRING % (request.user.first_name, request.user.last_name, course_ID),
			request.user.email,
			request.POST.get('emails').split(),
			fail_silently=False)
		return HttpResponseRedirect('/instructor/%s/course-add-successful' % request.user.username)
           

