"""learndjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    #path('', views.loadfirst),
    #path('linktonext',views.loadsecond),
    #path('nextpage',views.loadsecond),
    path('admin/', admin.site.urls),  
    path('SignUp', views.SignUp),  
    path('Dashboard',views.showdashboard),
    path('Login',views.Login),
    path('SubmitIncome',views.SubmitIncome),
    path('SubmitExpense',views.SubmitExpense),
    path('SubmitGeneralReserve',views.SubmitGeneralReserve),
    path('SubmitSavings',views.SubmitSavings),
    path('SubmitCredit',views.SubmitCredit),
    path('SubmitCreditEntry',views.SubmitCreditEntry),
    path('edit/<str:useremail>',views.edituser),
    path('update/<str:useremail>',views.update),
    path('logout',views.logout),
    path('showdetails',views.showdetails),
    path('edit/<str:entity>/<int:entityid>',views.editobject),
    path('editcredit/<str:entity>/<str:entityid>',views.editcredit),
    path('updateobj/<str:entity>/<int:entityid>',views.updateobject),
    path('updateobjcredit/<str:entity>/<str:entityid>',views.updatecredit),
    path('deletecredit/<str:entity>/<str:entityid>',views.deletecredit),
    path('backtodashboard',views.showdashboard),
    path('delete/<str:entity>/<int:entityid>',views.deleteobject),
    path('showloghistory',views.showloghistory),
    path('taxation',views.taxationpage),
    path('SubmitTaxAsPaid/<str:duration>',views.taxsubmit),
    #path('edit/<int:id>', views.edit),  
    #path('update/<int:id>', views.update),  
    #path('delete/<int:id>', views.destroy),   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)