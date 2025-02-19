from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.utils.encoding import escape_uri_path
from ..models import Catalog, Project, ProjectTool
from ..exporters import ToolsExporter



@login_required
def get_tree_json(request):
    """API endpoint для получения дерева каталогов и проектов"""
    catalogs = Catalog.objects.filter(
        date_delete__isnull=True
    ).select_related('creator').prefetch_related(
        Prefetch(
            'projects',
            queryset=Project.objects.filter(date_delete__isnull=True)
        )
    )

    def build_tree_data(parent_id=None):
        nodes = []

        # Добавляем каталоги текущего уровня
        for catalog in catalogs:
            if catalog.parent_id == parent_id:
                catalog_node = {
                    'text': f'<i class="bi bi-folder"></i> {catalog.name}',
                    'itemId': f'c_{catalog.id}',
                    'type': 'catalog',
                    'href': reverse('catalog_detail', kwargs={'pk': catalog.id}),
                    'nodes': []
                }

                # Добавляем подкаталоги
                catalog_node['nodes'].extend(build_tree_data(catalog.id))

                # Добавляем проекты каталога
                for project in catalog.projects.all():
                    project_text = f'<i class="bi bi-gear"></i> {project.name}'
                    if project.version > 0:
                        project_text += f" (вер. {project.version})"
                    if project.quantity > 1:
                        project_text += f" x{project.quantity}"

                    catalog_node['nodes'].append({
                        'text': project_text,
                        'itemId': f'p_{project.id}',
                        'type': 'project',
                        'href': reverse('project_detail', kwargs={'pk': project.id})
                    })

                nodes.append(catalog_node)

        return nodes

    tree_data = build_tree_data()
    return JsonResponse(tree_data, safe=False)


@login_required
def search_items(request):
    """API endpoint для поиска каталогов и проектов"""
    search_query = request.GET.get('query', '').strip()
    if not search_query:
        return JsonResponse([], safe=False)

    # Поиск по каталогам
    catalogs = Catalog.objects.filter(
        name__icontains=search_query,
        date_delete__isnull=True
    ).values('id', 'name')[:5]

    # Поиск по проектам
    projects = Project.objects.filter(
        name__icontains=search_query,
        date_delete__isnull=True
    ).values('id', 'name', 'version', 'quantity')[:5]

    results = []

    # Добавляем каталоги
    for catalog in catalogs:
        results.append({
            'id': f'c_{catalog["id"]}',
            'name': f'<i class="bi bi-folder"></i> {catalog["name"]}',
            'url': reverse('catalog_detail', kwargs={'pk': catalog['id']})
        })

    # Добавляем проекты
    for project in projects:
        name = project['name']
        if project['version'] > 0:
            name += f" (вер. {project['version']})"
        if project['quantity'] > 1:
            name += f" x{project['quantity']}"

        results.append({
            'id': f'p_{project["id"]}',
            'name': f'<i class="bi bi-gear"></i> {name}',
            'url': reverse('project_detail', kwargs={'pk': project['id']})
        })

    return JsonResponse(results, safe=False)


@login_required
def get_tools_string(request, project_id):
    """API endpoint для получения строки с информацией об инструментах проекта"""
    project = get_object_or_404(Project, pk=project_id)
    tools = ProjectTool.objects.filter(project=project).select_related('tool')

    tools_string = ';'.join([
        f"{tool.tool.name}:⌀{tool.tool.diameter}мм:L{tool.tool.length}мм:"
        f"Ресурс={tool.tool.resource}:Кол-во={tool.quantity}:Время={tool.application_time}сек"
        for tool in tools
    ])

    return JsonResponse({'tools_string': tools_string})


@login_required
def export_project_tools(request, project_id):
    """Экспорт инструментов проекта в Excel"""
    project = get_object_or_404(Project, pk=project_id, date_delete__isnull=True)

    exporter = ToolsExporter()
    exporter.collect_project_tools(project)

    # Формируем имя файла
    filename = project.name
    if project.version > 0:
        filename += f" (вер. {project.version})"
    filename += ".xlsx"
    encoded_filename = escape_uri_path(filename)

    response = HttpResponse(
        exporter.export_to_excel(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response[
        'Content-Disposition'] = f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    return response


@login_required
def export_catalog_tools(request, catalog_id):
    """Экспорт инструментов каталога в Excel"""
    catalog = get_object_or_404(Catalog, pk=catalog_id, date_delete__isnull=True)

    exporter = ToolsExporter()
    exporter.collect_catalog_tools(catalog)

    # Формируем имя файла
    filename = f"{catalog.name}.xlsx"
    encoded_filename = escape_uri_path(filename)

    response = HttpResponse(
        exporter.export_to_excel(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response[
        'Content-Disposition'] = f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    return response