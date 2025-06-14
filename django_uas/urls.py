"""
URL configuration for django_uas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# django_uas/urls.py

from django.contrib import admin
from django.urls import path, include
from buin import views as buin_views # <-- 1. Import views dari aplikasi buin

urlpatterns = [
    path('', buin_views.index, name='index'), # <-- 2. Tambahkan baris ini untuk halaman utama
    path('admin/', admin.site.urls),
    path('buin/', include('buin.urls')),
]
