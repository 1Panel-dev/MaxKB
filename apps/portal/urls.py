from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("portal", views.PortalView.as_view()),
    path("portal/info", views.PortalInfoView.as_view()),
    path("portal/login", views.PortalLoginView.as_view()),
    path("portal/logout", views.PortalLogoutView.as_view()),
]
