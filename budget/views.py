from django.http import HttpResponse
#import pandas as pd 

#def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")

#def loadfirst(req):
	#y=20
	#list1 = []
	#for i in range(2,21,2):
		#list1.append(i)
	#return render(req,'test.html')

#def loadsecond(req):
	#return render(req,'index1#.html')
import os 
from datetime import datetime
from django.conf import settings
from django.db.models import Sum
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect  
from .forms import UserSignUpForm, IncomeForm, ExpenseForm, GeneralReserveForm, SavingsForm, CreditForm, CreditEntryForm, logentryform
from .models import usertable, income, expense, generalreserve, savings, credit, creditentry, logentry, taxation

# Create your views here.  

#global userdetails

def showdetails(request):
	request.session['formsubmitted'] = 'nil'
	if request.session['updordel'] == 'update':
		indicator = "Updated Successfully!"
	elif request.session['updordel'] == 'delete':
		indicator = "Deleted Successfully!"
	else:
		indicator = "Nothing"
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	incomeobjects = income.objects.filter(useremail=userdetails['useremail']).order_by('-date')
	expenseobjects = expense.objects.filter(useremail=userdetails['useremail']).order_by('-date')
	creditentryobjects = creditentry.objects.filter(useremail=userdetails['useremail']).order_by('-date')
	generalreserveobjects = generalreserve.objects.filter(useremail=userdetails['useremail']).order_by('-date')
	creditobjects = credit.objects.filter(useremail=userdetails['useremail']).order_by('-date')
	savingsobjects = savings.objects.filter(useremail=userdetails['useremail']).order_by('-date')
	return render(request,'showdetails.html',{'indicator':indicator,'liquid':liquidcash(userdetails['opbalance']),'userdetails':userdetails,'incomeobjects':incomeobjects,'expenseobjects':expenseobjects,'creditentryobjects':creditentryobjects,'generalreserveobjects':generalreserveobjects,'creditobjects':creditobjects,'savingsobjects':savingsobjects})

def editobject(request, entity, entityid):
	request.session['formsubmitted'] = 'nil'
	if entity == 'income':
		incomeobj = income.objects.get(incomeid = entityid)
		return render(request,'updateincome.html',{'incomeobj':incomeobj})
	elif entity == 'expense':
		expenseobj = expense.objects.get(expenseid = entityid)
		return render(request,'updateexpense.html',{'expenseobj':expenseobj})
	elif entity == 'generalreserve':
		generalreserveobj = generalreserve.objects.get(GRid = entityid)
		return render(request,'updategr.html',{'generalreserveobj':generalreserveobj})
	elif entity == 'savings':
		savingsobj = savings.objects.get(savingsid = entityid)
		return render(request,'updatesavings.html',{'savingsobj':savingsobj})
	elif entity == 'creditentry':
		creditentryobj = creditentry.objects.get(creditentryid = entityid)
		return render(request,'updatecreditentry.html',{'creditentryobj':creditentryobj})
	else:
		pass

def editcredit(request, entity, entityid):
	request.session['formsubmitted'] = 'nil'
	if entity == 'credit':
		creditobj = credit.objects.get(creditaccount = entityid)
		return render(request,'updatecredit.html',{'creditobj':creditobj})
	else:
		pass

def updatecredit(request, entity, entityid):
	request.session['formsubmitted'] = 'nil'
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	request.session['updordel'] = 'update'
	if entity == "credit":
		if request.method == "POST":
			#print(credit.objects.get(creditaccount=entityid).incomeid.incomeid)
			updatedbalance = income.objects.get(incomeid=credit.objects.get(creditaccount=entityid).incomeid.incomeid).amount - float(request.POST.get('creditbalance'))
			income.objects.filter(incomeid=credit.objects.get(creditaccount=entityid).incomeid.incomeid).update(description="Credit Borrowed From" + request.POST.get('creditac'),amount=request.POST.get('creditbalance'))
			credit.objects.filter(creditaccount=entityid).update(creditaccount=request.POST.get('creditac'),creditbalance=float(request.POST.get('creditbalance')))
			usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] - updatedbalance)
			logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated credit registered details of account holder " + request.POST.get('creditac'),logtime=datetime.now())
			logobj.save()
			CalculateTax(request)
		return redirect('/showdetails')

def deletecredit(request, entity, entityid):
	request.session['formsubmitted'] = 'nil'
	request.session['updordel'] = 'delete'
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	if entity == 'credit':
		#print(credit.objects.get(creditaccount=entityid).proof.path)
		try:
			if(str(credit.objects.get(creditaccount=entityid).proof.path).find('no-proof.png')==-1):
				os.remove(credit.objects.get(creditaccount=entityid).proof.path)
				os.remove(income.objects.get(incomeid = credit.objects.get(creditaccount=entityid).incomeid.incomeid).proof.path)
				if(creditentry.objects.filter(creditaccount=credit.objects.get(creditaccount=entityid)).exists()):
					os.remove(creditentry.objects.get(creditaccount=credit.objects.get(creditaccount=entityid)).proof.path)
		except:
			pass
		#print(workornotasdf)
		usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] - income.objects.get(incomeid=credit.objects.get(creditaccount=entityid).incomeid.incomeid).amount)
		income.objects.filter(incomeid=credit.objects.get(creditaccount=entityid).incomeid.incomeid).delete()
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Deleted credit details of account " + entityid,logtime=datetime.now())
		logobj.save()
		CalculateTax(request)
		return redirect('/showdetails')

