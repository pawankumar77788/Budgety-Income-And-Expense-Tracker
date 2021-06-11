from django.contrib import admin

# Register your models here.

from .models import usertable, income, expense, generalreserve, savings, credit, creditentry, logentry, taxation
admin.site.register(usertable)
admin.site.register(income)
admin.site.register(expense)
admin.site.register(generalreserve)
admin.site.register(savings)
admin.site.register(credit)
admin.site.register(creditentry)
admin.site.register(logentry)
admin.site.register(taxation)
#admin.site.register(empsalary)
