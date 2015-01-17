from django.shortcuts import render, render_to_response

from django.template import RequestContext, loader

from django.core.context_processors import csrf
from django.core.mail import send_mail

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect

from registration_login.models import UserProfile, Institution

from DLR.settings import EMAIL_HOST_USER

import random
import string

passwordRecoverString = 'The DLR account associated with this email' + \
	' has requested a password recovery. Below is your account name and new temporary password:' + \
	'\n\nusername: %s\npassword: %s'

def userLogin(request):	
	'''
	UserLogin(request) - view handler for logging into the app
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
	userLogout(request) - the handler for logging out a user
	Parameters:
		request - an Http request
	'''
	logout(request)
	return HttpResponseRedirect('/')

def forgotPassword(request):
	'''
	forgotPassword(request) - view handler for beginning password recovery
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
	recoverPassword(request, username) - Handler for user password recovery. While this method
	for recovering a password probably isn't the most secure, it it suitable given the lack of
	intimate details about our users.
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
		#get the user 
		user = User.objects.filter(username=username)[0]
		#check if they answered the security question correctly
		if answer == user.userprofile.security_answer:
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
	resetPasswordSuccess(request) - Simple handler that renders the success template
	Parameters:
		request - an Http Request
	'''
	return render_to_response('registration_login/PasswordResetSuccess.html')

def studentRegistration(request):
	'''
	studentSignup(request) - view handler for instructor registration
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
	'''    
	if request.method == 'GET':
		institutions = Institution.objects.all().order_by('name')
		template = loader.get_template('registration_login/studentRegistration.html')
		context = RequestContext(request, {'csrf_token': csrf(request),
			'institutions':institutions,})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		pass




