def updateobject(request, entity, entityid):
	request.session['formsubmitted'] = 'nil'
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	request.session['updordel'] = 'update'
	if entity == 'income':
		if request.method == "POST":
			updatedbalance = income.objects.get(incomeid=entityid).amount - float(request.POST.get('amount'))
			income.objects.filter(incomeid=entityid).update(description=request.POST.get('description'),amount=request.POST.get('amount'))
			usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] - updatedbalance)
			logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated income entry of description " + request.POST.get('description'),logtime=datetime.now())
			logobj.save()
			CalculateTax(request)
		return redirect('/showdetails')
		#return render(request,'showdetails.html',{'incomeobjects':incomeobjects,'expenseobjects':expenseobjects,'creditentryobjects':creditentryobjects,'generalreserveobjects':generalreserveobjects,'creditobjects':creditobjects,'savingsobjects':savingsobjects})
	elif entity == 'expense':
		if request.method == "POST":
			updatedbalance = expense.objects.get(expenseid=entityid).amount - float(request.POST.get('amount'))
			expense.objects.filter(expenseid=entityid).update(description=request.POST.get('description'),amount=request.POST.get('amount'))
			usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + updatedbalance)
			logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated expense entry of description " + request.POST.get('description'),logtime=datetime.now())
			logobj.save()
		return redirect('/showdetails')
	elif entity == 'generalreserve':
		if request.method == "POST":
			updatedbalance = generalreserve.objects.get(GRid = entityid).reserveamt - float(request.POST.get('reserveamt'))
			expense.objects.filter(expenseid = generalreserve.objects.get(GRid = entityid).expenseid.expenseid).update(description="General Reserve for " + request.POST.get('assetname'),amount=float(request.POST.get('reserveamt')))
			generalreserve.objects.filter(GRid=entityid).update(assetname=request.POST.get('assetname'),assetvalue=request.POST.get('assetvalue'),reserveamt=request.POST.get('reserveamt'))
			usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + updatedbalance)
			logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated generalreserve made for " + request.POST.get('assetname'),logtime=datetime.now())
			logobj.save()
		return redirect('/showdetails')
	elif entity == 'savings':
		if request.method == "POST":
			updatedbalance = savings.objects.get(savingsid = entityid).amount - float(request.POST.get('amount'))
			expense.objects.filter(expenseid = savings.objects.get(savingsid = entityid).expenseid.expenseid).update(description="Savings Made for " + request.POST.get('savingsaccount'),amount=float(request.POST.get('amount')))
			savings.objects.filter(savingsid=entityid).update(savingsaccount=request.POST.get('savingsaccount'),amount=request.POST.get('amount'))
			usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + updatedbalance)
			logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated savings made for " + request.POST.get('savingsaccount'),logtime=datetime.now())
			logobj.save()
		return redirect('/showdetails')
	elif entity == 'creditentry':
		if request.method == "POST":
			updatedbalance = creditentry.objects.get(creditentryid = entityid).amountpaid - float(request.POST.get('amountpaid'))
			expense.objects.filter(expenseid = creditentry.objects.get(creditentryid = entityid).expenseid.expenseid).update(description="Paid back credit Borrowed from " + request.POST.get('creditaccount'),amount=float(request.POST.get('amountpaid')))
			creditentry.objects.filter(creditentryid=entityid).update(creditaccount=credit.objects.get(creditaccount=request.POST.get('creditaccount')),amountpaid=request.POST.get('amountpaid'))
			usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + updatedbalance)
			logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated Credit entry made for " + request.POST.get('creditaccount'),logtime=datetime.now())
			logobj.save()
		return redirect('/showdetails')
	else:
		pass

def showloghistory(request):
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	logentries = logentry.objects.filter(useremail=userdetails['useremail']).order_by('-logtime')
	return render(request,'loghistory.html',{'logentries':logentries})

