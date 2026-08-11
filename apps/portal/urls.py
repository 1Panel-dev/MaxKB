from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("portal", views.PortalView.as_view()),
    path("portal/info", views.PortalInfoView.as_view()),
    path("portal/login", views.PortalLoginView.as_view()),
    path("portal/logout", views.PortalLogoutView.as_view()),
    path("portal/application/<int:current_page>/<int:page_size>", views.PortalApplicationView.as_view()),
    path(
        "portal/historical_conversation/<int:current_page>/<int:page_size>",
        views.PortalHistoricalConversationView.as_view(),
    ),
]
