from django.db import models

from django.utils import timezone

from django.contrib.auth.models import User

from registration_login.models import Institution


class Course(models.Model):
    # ie cs249, cs386
    course_ID = models.CharField(max_length=20)
    # Name of the instructor
    instructor = models.ForeignKey(User)
    institution = models.ForeignKey(Institution)
    date_created = models.DateTimeField('Date Created', auto_now_add=True)
    date_ending = models.DateTimeField(null=True)
    
    # Current course based off semester system ~5months
    def is_current(self):
        return timezone.now() <= self.date_ending
    
    def __str__(self):
        return "%s: %s - Instructor: %s %s" % (
            self.course_ID,
            self.institution,
            self.instructor.first_name,
            self.instructor.last_name)