def deleteobject(request, entity, entityid):
	#global userdetails
	request.session['formsubmitted'] = 'nil'
	request.session['updordel'] = 'delete'
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	if entity == 'income':
		try:
			if(str(income.objects.get(incomeid=entityid).proof.path).find('no-proof.png')==-1):
				os.remove(income.objects.get(incomeid=entityid).proof.path)
			if(credit.objects.filter(incomeid = income.objects.get(incomeid=entityid)).exists()):
				os.remove(credit.objects.get(incomeid = income.objects.get(incomeid=entityid)).proof.path)
				if(creditentry.objects.filter(creditaccount=credit.objects.get(incomeid = income.objects.get(incomeid=entityid))).exists()):
					os.remove(creditentry.objects.get(creditaccount=credit.objects.get(incomeid = income.objects.get(incomeid=entityid))).proof.path)
		except:
			pass
		usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] - income.objects.get(incomeid=entityid).amount)
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Deleted Income entry and other entries related to it of Rs. " + str(income.objects.get(incomeid=entityid).amount),logtime=datetime.now())
		logobj.save()
		income.objects.filter(incomeid=entityid).delete()
		CalculateTax(request)
		return redirect('/showdetails')
	elif entity == 'expense':
		try:
			if(str(expense.objects.get(expenseid=entityid).proof.path).find('no-proof.png')==-1):
				os.remove(expense.objects.get(expenseid=entityid).proof.path)
			if(generalreserve.objects.filter(expenseid = expense.objects.get(expenseid=entityid)).exists()):
				os.remove(generalreserve.objects.get(expenseid = expense.objects.get(expenseid=entityid)).proof.path)
			if(savings.objects.filter(expenseid = expense.objects.get(expenseid=entityid)).exists()):
				os.remove(savings.objects.get(expenseid = expense.objects.get(expenseid=entityid)).proof.path)
			if(creditentry.objects.filter(expenseid = expense.objects.get(expenseid=entityid)).exists()):
				os.remove(creditentry.objects.get(expenseid = expense.objects.get(expenseid=entityid)).proof.path)
		except:
			pass
		usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + expense.objects.get(expenseid=entityid).amount)
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Deleted Expense entry and other entries related to it of Rs. " + str(expense.objects.get(expenseid=entityid).amount),logtime=datetime.now())
		logobj.save()
		expense.objects.filter(expenseid=entityid).delete()
		return redirect('/showdetails')
	elif entity == 'generalreserve':
		try:
			if(str(generalreserve.objects.get(GRid=entityid).proof.path).find('no-proof.png')==-1 and str(expense.objects.get(expenseid=generalreserve.objects.get(GRid=entityid).expenseid.expenseid).proof.path).find('no-proof.png')==-1):
				os.remove(generalreserve.objects.get(GRid=entityid).proof.path)
				os.remove(expense.objects.get(expenseid=generalreserve.objects.get(GRid=entityid).expenseid.expenseid).proof.path)
		except:
			pass
		usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + generalreserve.objects.get(GRid=entityid).reserveamt)
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Deleted General Reserve and other entries related to it of Rs. " + str(generalreserve.objects.get(GRid=entityid).reserveamt),logtime=datetime.now())
		logobj.save()
		expense.objects.filter(expenseid=generalreserve.objects.get(GRid = entityid).expenseid.expenseid).delete()
		return redirect('/showdetails')
	elif entity == 'savings':
		try:
			if(str(savings.objects.get(savingsid=entityid).proof.path).find('no-proof.png')==-1 and str(expense.objects.get(expenseid=savings.objects.get(savingsid=entityid).expenseid.expenseid).proof.path).find('no-proof.png')==-1):
				os.remove(savings.objects.get(savingsid=entityid).proof.path)
				os.remove(expense.objects.get(expenseid=savings.objects.get(savingsid=entityid).expenseid.expenseid).proof.path)
		except:
			pass
		usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + savings.objects.get(savingsid=entityid).amount)
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Deleted Savings entry and other entries related to it of Rs. " + str(savings.objects.get(savingsid=entityid).amount),logtime=datetime.now())
		logobj.save()
		expense.objects.filter(expenseid=savings.objects.get(savingsid = entityid).expenseid.expenseid).delete()
		return redirect('/showdetails')	
	elif entity == 'creditentry':
		try:
			if(str(creditentry.objects.get(creditentryid=entityid).proof.path).find('no-proof.png')==-1 and str(expense.objects.get(expenseid=creditentry.objects.get(creditentryid=entityid).expenseid.expenseid).proof.path).find('no-proof.png')==-1):
				os.remove(creditentry.objects.get(creditentryid=entityid).proof.path)
				os.remove(expense.objects.get(expenseid=creditentry.objects.get(creditentryid=entityid).expenseid.expenseid).proof.path)
		except:
			pass
		usertable.objects.filter(useremail=userdetails['useremail']).update(opbalance=userdetails['opbalance'] + creditentry.objects.get(creditentryid=entityid).amountpaid)
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Deleted Credit repayment entry and other entries related to it of Rs. " + str(creditentry.objects.get(creditentryid=entityid).amountpaid),logtime=datetime.now())
		logobj.save()
		expense.objects.filter(expenseid=creditentry.objects.get(creditentryid = entityid).expenseid.expenseid).delete()
		return redirect('/showdetails')
	else:
		pass

def edituser(request, useremail):
	userslist = usertable.objects.get(useremail=useremail)
	return render(request,'userdetailsupdate.html',{'userslist':userslist})

def update(request, useremail):  
    request.session['formsubmitted'] = "nil"
    userupdateobj = usertable.objects.get(useremail=useremail)
    emaildata = request.POST.get('useremail')
    creditform = credit.objects.filter(useremail=emaildata)
    #form = UserSignUpForm(request.POST, instance = userslist)
    #print(form.is_valid(),form.errors)
    #if form.is_valid():
    	#form.save()
    	#return redirect("/Dashboard")
    if request.method == "POST":
    	userupdateobj.username = request.POST.get('username')
    	userupdateobj.useremail = request.POST.get('useremail')
    	userupdateobj.profession = request.POST.get('profession')
    	userupdateobj.opbalance = request.POST.get('opbalance')
    	userupdateobj.password = request.POST.get('password')
    	userupdateobj.save()
    	userdetails = dict(usertable.objects.filter(useremail = useremail).values('username','useremail','opbalance','profession')[0])
    	logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="Updated user details",logtime=datetime.now())
    	logobj.save()
    	return redirect('/Dashboard')
    	#return render(request,'index1.html',{'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
    return render(request, 'userdetailsupdate.html', {'userslist': userslist})  

