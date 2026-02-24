from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("transactions/", views.transactions_list, name="transactions_list"),
]
