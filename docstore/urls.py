from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import RedirectView

from .accounts import views as accounts
from .documents import views as documents

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/$', accounts.AccountList, name='accounts'),
    url(r'^documents/$', documents.DocumentList, name='documents'),
    url(r'^documents/(?P<code>d-\w+)/$', documents.DocumentView, name='document'),
    url(r'^favicon.*$', RedirectView.as_view(url='/static/logo.png', permanent=True), name='favicon'),
    url(r'^$', RedirectView.as_view(url='https://github.com/eswald/docfiles/', permanent=True), name='main'),
]
