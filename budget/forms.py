from django import forms
from .models import usertable, income, expense, generalreserve, savings, credit, creditentry, logentry
class UserSignUpForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = usertable 
		fields = "__all__"

class IncomeForm(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	date = forms.DateTimeField(widget=forms.HiddenInput())
	incomeid = forms.IntegerField(widget=forms.HiddenInput())
	class Meta:
		model = income
		fields = "__all__"

class ExpenseForm(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	date = forms.DateTimeField(widget=forms.HiddenInput())
	expenseid = forms.IntegerField(widget=forms.HiddenInput())
	class Meta:
		model = expense
		fields = "__all__"

class GeneralReserveForm(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	date = forms.DateTimeField(widget=forms.HiddenInput())
	expenseid = forms.IntegerField(widget=forms.HiddenInput())
	GRid = forms.IntegerField(widget=forms.HiddenInput())
	class Meta:
		model = expense
		fields = "__all__"

class SavingsForm(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	expenseid = forms.IntegerField(widget=forms.HiddenInput())
	date = forms.DateTimeField(widget=forms.HiddenInput())
	savingsid = forms.IntegerField(widget=forms.HiddenInput())
	class Meta:
		model = savings
		fields = "__all__"

class CreditForm(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	incomeid = forms.IntegerField(widget=forms.HiddenInput())
	date = forms.DateTimeField(widget=forms.HiddenInput())
	class Meta:
		model = credit
		fields = "__all__"

class CreditEntryForm(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	expenseid = forms.IntegerField(widget=forms.HiddenInput())
	date = forms.DateTimeField(widget=forms.HiddenInput())
	creditaccount = forms.ModelChoiceField(queryset = credit.objects.values_list('creditaccount',flat=True))
	creditentryid = forms.IntegerField(widget=forms.HiddenInput())
	class Meta:
		model = creditentry
		fields = "__all__"

class logentryform(forms.ModelForm):
	useremail = forms.CharField(widget=forms.HiddenInput())
	action = forms.CharField(widget=forms.HiddenInput())