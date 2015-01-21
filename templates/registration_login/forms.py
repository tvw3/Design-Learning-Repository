from django import forms

class loginForm(forms.Form):
	username = forms.CharField(max_length=50,required=True)
	email = forms.EmailField(required=True)
