from django.urls import path
from . import views

urlpatterns = [
    # Каталоги
    path('', views.catalog_list, name='catalog_list'),
    path('catalog/create/', views.catalog_create, name='catalog_create'),
    path('catalog/<int:pk>/', views.catalog_detail, name='catalog_detail'),
    path('catalog/<int:pk>/edit/', views.catalog_edit, name='catalog_edit'),
    path('catalog/<int:pk>/delete/', views.catalog_delete, name='catalog_delete'),
    path('catalog/<int:catalog_id>/export/', views.export_catalog_tools, name='export_catalog_tools'),

    # Проекты
    path('catalog/<int:catalog_id>/project/create/', views.project_create, name='project_create'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('project/<int:project_id>/export/', views.export_project_tools, name='export_project_tools'),

    # Инструменты
    path('tools/', views.tool_list, name='tool_list'),
    path('tool/create/', views.tool_create, name='tool_create'),
    path('tool/<int:pk>/edit/', views.tool_edit, name='tool_edit'),
    path('tool/<int:pk>/delete/', views.tool_delete, name='tool_delete'),

    # Инструменты проекта
    path('project/<int:project_id>/tool/<int:tool_id>/edit/',
         views.project_tool_edit, name='project_tool_edit'),
    path('project/<int:project_id>/tool/<int:tool_id>/delete/',
         views.project_tool_delete, name='project_tool_delete'),
    path('project/<int:project_id>/add_tool/',
         views.project_tool_add, name='project_tool_add'),

    # API endpoints
    path('api/tree/', views.get_tree_json, name='get_tree_json'),
    path('api/search/', views.search_items, name='search_items'),
    path('api/tools-string/<int:project_id>/',
         views.get_tools_string, name='get_tools_string'),
    path('project/<int:project_id>/tool/<int:tool_id>/edit/', views.project_tool_edit, name='project_tool_edit'),
    path('tools/import/', views.tool_import, name='tool_import'),
    path('tools/import/example/', views.tool_import_example, name='tool_import_example'),
]
