from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("poke/<int:id>/", views.detail_view, name="detail"),
    path("api/poke/<int:id>/add_watchlist/", views.add_watchlist, name="add_watchlist"),
    path("api/poke/watchlist", views.get_watchlist, name="view_watchlist"),
]
