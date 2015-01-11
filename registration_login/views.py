from django.shortcuts import render

from django.template import RequestContext, loader

from django.core.context_processors import csrf

from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse

def userLogin(request):	
	'''
	UserLogin(request) - view handler for logging into the app
	Arguments:
	    request - an http request
	Variables:
	    template - the templated Login.html file
	    context - the RequestContext object. Dictionary values are:
	        message- boolean of whether a message is to be passed. Leave empty
	                    if no message
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
				#TODO CHANGEEVERYTHING BELOW THIS POINT FOR THIS FUNCTION
				logout(request)
				return HttpResponse('It worked')
			else:
				return HttpResponse('didntwork')
		else:
			return HttpResponse('didnt work')

def forgotPassword(request):
	if request.method == 'GET':
		template = loader.get_template('registration_login/ForgotPassword.html')
		context = RequestContext(request, {})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		pass