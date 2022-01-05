from django.urls import path, re_path, include

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('test/', views.test, name='test'),
    path('tickets/<int:ticket_id>/', views.show_ticket, name='show_ticket'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('accounts/login/', views.HelpDeskLoginView.as_view(), name='login_page'),
    path('accounts/logout/', views.HelpDeskLogoutView.as_view(), name='logout_page'),
    path('account/signup/', views.signup_page, name='signup_page'),
    path('accounts/useraccount/<int:pk>/',  views.UserAccountView.as_view(), name='user_account'),
    re_path(r'^media/.+', views.check_file_permissions, name='check_file_permissions'),
    path('500/', views.http_response_server_error, name='http_500')
]
