from django.db import models
from django import forms
from datetime import datetime
# Create your models here.

class usertable(models.Model):
	#userid = models.AutoField(primary_key=True)
	#active = models.BooleanField(default=False)
	username = models.CharField(max_length=100)
	useremail = models.EmailField(primary_key=True)  
	profession = models.CharField(max_length=100)
	age = models.IntegerField(default=18)
	opbalance = models.FloatField()
	password = models.CharField(max_length=20)
	class Meta:  
		db_table = "usertable"

class income(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	incomeid = models.AutoField(primary_key=True)
	description = models.CharField(max_length=100)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add=True)
	proof = models.FileField(upload_to='images',default='images/no-proof.png')

class expense(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	expenseid = models.AutoField(primary_key=True)
	description = models.CharField(max_length=100)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add=True)
	proof = models.FileField(upload_to='images',default='images/no-proof.png')

class generalreserve(models.Model):
	expenseid = models.ForeignKey(expense,on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	assetname = models.CharField(max_length=100)
	assetvalue = models.FloatField()
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	reserveamt = models.FloatField()
	GRid = models.AutoField(primary_key=True)
	proof = models.FileField(upload_to='images',default='images/no-proof.png')

class savings(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	expenseid = models.ForeignKey(expense,on_delete=models.CASCADE)
	savingsaccount = models.CharField(max_length=100)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add=True)
	savingsid = models.AutoField(primary_key=True)
	proof = models.FileField(upload_to='images',default='images/no-proof.png')

class credit(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	incomeid = models.ForeignKey(income,on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	creditaccount = models.CharField(max_length=100,primary_key=True)
	creditbalance = models.FloatField()
	proof = models.FileField(upload_to='images',default='images/no-proof.png')

class creditentry(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	creditaccount = models.ForeignKey(credit,on_delete=models.CASCADE)
	expenseid = models.ForeignKey(expense,on_delete=models.CASCADE)
	amountpaid = models.FloatField()
	date = models.DateTimeField(auto_now_add=True)
	creditentryid = models.AutoField(primary_key=True)
	proof = models.FileField(upload_to='images',default='images/no-proof.png')

class logentry(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	action = models.CharField(max_length=500)
	logtime = models.DateTimeField()

class taxation(models.Model):
	useremail = models.ForeignKey(usertable,on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now=True)
	duration = models.CharField(max_length=100) # fiscal year
	payableamt = models.FloatField()
	status = models.BooleanField()
	proof = models.FileField(upload_to='images',default='images/no-proof.png')