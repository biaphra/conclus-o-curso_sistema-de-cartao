from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic.base import TemplateView
from cards import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("cadastro/", views.signup, name="signup"),
    path("recuperar-senha/", auth_views.PasswordResetView.as_view(success_url="/recuperar-senha/enviado/"), name="password_reset"),
    path("recuperar-senha/enviado/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("redefinir-senha/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(success_url="/redefinir-senha/concluido/"), name="password_reset_confirm"),
    path("redefinir-senha/concluido/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("api/schema/", views.api_schema, name="api_schema"),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("cards/", include("cards.urls", namespace="cards")),
]
