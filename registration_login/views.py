from django.shortcuts import render, render_to_response

from django.template import RequestContext, loader

from django.core.context_processors import csrf
from django.core.mail import send_mail

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group

from django.http import HttpResponse, HttpResponseRedirect

from django.db import IntegrityError

from registration_login.models import UserProfile, Institution

from DLR.settings import EMAIL_HOST_USER

import random
import string

#This is the string that will be sent to users when they need to reset their password.
#The two arguments passed to this string should be the username and the password
passwordRecoverString = 'The DLR account associated with this email' + \
	' has requested a password recovery. Below is your account name and new temporary password:' + \
	'\n\nusername: %s\npassword: %s'

def userLogin(request):	
	'''
	UserLogin(request) - Login page. If login information is incorrect, or the user has been deactivated, then
	appropriate error messages are displayed.
	Parameters:
	    request - an http request
	Variables:
	    template - the templated Login.html file
	    context - the RequestContext object. Dictionary values are:
	        message- boolean of whether a message is to be passed.
	        messageContents - The message to be printed
	        csrf_token - Used in POST, must have the associated value returned by
	                    csrf(update)
	    username - username pulled out of Login.html template form
	    password - password pulled out of Login.html template form
	'''
	if request.method == 'GET':
		template = loader.get_template('registration_login/login.html')
		context = RequestContext(request, {'message': False,
			'messageContents': None,
			'csrf_token': csrf(request)})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		#verify that the username and password are correct
		username = request.POST['username']
		password = request.POST['pwd']
		user = authenticate(username=username, password=password)
		#successful login
		if user is not None:
			#sign in if their account is active
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/redirect')
			else:
				template = loader.get_template('registration_login/Login.html')
				context = RequestContext(request, {'message': True,
					'messageContents': 'Your account has been deactivated. Please contact an administrator.',
					'csrf_token': csrf(request),})
				return HttpResponse(template.render(context))
		else:
			#Failed to authenticate user, notify with username/password error messages
			template = loader.get_template('registration_login/Login.html')
			context = RequestContext(request,{'message': True,
			  	'messageContents': 'Invalid username or password. Please try again',
			  	'csrf_token':csrf(request),})
			return HttpResponse(template.render(context))

def userLogout(request):
	'''
	userLogout(request) - Simply used to logout the user and then redirect them to the home page
	Parameters:
		request - an Http request
	'''
	logout(request)
	return HttpResponseRedirect('/')

def forgotPassword(request):
	'''
	forgotPassword(request) - Page for password reset. Asks for a username in order to retrieve the security question to be used in
	the resetPassword handler.
	Parameters:
	    request - an http request
	Variables:
	    template - the templated ForgotPassword.html file
	    context - the RequestContext object. Dictionary values are:
	        message- boolean of whether a message is to be passed.
	        messageContents - The message to be printed
	        csrf_token - Used in POST, must have the associated value returned by
	                    csrf(update)
	    username - username pulled out of ForgotPassword.html template in order to check if the user exist
	'''
	if request.method == 'GET':
		template = loader.get_template('registration_login/ForgotPassword.html')
		context = RequestContext(request, {'message': False,
			'messageContents': None,
			'csrf_token': csrf(request)})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		username = request.POST['username']
		if User.objects.filter(username=username).exists():
			return HttpResponseRedirect('/reset-password/%s' % (username))
		else:
			template = loader.get_template('registration_login/ForgotPassword.html')
			context = RequestContext(request, {'message': True,
				'messageContents': 'Username was not found',
				'csrf_token': csrf(request)})
			return HttpResponse(template.render(context))

