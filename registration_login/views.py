from django.shortcuts import render_to_response

from django.template import RequestContext, loader

from django.core.context_processors import csrf
from django.core.mail import send_mail

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect

from django.db import IntegrityError

from registration_login.models import UserProfile, Institution

from DLR.settings import EMAIL_HOST_USER

import random
import string

# This is the string that will be sent to users when they need to reset their password.
# The two arguments passed to this string should be the username and the password
RESET_STRING = 'The DLR account associated with this email' + \
    ' has requested a password recovery. Below is your account name and new temporary password:' + \
    '\n\nusername: %s\npassword: %s'


def user_login(request):
    """
    Verifies that a user exists and logs them into the system
    :param request: http request
    :return: Either the form with applicable error messages, or sends the user to the redirect handler
    """
    if request.method == 'GET':
        template = loader.get_template('registration_login/login.html')
        context = RequestContext(
            request,
            {'message': False,
             'messageContents': None,
             'csrf_token': csrf(request)})
        return HttpResponse(template.render(context))
    elif request.method == 'POST':
        # verify that the username and password are correct
        username = request.POST['username']
        password = request.POST['pwd']
        user = authenticate(username=username, password=password)
        # successful login
        if user is not None:
            # sign in if their account is active
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/redirect')
            else:
                template = loader.get_template('registration_login/Login.html')
                context = RequestContext(
                    request,
                    {'message': True,
                     'messageContents': 'Your account has been deactivated. Please contact an administrator.',
                     'csrf_token': csrf(request)})
                return HttpResponse(template.render(context))
        else:
            # Failed to authenticate user, notify with username/password error messages
            template = loader.get_template('registration_login/Login.html')
            context = RequestContext(
                request,
                {'message': True,
                 'messageContents': 'Invalid username or password. Please try again',
                 'csrf_token':csrf(request),})
            return HttpResponse(template.render(context))


def user_logout(request):
    """
    Logs the user out and returns them to the home page
    :param request: an http request
    :return: redirect to the homepage
    """
    logout(request)
    return HttpResponseRedirect('/')


def forgot_password(request):
    """
    Handler for users that wish to begin the password recovery process
    :param request: an http request
    :return: Either the form with any applicable error messages, or a redirect to the password reset form
    """
    if request.method == 'GET':
        template = loader.get_template('registration_login/ForgotPassword.html')
        context = RequestContext(
            request,
            {'message': False,
             'messageContents': None,
             'csrf_token': csrf(request)})
        return HttpResponse(template.render(context))
    elif request.method == 'POST':
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            return HttpResponseRedirect('/reset-password/%s' % (username))
        else:
            template = loader.get_template('registration_login/ForgotPassword.html')
            context = RequestContext(
                request,
                {'message': True,
                 'messageContents': 'Username was not found',
                 'csrf_token': csrf(request)})
            return HttpResponse(template.render(context))


def reset_password(request, username):
    """
    Form for resetting the password, this will send a temporary password to the email on file
    given the user successfully answers their security question.
    :param request: an http request
    :param username: the username of the user trying to reset their password
    :return: Either a form with any applicable error messages, or a redirect to the reset success page.
    """
    if request.method == 'GET':
        # result is a query set, select the first item
        user = User.objects.filter(username=username)[0]
        template = loader.get_template('registration_login/ResetPassword.html')
        context = RequestContext(
            request,
            {'message': False,
             'messageContents': None,
             'question': user.userprofile.get_security_question_display(),
             'csrf_token': csrf(request)})
        return HttpResponse(template.render(context))
    elif request.method == 'POST':
        answer = request.POST['answer']
        # returns a queryset, so get the first (only) object in the set
        # otherwise the queryset object will be returned rather than the user object
        user = User.objects.filter(username=username)[0]
        # check if they answered the security question correctly
        if answer.lower() == user.userprofile.security_answer:
            # they did, send them an email containing their new, random password
            password = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
            # save the new password
            user.set_password(password)
            user.save()
            send_mail(
                'DLR Password Reset',
                RESET_STRING % (user.username, password),
                EMAIL_HOST_USER,
                (user.email,),
                fail_silently=False)
            return HttpResponseRedirect('/reset-password-success')
        else:
            # they did not, inform  them that their response is invalid
            template = loader.get_template('registration_login/ResetPassword.html')
            context = RequestContext(
                request,
                {'message': True,
                 'messageContents': 'Invalid response, please try again.',
                 'question': user.userprofile.get_security_question_display(),
                 'csrf_token': csrf(request)})
            return HttpResponse(template.render(context))


def reset_password_success(request):
    """
    Page notifying a user that their password reset email has been sent
    :param request: an http request
    :return: the success page
    """
    return render_to_response('registration_login/PasswordResetSuccess.html')


