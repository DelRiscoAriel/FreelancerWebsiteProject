"""
URL configuration for freelancer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tracker import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='registerTemp'),
    path('login/', views.login_view, name='loginTemp'),
    path('logout/', views.logout_view, name='logoutTemp'),
    path('account/', views.account_view, name='account'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('completed/', views.completed_view, name='completed'),
    path('clients/', views.client_list_view, name='client_list'),
    path('clients/<int:client_id>/edit/', views.edit_client_view, name='edit_client'),
    path('clients/<int:client_id>/projects/', views.client_projects_view, name='client_projects'),
    path('projects/create/', views.create_project_view, name='create_project'),
    path('projects/<int:project_id>/timer/start/', views.start_timer_view, name='start_timer'),
    path('projects/<int:project_id>/timer/stop/', views.stop_timer_view, name='stop_timer'),
    path('projects/<int:project_id>/set_inactive/', views.set_project_inactive_view, name='set_inactive_project'),
    path('projects/<int:project_id>/set_active/', views.set_project_active_view, name='set_active_project'),
    path('projects/<int:project_id>/track/', views.add_time_entry_for_project, name='track_time'),
    path('projects/<int:project_id>/entries/', views.project_time_entries_view, name='project_time_entries'),
    path('time-entry/<int:entry_id>/edit/', views.edit_time_entry_description, name='edit_time_entry'),
    path('time-entry/<int:entry_id>/delete/', views.delete_time_entry_view, name='delete_time_entry'),
    path('invoices/', views.invoice_list_view, name='invoice_list'),
    #path('invoices/create/', views.create_invoice_view, name='create_invoice'), 
    path('project/<int:project_id>/invoices/create/', views.create_invoice_project_view, name='create_invoice'),
    path('invoices/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
    path('project/<int:project_id>/invoices/', views.project_invoices_view, name='project_invoices'),
    path('invoices/<int:invoice_id>/update-status/', views.update_invoice_status_view, name='update_invoice_status'),
    path('invoices/<int:invoice_id>/delete/', views.delete_invoice_view, name='delete_invoice'), 
    path('invoices/<int:invoice_id>/pdf/', views.export_invoice_pdf, name='export_invoice_pdf'), 
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