def SignUp(request):
	#global userdetails
	request.session['formsubmitted'] = "nil"
	if request.method == "POST":
		form = UserSignUpForm(request.POST)
		print(form.is_valid(),form.errors)
		if form.is_valid():
			try:
				form.save()
				emaildata = request.POST.get('useremail')
				creditform = credit.objects.filter(useremail=emaildata)
				request.session['useremail'] = emaildata
				userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
				#return redirect('/Dashboard')
				logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="First time Account Signed Up!!!",logtime=datetime.now())
				logobj.save()
				return render(request,'index1.html',{'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
			except:
				pass
		else:
			print("something went wrong")
			registered = "You Are already registered. Go Ahead To Login"
			return render(request,'test.html',{'form':form,'registered':registered})
	else:
		form = UserSignUpForm()
		#print(form)
	return render(request,'test.html',{'form':form})

def Login(request):
	#global userdetails
	request.session['formsubmitted'] = "nil"
	emaildata = request.POST.get('emailid')
	passworddata = request.POST.get('password')
	notfound = "Username or Password incorrect!!!"
	if(usertable.objects.filter(useremail = emaildata, password = passworddata).exists()):
		userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
		#userdetails['opbalance'] = '{:,.2f}'.format(userdetails['opbalance'])
		#return redirect('/Dashboard')
		request.session['useremail'] = emaildata
		logobj = logentry(useremail=usertable.objects.get(useremail=emaildata),action="You have logged in",logtime=datetime.now())
		logobj.save()
		CalculateTax(request)
		return redirect('/Dashboard')
		#return render(request,'index1.html',{'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
	else:
		form = UserSignUpForm()
		return render(request,'test.html',{'notfound':notfound,'form':form})

def logout(request):
	logobj = logentry(useremail=usertable.objects.get(useremail=request.session['useremail']),action="you have logged out",logtime=datetime.now())
	logobj.save()
	return redirect('/SignUp')

import locale

def liquidcash(amt):
	locale.setlocale(locale.LC_MONETARY, 'en_IN')
	amount = locale.currency(amt,grouping=True).lstrip('?')
	if amt >= 0:
		liquid = "Liquid Cash Available:"
		return dict(amt=amount,liquid=liquid)
	else:
		liquid = "You are bankrupt/ Owe:"
		return dict(amt=amount,liquid=liquid)

def SubmitIncome(request):
	#global userdetails
	emaildata = request.session['useremail']
	userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	creditform = CreditEntryForm()
	if request.method == "POST":
		desc = request.POST.get('incomedesc')
		amt = request.POST.get('incomeamt')
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/income')
				filename = fs.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		try:
			inc_obj = income(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']),proof='images/' + userdetails['username'] + '/income/' + filename)
		except:
			inc_obj = income(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		try:
			inc_obj.save()
			logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Income of Rs. " + str(income.objects.latest('incomeid').amount) + " was recieved on the name of " + income.objects.latest('incomeid').description, logtime = income.objects.latest('incomeid').date)
			logobj.save()
			incdetails = {'description':income.objects.latest('incomeid').description,'amount':income.objects.latest('incomeid').amount}
			#incdetails = income.objects.filter(useremail=userdetails['useremail']).values('description','amount')
			try:
				usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] + incdetails['amount'])
				userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
				#print(income.objects.filter(useremail= userdetails['useremail']).values_list())
			except:
				print("Was not able to update")
			request.session['formsubmitted'] = "incomedetails"
			CalculateTax(request)
			return redirect('/Dashboard')
			#return render(request,'index1.html',{'incdetails':incdetails,'creditform':creditform,'added':"it was added",'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})
		except:
			pass
	else:
		form = IncomeForm()
	return redirect('/Dashboard')

def SubmitExpense(request):
	#global userdetails
	emaildata = request.session['useremail']
	userdetails = userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	creditform = CreditEntryForm()
	if request.method == "POST":
		desc = request.POST.get('expensedesc')
		amt = request.POST.get('expenseamt')
		#print(usertable.objects.get(useremail = userdetails['useremail']))
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/expense')
				filename = fs.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		try:
			exp_obj = expense(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']),proof='images/' + userdetails['username'] + '/expense/' + filename)
		except:
			exp_obj = expense(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		try:
			exp_obj.save()
			logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Expense of Rs. " + str(expense.objects.latest('expenseid').amount) + " was incurred on the name of " + expense.objects.latest('expenseid').description, logtime = expense.objects.latest('expenseid').date)
			logobj.save()
			#print(expense.objects.latest('expenseid').description,expense.objects.latest('expenseid').amount)
			expdetails = dict(description=expense.objects.latest('expenseid').description,amount=expense.objects.latest('expenseid').amount)
			#print(expense.objects.latest('expenseid'))
			#incdetails = income.objects.filter(useremail=userdetails['useremail']).values('description','amount')
			try:
				usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] - expdetails['amount'])
				userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
				#print(expense.objects.filter(useremail = userdetails['useremail']).values_list())
			except:
				print("Was not able to update")
			request.session['formsubmitted'] = "expensedetails"
			return redirect('/Dashboard')
			#return render(request,'index1.html',{'expdetails':expdetails,'creditform':creditform,'added':"it was added",'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})
		except:
			pass
	else:
		form = ExpenseForm()
	return redirect('/Dashboard')

def SubmitGeneralReserve(request):
	#global userdetails
	emaildata = request.session['useremail']
	userdetails = userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	creditform = CreditEntryForm()
	if request.method == "POST":
		assetname = request.POST.get('assetname')
		assetvalue = request.POST.get('assetvalue')
		reserveamt = request.POST.get('reserveamt')
		desc = "General Reserve for " + assetname 
		amt = reserveamt
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/generalreserve')
				fs1 = FileSystemStorage(location='media/images/' + userdetails['username'] + '/expense')
				filename = fs.save(myfile.name, myfile)
				filename1 = fs1.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		try:
			exp_obj = expense(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']),proof='images/' + userdetails['username'] + '/expense/' + filename1)
		except:
			exp_obj = expense(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		#print(expense.objects.latest('expenseid'))
		try:
			exp_obj.save()
			logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Expense of Rs. " + str(expense.objects.latest('expenseid').amount) + " was incurred on the name of " + expense.objects.latest('expenseid').description, logtime = expense.objects.latest('expenseid').date)
			logobj.save()
			expdetails = dict(description=expense.objects.latest('expenseid').description,amount=expense.objects.latest('expenseid').amount)
			try:
				usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] - expdetails['amount'])
				userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
				#print(expense.objects.filter(useremail = userdetails['useremail']).values_list())
			except:
				print("Was not able to update")
			try:
				GR_obj = generalreserve(assetname = assetname, assetvalue = assetvalue, reserveamt = reserveamt, useremail = usertable.objects.get(useremail = userdetails['useremail']), expenseid = expense.objects.latest('expenseid'),proof = 'images/' + userdetails['username'] + '/generalreserve/' + filename)
			except:
				GR_obj = generalreserve(assetname = assetname, assetvalue = assetvalue, reserveamt = reserveamt, useremail = usertable.objects.get(useremail = userdetails['useremail']), expenseid = expense.objects.latest('expenseid'))
			try:
				GR_obj.save()
				logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "A General Reserve of Rs. " + str(generalreserve.objects.latest('GRid').reserveamt) + " was recieved for the asset " + generalreserve.objects.latest('GRid').assetname + " valued at Rs. " + str(generalreserve.objects.latest('GRid').assetvalue), logtime = generalreserve.objects.latest('GRid').date)
				logobj.save()
				GRdetails = dict(assetname=generalreserve.objects.latest('GRid').assetname,assetvalue=generalreserve.objects.latest('GRid').assetvalue, reserveamt = generalreserve.objects.latest('GRid').reserveamt)
			except:
				print("Was not able to send the GR_obj details")
			request.session['formsubmitted'] = "generalreservedetails"
			return redirect('/Dashboard')
			#return render(request,'index1.html',{'GRdetails':GRdetails,'creditform':creditform,'added':"it was added",'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})
		except:
			print("not able to add expense nor render GR_obj")
			pass
	else:
		form = GeneralReserveForm()
	return redirect('/Dashboard')

def SubmitSavings(request):
	#global userdetails
	emaildata = request.session['useremail']
	userdetails = userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	creditform = CreditEntryForm()
	if request.method == "POST":
		savingsaccount = request.POST.get('savingsac')
		amount = request.POST.get('savingsamt')
		desc = "Savings Made for " + savingsaccount 
		amt = amount
		#print(expense.objects.latest('expenseid'))
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/savings')
				fs1 = FileSystemStorage(location='media/images/' + userdetails['username'] + '/expense')
				filename = fs.save(myfile.name, myfile)
				filename1 = fs1.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		try:
			exp_obj = expense(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']),proof= 'images/' + userdetails['username'] + '/expense/' + filename1)
		except:
			exp_obj = expense(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		try:
			exp_obj.save()
			logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Expense of Rs. " + str(expense.objects.latest('expenseid').amount) + " was incurred on the name of " + expense.objects.latest('expenseid').description, logtime = expense.objects.latest('expenseid').date)
			logobj.save()
			expdetails = dict(description=expense.objects.latest('expenseid').description,amount=expense.objects.latest('expenseid').amount)
			try:
				usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] - expdetails['amount'])
				userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
				#print(expense.objects.filter(useremail = userdetails['useremail']).values_list())
			except:
				print("Was not able to update")
			try:
				savings_obj = savings(savingsaccount = savingsaccount, amount = amount, useremail = usertable.objects.get(useremail = userdetails['useremail']), expenseid = expense.objects.latest('expenseid'), proof = 'images/' + userdetails['username'] + '/savings/' + filename)
			except:
				savings_obj = savings(savingsaccount = savingsaccount, amount = amount, useremail = usertable.objects.get(useremail = userdetails['useremail']), expenseid = expense.objects.latest('expenseid'))
			try:
				savings_obj.save()
				logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "A Savings of Rs. " + str(savings.objects.latest('savingsid').amount) + " on the name of " + savings.objects.latest('savingsid').savingsaccount, logtime = savings.objects.latest('savingsid').date)
				logobj.save()
				savingsdetails = dict(savingsaccount=savings.objects.latest('savingsid').savingsaccount,amount=savings.objects.latest('savingsid').amount)
			except:
				print("Was not able to send the Savings_obj details")
			request.session['formsubmitted'] = "savingsdetails"
			return redirect('/Dashboard')
			#return render(request,'index1.html',{'savingsdetails':savingsdetails,'creditform':creditform,'added':"it was added",'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})
		except:
			print("not able to add expense nor render savings_obj")
			pass
	else:
		form = SavingsForm()
	return redirect('/Dashboard')

