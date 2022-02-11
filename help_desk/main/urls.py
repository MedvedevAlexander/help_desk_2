from django.urls import path, re_path, include

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('test/', views.test, name='test'),
    path('tickets/<int:ticket_id>/', views.ShowTicket.as_view(), name='show_ticket'),
    path('tickets/<int:ticket_id>/update_status', views.UpdateTicketStatus.as_view(), name='update_ticket_status'),
    path('tickets/create/', views.CreateTicket.as_view(), name='create_ticket'),
    path('accounts/login/', views.HelpDeskLoginView.as_view(), name='login_page'),
    path('accounts/logout/', views.HelpDeskLogoutView.as_view(), name='logout_page'),
    path('account/signup/', views.signup_page, name='signup_page'),
    path('accounts/useraccount/<int:pk>/',  views.UserAccountView.as_view(), name='user_account'),
    path('accounts/useraccount/<int:pk>/tickets_list/', views.UserAccountTicketsListView.as_view(), name='user_account_tickets_list'),
    path('accounts/useraccount/<int:pk>/profile_info', views.UserAccountProfileInfoEditView.as_view(), name='user_account_profile_info'),
    re_path(r'^media/.+', views.check_file_permissions, name='check_file_permissions'),
    path('500/', views.http_response_server_error, name='http_500'),
]
