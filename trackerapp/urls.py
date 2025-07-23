from django.urls import path
from . import views

urlpatterns = [
    path('', views.demand_list, name='demand_list'),
    path('add/', views.add_demand, name='add_demand'),
    path('edit/<int:demand_id>/', views.edit_demand, name='edit_demand'),
    path('delete/<int:demand_id>/', views.delete_demand, name='delete_demand'),
    path('update_stage/', views.update_stage, name='update_stage'),
    path('edit_stage_dates/', views.edit_stage_dates, name='edit_stage_dates'),
    path('update_weekly_dates/', views.update_weekly_dates, name='update_weekly_dates'),
    path('update_weekly_stage/', views.update_weekly_stage, name='update_weekly_stage'),
    path('update_weekly_progress/', views.update_weekly_progress, name='update_weekly_progress'),
    path('update_weekly_challenge/', views.update_weekly_challenge, name='update_weekly_challenge'),
    
    # Weekly Update URLs
    path('demand/<int:demand_id>/weekly/add/', views.add_weekly_update, name='add_weekly_update'),
    path('demand/<int:demand_id>/weekly/history/', views.weekly_history, name='weekly_history'),
    path('weekly/<int:update_id>/edit/', views.edit_weekly_update, name='edit_weekly_update'),
    path('weekly/<int:update_id>/delete/', views.delete_weekly_update, name='delete_weekly_update'),
    path('weekly/summary/', views.weekly_summary, name='weekly_summary'),
]

