from django.urls import path

from . import views

app_name = "team"
urlpatterns = [
    path('team/member', views.TeamMember.as_view(), name="team"),
    path('team/member/<str:member_id>', views.TeamMember.Operate.as_view(), name='member')
]
