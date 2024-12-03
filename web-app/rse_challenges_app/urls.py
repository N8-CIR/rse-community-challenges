from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("challenges", views.index, name="index"),
    path("challenge/<int:challenge_id>/", views.challenge_view, name="challenge"),
    path("challenge/<int:challenge_id>/<str:component_key>", views.challenge_component_view, name="challenge_component"),
]