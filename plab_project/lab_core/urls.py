from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    PatientLoginView,
    DashboardView,
    SignUpView,
    HomeView,
    AboutView,
    ForgotPasswordView,
    RobotsTxtView,
    SitemapXmlView,
    BlogPostDetailView,
    # ToggleHeartView,
    ProfileView,
    ChangePasswordView,
    like_post_ajax
)

app_name = "lab_core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("posts/<str:slug>/", BlogPostDetailView.as_view(), name="post_detail"),
    # path("posts/<int:pk>/heart/", ToggleHeartView.as_view(), name="toggle_heart"),
    path("posts/<int:pk>/like/", like_post_ajax, name="like_post_ajax"),
    path("login/", PatientLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("robots.txt", RobotsTxtView.as_view(), name="robots_txt"),
    path("sitemap.xml", SitemapXmlView.as_view(), name="sitemap_xml"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("logout/", LogoutView.as_view(next_page="lab_core:login"), name="logout"),
]