def resetPassword(request, username):
	'''
	recoverPassword(request, username) - Handler for user password recovery. Asks the user the security question associated with
	the account attached to username. While this method for recovering a password probably isn't the most secure, 
	it it suitable given the lack of intimate details about our users.
	Parameters:
		request - an http request
		username - the username for the account of the user in need of password recovery
	Variable:
		template - the tempalted RecoverPassword.html file
		context - The RequestContext object (state of the template). Dictionary values are:
			message - boolean of wheter a message is to be passed
			messageContents - the message to be printed to the user
			question - the security question to be answered
			csrf_token- Used in POST, must have the associated value returned by csrf(update)
		answer - the user's answer to the security question
	'''
	if request.method == 'GET':
		#result is a query set, select the first item
		user = User.objects.filter(username=username)[0]
		template = loader.get_template('registration_login/ResetPassword.html')
		context = RequestContext(request, {'message': False,
			'messageContents': None,
			'question': user.userprofile.get_security_question_display(),
			'csrf_token': csrf(request)})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		answer = request.POST['answer']
		#returns a queryset, so get the first (only) object in the set
		#otherwise the queryset object will be returned rather than the user object
		user = User.objects.filter(username=username)[0]
		#check if they answered the security question correctly
		if answer.lower() == user.userprofile.security_answer:
			#they did, send them an email containing their new, random password
			password = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
			#save the new password
			user.set_password(password)
			user.save()
			send_mail('DLR Password Reset',
				passwordRecoverString % (user.username, password),
				EMAIL_HOST_USER,
				(user.email,),
				fail_silently=False)
			return HttpResponseRedirect('/reset-password-success')
		else:
			#they did not, inform  them that the 
			template = loader.get_template('registration_login/ResetPassword.html')
			context = RequestContext(request, {'message': True,
			'messageContents': 'Invalid response, please try again.',
			'question': user.userprofile.get_security_question_display(),
			'csrf_token': csrf(request)})
			return HttpResponse(template.render(context))
			
def resetPasswordSuccess(request):
	'''
	resetPasswordSuccess(request) - Notfies the user that their password has been successfully reset, and that an email containing the new temporary
	password has been sent to the email associated with the username provided.
	Parameters:
		request - an Http Request
	'''
	return render_to_response('registration_login/PasswordResetSuccess.html')

def studentRegistration(request):
	'''
	studentRegistration(request) - Page for student registration. Requires that the student enter all user related information, including 
	selecting a security question, answer, as well as the institution they are attending. Unlike the instructor, students do not require verification.
	Arguments:
	    request - a http request
	Variables:
	    template - the templated Login.html file
	    context - the RequestContext object. Dictionary values are:
	        message- boolean of whether a message is to be passed. Leave empty
	                    if message
	        messageContents - The message to be printed
	        csrf_token - Used in POST, must have the associated value of
	                    csrf(update)
	    user - user object what will be saved to profile
	    group - user group that the user will be added to
	    profile - UserProfile object, the link between users and institutions
	    institutions - a query set of all institutions, used to show registered
	                    institutions to user
        security_questions - the security questions that a user can choose for password reset
        				which are defined in the UserProfile model
	'''    
	if request.method == 'GET':
		institutions = Institution.objects.all().order_by('name')
		security_questions = UserProfile.SECURITY_QUESTIONS
		template = loader.get_template('registration_login/studentRegistration.html')
		context = RequestContext(request, {'csrf_token': csrf(request),
			'institutions':institutions,
			'message': False,
			'messageContents': None,
			'securityQuestions': security_questions,})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		try:
			#Use form inputs to create a new User
			user = User.objects.create_user(request.POST['username'],request.POST['email'],request.POST['pwd'])
			#Fill out the rest of the attributes
			user.last_name = request.POST['lastName']
			user.first_name = request.POST['firstName']
			#Add the user to the student group
			group = Group.objects.get(name='Student')
			group.user_set.add(user)
			user.save()
			user.userprofile.institution = Institution.objects.get(id=request.POST['institutionID'])
			#Set the selected security question, as well as the answer for that question
			user.userprofile.security_question = request.POST['questionID']
			user.userprofile.security_answer = request.POST['answer'].lower()
			#Set if the student agreed to let their materials be used in research
			#if research does not exist in post, then the checkbox wasnt marked
			if 'research' in request.POST:
				user.userprofile.permission_granted = True
			else:
				user.userprofile.permission_granted = False
			user.userprofile.save()
			return HttpResponseRedirect('/student-registration-success')
			#username entered is already in use
		except IntegrityError as e:
		    institutions = Institution.objects.all().order_by('name')
		    template = loader.get_template('registration_login/studentRegistration.html')
		    context = RequestContext(request,{'institutions':institutions,
		                                      'message':True,
		                                      'messageContents':'Username already in use',
		                                      'csrf_token':csrf(request),})
		    return HttpResponse(template.render(context))

def studentRegistrationSuccess(request):
	'''
	studentRegistrationSuccess(request) - Notifies the student that they have successfully registered, and they can now log in.
	Parameters:
		request - an Http Request
	'''
	return render_to_response('registration_login/studentRegistrationSuccess.html')

