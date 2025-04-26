from django.urls import path
from django.contrib.auth import views as auth_views
from .views import dashboard, add_user, edit_user, delete_user, view_user
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add-user/', add_user, name='add_user'), # Ajoutez cette ligne
    path('edit_user/<int:profile_id>/', edit_user, name='edit_user'), # <-- nouveau
    path('delete_user/<int:profile_id>/', delete_user, name='delete_user'), # <-- nouveau
    path('view_user/<int:profile_id>/', view_user, name='view_user'), # <-- nouveau
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
