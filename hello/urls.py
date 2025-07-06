from django.urls import path
from django.contrib.auth.views import LogoutView
from hello import views
from hello.models import LogMessage
from django.conf import settings
from django.conf.urls.static import static

home_list_view = views.HomeListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],  # :5 limits the results to the five most recent
    context_object_name="message_list",
    template_name="hello/home.html",
)

class LogoutViewAllowPost(LogoutView):
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

urlpatterns = [
    path('', views.home, name='home'),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('approvals/', views.approval_list, name='approval_list'),
    path('approvals/<int:pk>/', views.approval_detail, name='approval_detail'),
    path('report/', views.report, name='report'),
    # path('profile/<int:id>/', views.profile_detail, name='profile_detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('expense/add/', views.expense_create, name='expense_add'),
    path('expense/<int:pk>/edit/', views.expense_update, name='expense_edit'),
    path('expense/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('expense-permissions/', views.expense_permission_list, name='expense_permission_list'),
    path('toggle-edit-permission/<int:user_id>/', views.toggle_edit_permission, name='toggle_edit_permission'),
    path('expense/<int:pk>/detail/', views.expense_detail, name='expense_detail'),
    path('permission/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