def instructorRegistration(request):
	'''
	instructorRegistration(request) - Handles instructor registration. Requires the instructor to enter all user related information,
	as well as select a security question, answer, and institution. If the instructor's institution is not available, then they
	can register a new institution
	Arguments:
	    request - a http request
	Variables:
	    template - the templated Login.html file
	    context - the RequestContext object. Dictionary values are:
	        message- boolean of whether a message is to be passed. Leave empty
	                    if message
	        messageContents - The message to be printed
	        csrf_token - Used in POST, must have the associated value of
	                    csrf(update)
	    user - user object what will be saved to profile
	    group - user group that the user will be added to
	    profile - UserProfile object, the link between users and institutions
	    institutions - a query set of all institutions, used to show registered
	                    institutions to user
        security_questions - the security questions that a user can choose for password reset
        				which are defined in the UserProfile model
	''' 
	if request.method == 'GET':
		institutions = Institution.objects.all().order_by('name')
		security_questions = UserProfile.SECURITY_QUESTIONS
		template = loader.get_template('registration_login/instructorRegistration.html')
		context = RequestContext(request,{'institutions':institutions,
	                                      'message': False,
	                                      'messageContents': None,
	                                      'csrf_token':csrf(request),
	                                      'securityQuestions':security_questions})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		try:
			#create a new user from the post info
			user = User.objects.create_user(request.POST['username'],
				request.POST['email'],
				request.POST['pwd'])
			#set the rest of the user's information
			user.first_name = request.POST['firstName']
			user.last_name = request.POST['lastName']
			#Instructors must be manually approved
			#Requires user groups to be setup prior to user registration
			group = Group.objects.get(name='Instructor-pending')
			group.user_set.add(user)
			user.save()
			#set institution, if the instructor is adding a new one, then create the institution first before adding
			#check to make sure that the add institutio checkbox was checked
			if 'createSchool' in request.POST:
				inst_object = Institution()
				inst_object.name = request.POST['instName']
				inst_object.city = request.POST['city']
				inst_object.state = request.POST['state']
				inst_object.country = request.POST['country']
				inst_object.save()
			else:
				inst_object = Institution.objects.get(id=request.POST['institutionID'])
			user.userprofile.institution = inst_object
			#Set the selected security question, as well as the answer for that question
			user.userprofile.security_question = request.POST['questionID']
			user.userprofile.security_answer = request.POST['answer'].lower()
			#Set if the instructor agreed to let their materials be used in research
			#if research does not exist in post, then the checkbox wasnt marked
			if 'research' in request.POST:
				user.userprofile.permission_granted = True
			else:
				user.userprofile.permission_granted = False
			user.userprofile.save()
			return HttpResponseRedirect('/instructor-registration-success')
		except IntegrityError as e:
			institutions = Institution.objects.all().order_by('name')
			security_questions = UserProfile.SECURITY_QUESTIONS()
			template = loader.get_template('registration_login/instructorRegistration.html')
			context = RequestContext(request,{'institutions':institutions,
		                                      'message': True,
		                                      'messageContents': 'Username already in use',
		                                      'csrf_token':csrf(request),
		                                      'securityQuestions':security_questions})
			return HttpResponse(template.render(context))

def instructorRegistrationSuccess(request):
	'''
	instructorRegistrationSuccess(request) - Inform the instructor that they have successfully registered and that they will be notified when
	their status as a professor at the provided institution has been verified
	Parameters:
		request - an Http Request
	'''
	return render_to_response('registration_login/instructorRegistrationSuccess.html')	

def approvalPending(request):
	'''
	approvalPending(request) - Page that informs instructors that they cannot log in until their 
	account and status as a professor has been verified.
	Parameters:	
		request - an Http Request
	'''
	#User can't access anything anyways, so log them out out automatically
	logout(request)
	return render_to_response('registration_login/approvalPending.html')

def loginRedirect(request):
	'''
	loginRedirect(request) - redirects the user to the proper home page based on user permission. If the
	user requesting the page is not authenticated, then redirect to the home page
	Parameters:
		request - an Http request
	'''
	#make sure a valid user is logged in
	if request.user.is_authenticated():
		#redirect the user based on their permissions group
		if request.user.groups.filter(name='Student').exists():
			return HttpResponseRedirect('/student/%s/home' % request.user.username)
		elif request.user.groups.filter(name='instructor').exists():
			return HttpResponseRedirect('/instructor/%s/home' % request.user.username)
		elif request.user.groups.filter(name='instructor-pending').exists():
			return HttpResponseRedirect('approval-pending')
	#if not, then return them to the home page
	else:
		return HttpResponseRedirect('/')

