def SubmitCredit(request):
	#global userdetails
	emaildata = request.session['useremail']
	userdetails = userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	creditform = credit.objects.filter(useremail=emaildata).values('creditaccount','creditbalance')
	if request.method == "POST":
		creditaccount = request.POST.get('creditac')
		creditbalance = request.POST.get('creditbalance')
		desc = "Credit Borrowed From " + creditaccount 
		amt = creditbalance
		#print(expense.objects.latest('expenseid'))
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/credit')
				fs1 = FileSystemStorage(location='media/images/' + userdetails['username'] + '/income')
				filename1 = fs1.save(myfile.name, myfile)
				filename = fs.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		try:
			inc_obj = income(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']),proof = 'images/' + userdetails['username'] + '/income/' + filename1)
		except:
			inc_obj = income(description = desc, amount = amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		try:
			inc_obj.save()
			logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Income of Rs. " + str(income.objects.latest('incomeid').amount) + " was recieved on the name of " + income.objects.latest('incomeid').description, logtime = income.objects.latest('incomeid').date)
			logobj.save()
			incdetails = dict(description=income.objects.latest('incomeid').description,amount=income.objects.latest('incomeid').amount)
			try:
				usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] + incdetails['amount'])
				userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
				#print(expense.objects.filter(useremail = userdetails['useremail']).values_list())
			except:
				print("Was not able to update")
			try:
				credit_obj = credit(creditaccount = creditaccount, creditbalance = creditbalance, useremail = usertable.objects.get(useremail = userdetails['useremail']), incomeid = income.objects.latest('incomeid'), proof = 'images/' + userdetails['username'] + '/credit/' + filename)
			except:
				credit_obj = credit(creditaccount = creditaccount, creditbalance = creditbalance, useremail = usertable.objects.get(useremail = userdetails['useremail']), incomeid = income.objects.latest('incomeid'))
			try:
				credit_obj.save()
				logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "A Credit of Rs. " + str(creditbalance) + " was Borrowed on the name of " + creditaccount, logtime = credit.objects.get(creditaccount=creditaccount).date)
				logobj.save()
				creditdetails = dict(creditaccount=creditaccount,creditbalance=creditbalance)
			except:
				print("Was not able to send the Savings_obj details")
			request.session['formsubmitted'] = "creditdetails"
			#return redirect('/Dashboard')
			return render(request,'index1.html',{'creditdetails':creditdetails,'creditform':creditform,'added':"it was added",'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})
		except:
			print("not able to add expense nor render savings_obj")
			pass
	else:
		creditform = credit.objects.filter(useremail=emaildata)
	return render(request,'index1.html',{'creditform':creditform,'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})

def SubmitCreditEntry(request):
	#global userdetails
	emaildata = request.session['useremail']
	userdetails = userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	if request.method == "POST":
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/creditentry')
				fs1 = FileSystemStorage(location='media/images/' + userdetails['username'] + '/expense')
				filename = fs.save(myfile.name, myfile)
				filename1 = fs1.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		desc = "Paid back credit Borrowed from " + request.POST.get('creditaccount')
		amt = request.POST.get('amountpaid')
		try:
			exp_obj = expense(description=desc,amount=amt, useremail = usertable.objects.get(useremail = userdetails['useremail']), proof = 'images/' + userdetails['username'] + '/expense/' + filename1)
		except:
			exp_obj = expense(description=desc,amount=amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		exp_obj.save()
		logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Expense of Rs. " + str(expense.objects.latest('expenseid').amount) + " was incurred on the name of " + expense.objects.latest('expenseid').description, logtime = expense.objects.latest('expenseid').date)
		logobj.save()
		#print(request.POST.get('creditaccount'),request.POST.get('amountpaid'))
		expdetails = dict(description=expense.objects.latest('expenseid').description,amount=expense.objects.latest('expenseid').amount)
		try:
			creditentryobj = creditentry(creditaccount=credit.objects.get(creditaccount=request.POST.get('creditaccount')),useremail = usertable.objects.get(useremail = userdetails['useremail']),expenseid = expense.objects.latest('expenseid'),amountpaid = request.POST.get('amountpaid'),proof = 'images/' + userdetails['username'] + '/creditentry/' + filename)
		except:
			creditentryobj = creditentry(creditaccount=credit.objects.get(creditaccount=request.POST.get('creditaccount')),useremail = usertable.objects.get(useremail = userdetails['useremail']),expenseid = expense.objects.latest('expenseid'),amountpaid = request.POST.get('amountpaid'))
		creditentryobj.save()
		logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "A Credit amount of Rs. " + str(creditentry.objects.latest('creditentryid').amountpaid) + " was returned to " + creditentry.objects.latest('creditentryid').creditaccount.creditaccount, logtime = creditentry.objects.latest('creditentryid').date)
		logobj.save()
		credit.objects.filter(creditaccount=request.POST.get('creditaccount')).update(creditbalance = credit.objects.get(creditaccount=request.POST.get('creditaccount')).creditbalance - creditentry.objects.latest('creditentryid').amountpaid)
		if(credit.objects.get(creditaccount=request.POST.get('creditaccount')).creditbalance <= 0):
			creditentrydetails = dict(creditaccount=request.POST.get('creditaccount'),amountpaid=creditentry.objects.latest('creditentryid').amountpaid)
			credit.objects.filter(creditaccount=request.POST.get('creditaccount')).delete()
		else:
			creditentrydetails = dict(creditaccount=request.POST.get('creditaccount'),amountpaid=creditentry.objects.latest('creditentryid').amountpaid,creditbalance=credit.objects.get(creditaccount=request.POST.get('creditaccount')).creditbalance,balancecleared="notclear")
		usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] - expdetails['amount'])
		userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
		creditform = credit.objects.filter(useremail=emaildata)
		return render(request,'index1.html',{'creditentrydetails':creditentrydetails,'creditform':creditform,'added':"it was added",'userdetails':userdetails,'liquid':liquidcash(userdetails['opbalance'])})
		#except:
			#print("error")
	#else:
		#creditform = CreditEntryForm()
	#return redirect('/Dashboard')

def taxationpage(request):
	CalculateTax(request)
	taxobjects = taxation.objects.filter(useremail=request.session['useremail'])
	totalincome = income.objects.filter(useremail=request.session['useremail']).aggregate(Sum('amount'))['amount__sum']
	totalexpense = expense.objects.filter(useremail=request.session['useremail']).aggregate(Sum('amount'))['amount__sum']
	totalsavings = savings.objects.filter(useremail=request.session['useremail']).aggregate(Sum('amount'))['amount__sum']
	totalgeneralreserves = generalreserve.objects.filter(useremail=request.session['useremail']).aggregate(Sum('reserveamt'))['reserveamt__sum']
	totalcredits = credit.objects.filter(useremail=request.session['useremail']).aggregate(Sum('creditbalance'))['creditbalance__sum']
	totalcreditentrys = creditentry.objects.filter(useremail=request.session['useremail']).aggregate(Sum('amountpaid'))['amountpaid__sum']
	current_fiscal_month = int(datetime.now().strftime('%m'))
	current_fiscal_year = int(datetime.now().strftime('%Y'))
	if current_fiscal_month < 4:
		current_fiscal_period = str(current_fiscal_year - 1) + '-' + str(current_fiscal_year)
	else:
		current_fiscal_period = str(current_fiscal_year) + '-' + str(current_fiscal_year + 1)
	return render(request,'taxation.html',{'taxobjects':taxobjects,'totalincome':totalincome,'totalexpense':totalexpense,'totalsavings':totalsavings,'totalgeneralreserves':totalgeneralreserves,'totalcredits':totalcredits,'totalcreditentrys':totalcreditentrys,'current_fiscal_period':current_fiscal_period});

def showdashboard(request):
    #global userdetails
    emaildata = request.session['useremail']
    request.session['updordel'] = "nothing"
    userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
    #creditform = CreditEntryForm()
    creditform = credit.objects.filter(useremail=emaildata)
    #print(creditform)
    #print(credit.objects.filter(useremail=emaildata).values('creditaccount','creditbalance'))
    userdetails = dict(usertable.objects.filter(useremail = userdetails['useremail']).values('username','useremail','opbalance','profession')[0])
    if request.session['formsubmitted'] == "incomedetails":
    	incdetails = {'description':income.objects.latest('incomeid').description,'amount':income.objects.latest('incomeid').amount}
    	return render(request,'index1.html',{'incdetails':incdetails,'added':"it was added",'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
    elif request.session['formsubmitted'] == "expensedetails":
    	expdetails = dict(description=expense.objects.latest('expenseid').description,amount=expense.objects.latest('expenseid').amount)
    	return render(request,'index1.html',{'expdetails':expdetails,'added':"it was added",'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
    elif request.session['formsubmitted'] == "generalreservedetails":
    	GRdetails = dict(assetname=generalreserve.objects.latest('GRid').assetname,assetvalue=generalreserve.objects.latest('GRid').assetvalue, reserveamt = generalreserve.objects.latest('GRid').reserveamt)
    	return render(request,'index1.html',{'GRdetails':GRdetails,'added':"it was added",'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
    elif request.session['formsubmitted'] == "savingsdetails":
    	savingsdetails = dict(savingsaccount=savings.objects.latest('savingsid').savingsaccount,amount=savings.objects.latest('savingsid').amount)
    	return render(request,'index1.html',{'savingsdetails':savingsdetails,'added':"it was added",'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
    else:
    	return render(request,'index1.html',{'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})
    #return render(request,'index1.html',{'userdetails':userdetails,'creditform':creditform,'liquid':liquidcash(userdetails['opbalance'])})  
#def edit(request, id):  
    #employee = Employee.objects.get(id=id)  
    #return render(request,'edit.html', {'employee':employee})  
#def update(request, id):  
    #employee = Employee.objects.get(id=id)  
    #form = EmployeeForm(request.POST, instance = employee)  
    #if form.is_valid():  
        #form.save()  
        #return redirect("/show")  
    #return render(request, 'edit.html', {'employee': employee})  
#def destroy(request, id):  
    #employee = Employee.objects.get(id=id)  
    #employee.delete()  
    #return redirect("/show")

def CalculateTax(request):
	try:
		import pandas as pd
		year = []
		totalincome = []
		for a in income.objects.filter(useremail = request.session['useremail']).values_list():
			if a[4].month < 4:
				fiscal_start_year = a[4].year - 1
				fiscal_end_year = a[4].year 
			else:
				fiscal_start_year = a[4].year 
				fiscal_end_year = a[4].year + 1
			year.append(str(fiscal_start_year) + '-' + str(fiscal_end_year))
			totalincome.append(float(a[3]))
			df = pd.DataFrame({'Year':pd.Series(year),'TotalIncome':pd.Series(totalincome)})
		#print(df)
		result = df.groupby('Year')['TotalIncome'].sum()
		dictresult = dict(result)
		fiscal_period = list(dictresult.keys())
		for i in range(0,len(fiscal_period)):
			#print("Fiscal Period: "+fiscal_period[i]+", Total Income: "+str(dictresult[fiscal_period[i]]))
			grosstotalincome = dictresult[fiscal_period[i]]
			age = usertable.objects.get(useremail = request.session['useremail']).age
			#age constraint
			taxpayable = 0
			if age < 60:
				#male or female
				if grosstotalincome <= 250000:
					taxpayable = 0
				elif grosstotalincome > 250000 and grosstotalincome <= 500000:
					taxpayable = 0.05 * grosstotalincome
				elif grosstotalincome > 500000 and grosstotalincome <= 1000000:
					taxpayable = 12500 + 0.2 * grosstotalincome
				else:
					taxpayable = 112500 + 0.3 * grosstotalincome
			elif age >= 60 and age < 80:
				#senior citizen
				if grosstotalincome <= 300000:
					taxpayable = 0
				elif grosstotalincome > 300000 and grosstotalincome <= 500000:
					taxpayable = 0.05 * grosstotalincome
				elif grosstotalincome > 500000 and grosstotalincome <= 1000000:
					taxpayable = 10000 + 0.2 * grosstotalincome
				else:
					taxpayable = 110000 + 0.3 * grosstotalincome
			else:
				#very senior citizen
				if grosstotalincome <= 500000:
					taxpayable = 0
				elif grosstotalincome > 500000 and grosstotalincome <= 1000000:
					taxpayable = 0.2 * grosstotalincome
				else:
					taxpayable = 100000 + 0.3 * grosstotalincome
			#We have update only the current fiscal year dynamically, so 
			current_fiscal_month = int(datetime.now().strftime('%m'))
			current_fiscal_year = int(datetime.now().strftime('%Y'))
			if current_fiscal_month < 4:
				current_fiscal_period = str(current_fiscal_year - 1) + '-' + str(current_fiscal_year)
			else:
				current_fiscal_period = str(current_fiscal_year) + '-' + str(current_fiscal_year + 1)
			if taxation.objects.filter(useremail=usertable.objects.get(useremail = request.session['useremail']),duration=fiscal_period[i]).exists():
				if fiscal_period[i] == current_fiscal_period:
					taxation.objects.filter(useremail=usertable.objects.get(useremail = request.session['useremail']),duration=fiscal_period[i]).update(payableamt=taxpayable,date = datetime.now())
					logobj = logentry(useremail = usertable.objects.get(useremail = request.session['useremail']), action = 'Tax for current Fiscal period was updated', logtime = datetime.now())
					logobj.save()
			else:
				taxobj = taxation(useremail=usertable.objects.get(useremail = request.session['useremail']),duration=fiscal_period[i],payableamt=taxpayable,status=False)
				taxobj.save()
	except:
		pass

def taxsubmit(request, duration):
	emaildata = request.session['useremail']
	userdetails = userdetails = dict(usertable.objects.filter(useremail = emaildata).values('username','useremail','opbalance','profession')[0])
	if request.method == "POST":
		try:
			if request.FILES['proof']:
				myfile = request.FILES['proof']
				fs = FileSystemStorage(location='media/images/' + userdetails['username'] + '/TaxInvoice')
				fs1 = FileSystemStorage(location='media/images/' + userdetails['username'] + '/expense')
				filename = fs.save(myfile.name, myfile)
				filename1 = fs1.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(filename,uploaded_file_url)
		except:
			pass
		desc = "TAX paid for the Fiscal Year " + duration
		amt = taxation.objects.get(useremail= userdetails['useremail'],duration=duration).payableamt
		try:
			exp_obj = expense(description=desc,amount=amt, useremail = usertable.objects.get(useremail = userdetails['useremail']), proof = 'images/' + userdetails['username'] + '/expense/' + filename1)
		except:
			exp_obj = expense(description=desc,amount=amt, useremail = usertable.objects.get(useremail = userdetails['useremail']))
		exp_obj.save()
		logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "An Expense of Rs. " + str(expense.objects.latest('expenseid').amount) + " was incurred on the name of " + expense.objects.latest('expenseid').description, logtime = expense.objects.latest('expenseid').date)
		logobj.save()
		#print(request.POST.get('creditaccount'),request.POST.get('amountpaid'))
		expdetails = dict(description=expense.objects.latest('expenseid').description,amount=expense.objects.latest('expenseid').amount)
		usertable.objects.filter(useremail = userdetails['useremail']).update(opbalance = userdetails['opbalance'] - expdetails['amount'])
		taxation.objects.filter(useremail= userdetails['useremail'],duration=duration).update(status=True)
		logobj = logentry(useremail = usertable.objects.get(useremail = userdetails['useremail']), action = "Tax was cleared for the duration paid as of" + duration, logtime = expense.objects.latest('expenseid').date)
		logobj.save()
		return redirect('/taxation')