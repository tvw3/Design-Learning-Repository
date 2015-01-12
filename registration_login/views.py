from django.shortcuts import render

from django.template import RequestContext, loader

from django.core.context_processors import csrf

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect

from registration_login.models import UserProfile

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
				return HttpResponse('/redirect')
			else:
				template = loader.get_template('Login.html')
				context = RequestContext(request, {'message': True,
												'messageContents': 'Your account has been deactivated. Please contact an administrator.',
												'csrf_token': csrf(request),})
				return HttpResponse(template.render(context))
		else:
			#Failed to authenticate user, notify with username/password error message
			template = loader.get_template('Login.html')
			context = RequestContext(request,{'message': True,
											  'messageContents': 'Invalid username or password. Please try again',
											  'csrf_token':csrf(request),})
			return HttpResponse(template.render(context))

def userLogout(request):
	'''
	userLogout(request) - the handler for logging out a suer
	Parameters:
		request - an Http request
	'''
	logout(request)
	HttpResponseRedirect('/')

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
			return HttpResponseRedirect('/recover-password/%s' % (username))
		else:
			template = loader.get_template('registration_login/ForgotPassword.html')
			context = RequestContext(request, {'message': True,
				'messageContents': 'Username was not found',
				'csrf_token': csrf(request)})
			return HttpResponse(template.render(context))

def recoverPassword(request, username):
	'''

	'''
	if request.method == 'GET':
		#result is a query set, select the first item
		user = User.objects.filter(username=username)[0]
		template = loader.get_template('registration_login/RecoverPassword.html')
		context = RequestContext(request, {'message': False,
			'messageContents': None,
			'question': UserProfile.SECURITY_QUESTIONS(user.userprofile.security_question),
			'csrf_token': csrf(request)})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		pass


























