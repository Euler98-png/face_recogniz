from django import views
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import dashboard, add_user, edit_user, delete_user, view_user, recognition_interface, recognize_face, custom_login
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login/', custom_login, name='login'),
    path('', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add-user/', add_user, name='add_user'), # Ajoutez cette ligne
    path('edit_user/<int:user_id>/', edit_user, name='edit_user'), # <-- nouveau
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'), # <-- nouveau
    path('view_user/<int:user_id>/', view_user, name='view_user'), # <-- nouveau
    path('recognize-face/', recognize_face, name='recognize_face'),
    path('interface/', recognition_interface, name='recognition_interface'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)