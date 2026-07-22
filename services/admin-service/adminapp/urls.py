from django.urls import path

from . import settings_views, tickets_views, views

urlpatterns = [
    path("internal/organizations", views.InternalCreateOrganizationView.as_view()),
    path("internal/organizations/resolve-invite/<str:code>", views.InternalResolveInviteView.as_view()),
    path("internal/organizations/<str:pk>", views.InternalOrganizationDetailView.as_view()),
    path("organizations/me", views.MyOrganizationView.as_view()),
    path("organizations", views.OrganizationListView.as_view()),
    path("organizations/<str:pk>/status", views.OrganizationStatusView.as_view()),
    path("organizations/<str:pk>/plan", views.OrganizationPlanView.as_view()),
    path("support-tickets", tickets_views.SupportTicketListCreateView.as_view()),
    path("support-tickets/<str:pk>", tickets_views.SupportTicketDetailView.as_view()),
    path("internal/audit-logs", settings_views.InternalAuditLogCreateView.as_view()),
    path("audit-logs", settings_views.AuditLogListView.as_view()),
    path("settings", settings_views.PlatformSettingsView.as_view()),
    path("settings/<str:key>", settings_views.PlatformSettingDetailView.as_view()),
]
