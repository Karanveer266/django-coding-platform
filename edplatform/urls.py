"""
URL configuration for the *edplatform* project.

—  "Site" pages (HTML templates) are declared FIRST so they win the
   URL-resolver race against similarly-named API routes.
—  API endpoints live under /api/auth/ and come afterwards.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from users.views import login_view, signup_view, logout_view, dashboard_view

urlpatterns = [
    # ──────────────────────────────────────────
    # 1)  Public / session-based HTML pages
    # ──────────────────────────────────────────
    path("login/", login_view, name="login"),
    path("login-fixed/", login_view, name="login_fixed"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("", login_view, name="root"),

    # ──────────────────────────────────────────
    # 2)  Feature-app URLConfs
    # ──────────────────────────────────────────
    path("problems/", include("problems.urls")),
    path("blogs/", include("blogs.urls")),
    path("users/", include("users.urls")),
    path("submit/", include("submit.urls")),
    path("learning-sessions/", include("learning_sessions.urls")),
    path("ai-code-review/", include("ai_code_review.urls")),

    # ──────────────────────────────────────────
    # 3)  API  (dj-rest-auth / DRF) - Commented out for now
    #     Kept AFTER site pages so names don't clash
    # ──────────────────────────────────────────
    # path("api/auth/", include("dj_rest_auth.urls")),
    # path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    # path("api/problems/", include("problems.api_urls")),
    # path("api/learning-sessions/", include("learning_sessions.api_urls")),

    # ──────────────────────────────────────────
    # 4)  Django Admin
    # ──────────────────────────────────────────
    path("admin/", admin.site.urls),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)