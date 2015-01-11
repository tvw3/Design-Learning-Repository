from django.db import models
from django.contrib.auth.models import User


#The institution with which a student or instructor is affiliated with
class Institution(models.Model):
	name = models.CharField(max_length=100)
	city = models.CharField(max_length=50)
	state = models.CharField(max_length=20)
	country = models.CharField(max_length=50)

	def __str__(self):
		return self.name

#This allows us to store additonal information about the user without having to extend the base
#user model. 
class UserProfile(models.Model):
	user = models.OneToOneField(User)
	#affiliated institution
	Institution = models.ForeignKey(Institution, null=True)
	#used for recovering password if forgotten
	SECURITY_QUESTIONS = (
			('teacher','What was the last name of your favorite grade teacher?'),
			('book','What was the first book you ever read?'),
			('pet','What was the name of your first pet?'),
			('father','In what city was your father born?'),
			('mother','In what city was your mother born?'),
			('car','What was the color of your first car?'),
		)
	security_question = models.CharField(max_length=7, choices=SECURITY_QUESTIONS, default='pet')
	security_answer = models.CharField(max_length=50, null=True)
	#whether or not a student or instructorhas given permission to use materials for research
	permission_granted = models.BooleanField(default=False)

#makes a new user profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

#automatically create a user profile for a new user
models.signals.post_save.connect(create_user_profile,sender=User)