# urls.py

from django.urls import path
from .views import (
    project_create, project_detail, project_edit, project_delete,
    tool_list, tool_create, tool_edit, tool_delete, tool_import, tool_import_example,  # Добавили import и import_example
    project_tool_add, project_tool_edit, project_tool_delete,
    catalog_list, catalog_create, catalog_detail, catalog_edit, catalog_delete,
    get_tree_json, get_tools_string, search_items,
    export_project_tools, export_catalog_tools
)

urlpatterns = [
    # Каталоги
    path('', catalog_list, name='catalog_list'),
    path('catalog/create/', catalog_create, name='catalog_create'),
    path('catalog/<int:pk>/', catalog_detail, name='catalog_detail'),
    path('catalog/<int:pk>/edit/', catalog_edit, name='catalog_edit'),
    path('catalog/<int:pk>/delete/', catalog_delete, name='catalog_delete'),
    path('catalog/<int:catalog_id>/export/', export_catalog_tools, name='export_catalog_tools'),

    # Проекты
    path('catalog/<int:catalog_id>/project/create/', project_create, name='project_create'),
    path('project/<int:pk>/', project_detail, name='project_detail'),
    path('project/<int:pk>/edit/', project_edit, name='project_edit'),
    path('project/<int:pk>/delete/', project_delete, name='project_delete'),
    path('project/<int:project_id>/export/', export_project_tools, name='export_project_tools'),

    # Инструменты
    path('tools/', tool_list, name='tool_list'),
    path('tool/create/', tool_create, name='tool_create'),
    path('tool/<int:pk>/edit/', tool_edit, name='tool_edit'),
    path('tool/<int:pk>/delete/', tool_delete, name='tool_delete'),

    # Инструменты проекта
    path('project/<int:project_id>/tool/<int:tool_id>/edit/',
         project_tool_edit, name='project_tool_edit'),
    path('project/<int:project_id>/tool/<int:tool_id>/delete/',
         project_tool_delete, name='project_tool_delete'),
    path('project/<int:project_id>/add_tool/',
         project_tool_add, name='project_tool_add'),

    # API endpoints
    path('api/tree/', get_tree_json, name='get_tree_json'),
    path('api/search/', search_items, name='search_items'),
    path('api/tools-string/<int:project_id>/',
         get_tools_string, name='get_tools_string'),
    path('project/<int:project_id>/tool/<int:tool_id>/edit/', project_tool_edit, name='project_tool_edit'),
    path('tools/import/', tool_import, name='tool_import'),
    path('tools/import/example/', tool_import_example, name='tool_import_example'),
]
