from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView

from .accounts import views as accounts
from .documents import views as documents

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', accounts.AccountList, name='accounts'),
    url(r'^favicon.*$', RedirectView.as_view(url='/static/logo.png', permanent=True), name='favicon'),
    url(r'^$', RedirectView.as_view(url='https://github.com/eswald/docfiles/', permanent=True), name='main'),
]
