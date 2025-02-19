from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
import io
from ..models import Tool
from ..forms import ToolForm, ToolImportForm
from ..importers import ToolImporter, create_example_file
import base64


@login_required
def tool_list(request):
    """Отображение списка инструментов с пагинацией и поиском"""
    # Базовый QuerySet с оптимизацией
    tools_queryset = Tool.objects.select_related('creator').filter(date_delete__isnull=True)

    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        tools_queryset = tools_queryset.filter(
            Q(name__icontains=search_query) |
            Q(creator__username__icontains=search_query)
        )

    # Сортировка
    sort_by = request.GET.get('sort', '-created_at')
    tools_queryset = tools_queryset.order_by(sort_by)

    # Пагинация
    paginator = Paginator(tools_queryset, 10)  # 10 инструментов на страницу
    page = request.GET.get('page')
    tools = paginator.get_page(page)

    context = {
        'tools': tools,
        'can_create': request.user.has_perm('projects.add_tool'),
        'search_query': search_query,
        'sort_by': sort_by
    }

    return render(request, 'projects/tool_list.html', context)


@login_required
@permission_required('projects.add_tool', raise_exception=True)
def tool_create(request):
    """Создание нового инструмента"""
    if request.method == 'POST':
        form = ToolForm(request.POST)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.creator = request.user
            tool.save()
            return redirect('tool_list')
    else:
        form = ToolForm()

    context = {
        'form': form,
        'is_edit': False,
        'form_action': reverse('tool_create'),
        'submit_label': 'Добавить инструмент'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/tool_form.html', context)


@login_required
@permission_required('projects.change_tool', raise_exception=True)
def tool_edit(request, pk):
    """Редактирование инструмента"""
    tool = get_object_or_404(Tool.objects.select_related('creator'), pk=pk)

    if request.method == 'POST':
        form = ToolForm(request.POST, instance=tool)
        if form.is_valid():
            form.save()
            return redirect('tool_list')
    else:
        form = ToolForm(instance=tool)

    context = {
        'form': form,
        'tool': tool,
        'is_edit': True,
        'form_action': reverse('tool_edit', args=[pk]),
        'submit_label': 'Сохранить'
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'projects/forms/modal_base.html', context)
    return render(request, 'projects/tool_form.html', context)


@login_required
@permission_required('projects.delete_tool', raise_exception=True)
def tool_delete(request, pk):
    """Удаление инструмента"""
    tool = get_object_or_404(Tool, pk=pk)
    if request.method == 'POST':
        tool.soft_delete(request.user)
        return redirect('tool_list')
    return redirect('tool_list')


@login_required
@permission_required('projects.add_tool', raise_exception=True)
def tool_import(request):
    """Импорт инструментов из Excel файла"""
    if request.method == 'POST':
        if 'validate' in request.POST and request.FILES.get('file'):
            form = ToolImportForm(request.POST, request.FILES)
            if form.is_valid():
                # Конвертируем байты файла в base64 строку
                file_content = request.FILES['file'].read()
                file_content_b64 = base64.b64encode(file_content).decode('utf-8')

                # Сохраняем в сессию
                request.session['temp_file'] = file_content_b64
                request.session['filename'] = request.FILES['file'].name

                # Создаем BytesIO объект из данных
                file_data = io.BytesIO(file_content)
                file_data.name = request.FILES['file'].name

                importer = ToolImporter(file_data, request.user)
                is_valid = importer.validate_and_preview()

                valid_rows = len([row for row in importer.preview_data if not row.get('errors')])
                invalid_rows = len([row for row in importer.preview_data if row.get('errors')])

                return render(request, 'projects/tool_import.html', {
                    'form': form,
                    'preview_data': importer.preview_data,
                    'errors': importer.errors,
                    'is_valid': True,  # Разрешаем импорт даже при наличии ошибок
                    'filename': request.FILES['file'].name,
                    'valid_rows': valid_rows,
                    'invalid_rows': invalid_rows
                })


        elif 'import' in request.POST and request.session.get('temp_file'):

            # Получаем данные файла из сессии
            file_content = base64.b64decode(request.session['temp_file'])
            filename = request.session.get('filename', 'import.xlsx')

            # Создаем BytesIO объект
            file_data = io.BytesIO(file_content)
            file_data.name = filename
            importer = ToolImporter(file_data, request.user)

            successful, failed, skipped = importer.import_tools()

            # Очищаем временное хранилище
            del request.session['temp_file']
            del request.session['filename']

            return redirect('tool_list')

        form = ToolImportForm()
    else:
        form = ToolImportForm()

    return render(request, 'projects/tool_import.html', {'form': form})


@login_required
def tool_import_example(request):
    """Скачивание примера файла для импорта"""
    buffer = create_example_file()

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=tool_import_example.xlsx'
    return response