def student_registration(request):
    """
    Form for student registration. Requires the student to enter all relevant user information,
    as well as information about their school.
    :param request: an http request
    :return: Either the form with any applicable error messages (if any), or a redirect to the registartion
        success page
    """
    if request.method == 'GET':
        institutions = Institution.objects.all().order_by('name')
        security_questions = UserProfile.SECURITY_QUESTIONS
        template = loader.get_template('registration_login/studentRegistration.html')
        context = RequestContext(
            request,
            {'csrf_token': csrf(request),
             'institutions':institutions,
             'message': False,
             'messageContents': None,
             'securityQuestions': security_questions,})
        return HttpResponse(template.render(context))
    elif request.method == 'POST':
        try:
            # Use form inputs to create a new User
            user = User.objects.create_user(request.POST['username'],request.POST['email'],request.POST['pwd'])
            # Fill out the rest of the attributes
            user.last_name = request.POST['lastName']
            user.first_name = request.POST['firstName']
            # Add the user to the student group
            group = Group.objects.get(name='Student')
            group.user_set.add(user)
            user.save()
            user.userprofile.institution = Institution.objects.get(id=request.POST['institutionID'])
            # Set the selected security question, as well as the answer for that question
            user.userprofile.security_question = request.POST['questionID']
            user.userprofile.security_answer = request.POST['answer'].lower()
            # Set if the student agreed to let their materials be used in research
            # if research does not exist in post, then the checkbox wasnt marked
            if 'research' in request.POST:
                user.userprofile.permission_granted = True
            else:
                user.userprofile.permission_granted = False
            user.userprofile.save()
            return HttpResponseRedirect('/student-registration-success')
            # username entered is already in use
        except IntegrityError as e:
            institutions = Institution.objects.all().order_by('name')
            template = loader.get_template('registration_login/studentRegistration.html')
            context = RequestContext(
                request,
                {'institutions': institutions,
                 'message': True,
                 'messageContents': 'Username already in use',
                 'csrf_token': csrf(request)})
            return HttpResponse(template.render(context))


def student_registration_success(request):
    """
    Informs the student that they have successfully registered with the app
    :param request: an http request
    :return: the success page
    """
    return render_to_response('registration_login/studentRegistrationSuccess.html')


def instructor_registration(request):
    """
    Form for instructor registration. In addition to user and account information, instructors must also select
    their affiliated institution. If the institution is not available in the drop-down, then they can also register
    their institution.
    :param request: an http request
    :return: Either the form with any applicable error messages (if any) or a redirect to the registration success
    page
    """
    if request.method == 'GET':
        institutions = Institution.objects.all().order_by('name')
        security_questions = UserProfile.SECURITY_QUESTIONS
        template = loader.get_template('registration_login/instructorRegistration.html')
        context = RequestContext(
            request,
            {'institutions': institutions,
             'message': False,
             'messageContents': None,
             'csrf_token': csrf(request),
             'securityQuestions': security_questions})
        return HttpResponse(template.render(context))
    elif request.method == 'POST':
        try:
            # create a new user from the post info
            user = User.objects.create_user(
                request.POST['username'],
                request.POST['email'],
                request.POST['pwd'])
            # set the rest of the user's information
            user.first_name = request.POST['firstName']
            user.last_name = request.POST['lastName']
            # Instructors must be manually approved
            # Requires user groups to be setup prior to user registration
            group = Group.objects.get(name='Instructor-pending')
            group.user_set.add(user)
            user.save()
            # set institution, if the instructor is adding a new one, then create the institution first before adding
            # check to make sure that the add institutio checkbox was checked
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
            # Set the selected security question, as well as the answer for that question
            user.userprofile.security_question = request.POST['questionID']
            user.userprofile.security_answer = request.POST['answer'].lower()
            # Set if the instructor agreed to let their materials be used in research
            # if research does not exist in post, then the checkbox wasnt marked
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
            context = RequestContext(
                request,
                {'institutions': institutions,
                 'message': True,
                 'messageContents': 'Username already in use',
                 'csrf_token': csrf(request),
                 'securityQuestions': security_questions})
            return HttpResponse(template.render(context))


def instructor_registration_success(request):
    """
    Informs the instructor that they have successfully registered with the app, and they will be notified when
    their status as an instructor at the institution selected is verified
    :param request: an http request
    :return: the success page
    """
    return render_to_response('registration_login/instructorRegistrationSuccess.html')


def approval_pending(request):
    """
    Page shown when an instructor that has registered but has not been verified attempts to login.
    Informs them that their account is still being verified
    :param request: an http request
    :return: the approval pending page
    """
    # User can't access anything anyways, so log them out out automatically
    logout(request)
    return render_to_response('registration_login/approvalPending.html')


@login_required()
def login_redirect(request):
    """
    Redirects the user to the appropriated page based on their group
    :param request: an http request
    :return: The home page for verified instructors and students. The approval pending for instructors
    still waiting on approval.
    """
    # redirect the user based on their permissions group
    if request.user.groups.filter(name='Student').exists():
        return HttpResponseRedirect('/student/%s/home' % request.user.username)
    elif request.user.groups.filter(name='instructor').exists():
        return HttpResponseRedirect('/instructor/%s/home' % request.user.username)
    elif request.user.groups.filter(name='instructor-pending').exists():
        return HttpResponseRedirect('/approval-pending')

























