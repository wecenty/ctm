# views/catalog_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Prefetch
from ..models import Catalog, Project
from django.template.loader import render_to_string
from django.http import HttpResponse
from ..forms import CatalogForm
from django.urls import reverse


@login_required
def catalog_list(request):
    """Отображение списка каталогов"""
    catalogs = Catalog.objects.filter(
        date_delete__isnull=True,
        parent__isnull=True
    ).prefetch_related(
        Prefetch(
            'projects',
            queryset=Project.objects.filter(date_delete__isnull=True)
        )
    )

    return render(request, 'projects/catalog_list.html', {
        'catalogs': catalogs,
        'current_catalog': None
    })


@login_required
def catalog_detail(request, pk):
    """Просмотр содержимого каталога"""
    catalog = get_object_or_404(
        Catalog.objects.prefetch_related(
            Prefetch('projects', queryset=Project.objects.filter(date_delete__isnull=True))
        ),
        pk=pk,
        date_delete__isnull=True
    )

    return render(request, 'projects/catalog_detail.html', {
        'catalog': catalog,
        'projects': catalog.projects.all(),
        'current_catalog': catalog
    })


@login_required
@permission_required('projects.add_catalog', raise_exception=True)
def catalog_create(request):
    if request.method == 'POST':
        form = CatalogForm(request.POST)
        if form.is_valid():
            catalog = form.save(commit=False)
            catalog.creator = request.user
            catalog.save()
            return redirect('catalog_detail', pk=catalog.pk)
    else:
        form = CatalogForm()

    context = {
        'form': form,
        'is_edit': False,
        'form_action': reverse('catalog_create'),
        'submit_label': 'Создать каталог'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/catalog_form.html', context)


@login_required
@permission_required('projects.change_catalog', raise_exception=True)
def catalog_edit(request, pk):
    catalog = get_object_or_404(Catalog, pk=pk, date_delete__isnull=True)

    if request.method == 'POST':
        form = CatalogForm(request.POST, instance=catalog)
        if form.is_valid():
            form.save()
            return redirect('catalog_detail', pk=catalog.pk)
    else:
        form = CatalogForm(instance=catalog)

    context = {
        'form': form,
        'catalog': catalog,
        'is_edit': True
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse(render_to_string('projects/forms/catalog_form_modal.html',
                                             context, request=request))
    return render(request, 'projects/catalog_form.html', context)


@login_required
@permission_required('projects.delete_catalog', raise_exception=True)
def catalog_delete(request, pk):
    """Мягкое удаление каталога"""
    catalog = get_object_or_404(Catalog, pk=pk, date_delete__isnull=True)

    if request.method == 'POST':
        # Получаем все подкаталоги рекурсивно
        def get_child_catalogs(parent_catalog):
            children = Catalog.objects.filter(
                parent=parent_catalog,
                date_delete__isnull=True
            )
            result = list(children)
            for child in children:
                result.extend(get_child_catalogs(child))
            return result

        # Помечаем удаленными каталог и все его подкаталоги
        catalogs_to_delete = [catalog] + get_child_catalogs(catalog)

        # Помечаем удаленными все проекты в этих каталогах
        projects_to_delete = Project.objects.filter(
            catalog__in=catalogs_to_delete,
            date_delete__isnull=True
        )

        now = timezone.now()

        # Удаляем каталоги
        for cat in catalogs_to_delete:
            cat.date_delete = now
            cat.who_delete = request.user
            cat.save()

        # Удаляем проекты
        for project in projects_to_delete:
            project.date_delete = now
            project.who_delete = request.user
            project.save()

        message_parts = [f'Каталог "{catalog.name}"']
        if len(catalogs_to_delete) > 1:
            message_parts.append(f'{len(catalogs_to_delete) - 1} подкаталогов')
        if projects_to_delete:
            message_parts.append(f'{projects_to_delete.count()} проектов')

        messages.success(request, f'{", ".join(message_parts)} успешно удалены.')
        return redirect('catalog_list')

    return redirect('catalog_detail', pk=pk)
