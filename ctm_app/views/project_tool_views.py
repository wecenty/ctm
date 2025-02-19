# views/project_tool_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from ..models import Project, ProjectTool
from django.template.loader import render_to_string
from django.http import HttpResponse
from ..forms import ProjectToolForm
from django.urls import reverse


@login_required
@permission_required('projects.add_projecttool', raise_exception=True)
def project_tool_add(request, project_id):
    project = get_object_or_404(Project, pk=project_id, date_delete__isnull=True)

    if request.method == 'POST':
        form = ProjectToolForm(request.POST)
        if form.is_valid():
            project_tool = form.save(commit=False)
            project_tool.project = project
            project_tool.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectToolForm()

    context = {
        'form': form,
        'project': project,
        'is_edit': False,
        'form_action': reverse('project_tool_add', args=[project_id]),
        'submit_label': 'Добавить инструмент'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/project_tool_form.html', context)


@login_required
@permission_required('projects.change_projecttool', raise_exception=True)
def project_tool_edit(request, project_id, tool_id):
    project_tool = get_object_or_404(
        ProjectTool.objects.select_related('project', 'tool'),
        project_id=project_id,
        id=tool_id,
        project__date_delete__isnull=True
    )

    if request.method == 'POST':
        form = ProjectToolForm(request.POST, instance=project_tool)
        if form.is_valid():
            form.save()
            return redirect('project_detail', pk=project_id)
    else:
        form = ProjectToolForm(instance=project_tool)

    context = {
        'form': form,
        'project': project_tool.project,
        'is_edit': True,
        'tool_info': project_tool.tool,
        # Убираем слеш в конце URL
        'form_action': reverse('project_tool_edit', args=[project_id, tool_id]).rstrip('/'),
        'submit_label': 'Сохранить'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/project_tool_form.html', context)


@login_required
@permission_required('projects.delete_projecttool', raise_exception=True)
def project_tool_delete(request, project_id, tool_id):
    """
    Удаление инструмента из проекта
    """
    project_tool = get_object_or_404(
        ProjectTool,
        project_id=project_id,
        id=tool_id,
        project__date_delete__isnull=True
    )
    if request.method == 'POST':
        project_tool.delete()
    return redirect('project_detail', pk=project_id)