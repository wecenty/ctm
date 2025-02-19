# views/project_views.py

from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Prefetch
from ..models import Project, ProjectTool, Catalog
from ..forms import ProjectForm


@login_required
@permission_required('projects.add_project', raise_exception=True)
def project_create(request, catalog_id):
    """Создание нового проекта"""
    catalog = get_object_or_404(Catalog, pk=catalog_id, date_delete__isnull=True)

    if request.method == 'POST':
        form = ProjectForm(catalog, request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.catalog = catalog
            project.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(catalog)

    context = {
        'form': form,
        'catalog': catalog,
        'is_edit': False,
        'form_action': reverse('project_create', args=[catalog_id]),
        'submit_label': 'Создать проект'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/project_form.html', context)


@login_required
@permission_required('projects.change_project', raise_exception=True)
def project_edit(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('catalog'),
        pk=pk,
        date_delete__isnull=True
    )

    if request.method == 'POST':
        form = ProjectForm(project.catalog, request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Проект "{project.name}" успешно обновлен.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(project.catalog, instance=project)

    context = {
        'form': form,
        'object': project,
        'is_edit': True,
        'form_action': reverse('project_edit', args=[pk]),
        'submit_label': 'Сохранить'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/project_form.html', context)


@login_required
def project_detail(request, pk):
    """Просмотр деталей проекта"""
    project = get_object_or_404(
        Project.objects.select_related('creator', 'catalog').prefetch_related(
            Prefetch(
                'tools',
                queryset=ProjectTool.objects.select_related('tool')
            )
        ),
        pk=pk,
        date_delete__isnull=True
    )

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tools': project.tools.all(),
        'current_catalog': project.catalog
    })


@login_required
@permission_required('projects.delete_project', raise_exception=True)
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.soft_delete(request.user)
        return redirect('catalog_detail', pk=project.catalog.pk)
    return redirect('project_detail', pk=pk)
