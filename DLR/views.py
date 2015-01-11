'''
This module contains only the view for the home page, which isn't really part of any app
but rather the project as a whole
'''

from django.shortcuts import render_to_response

def home(request):
	return render_to_response('home/Overview.html')