from decimal import Decimal
from collections import defaultdict
import xlsxwriter
from io import BytesIO
from .models import Catalog, Project, ProjectTool


class ToolsExporter:
    def __init__(self):
        self.tools_data = defaultdict(lambda: {'quantity': Decimal('0.00'), 'time': 0})

    def collect_project_tools(self, project):
        """Собирает данные об инструментах проекта"""
        tools = ProjectTool.objects.select_related('tool').filter(project=project)
        for tool in tools:
            key = (tool.tool.id, tool.tool.name, tool.tool.diameter, tool.tool.length, tool.tool.resource)
            self.tools_data[key]['quantity'] += tool.quantity
            self.tools_data[key]['time'] += tool.application_time

    def collect_catalog_tools(self, catalog):
        """Рекурсивно собирает данные об инструментах каталога и его подкаталогов"""
        # Собираем инструменты проектов текущего каталога
        projects = Project.objects.filter(catalog=catalog, date_delete__isnull=True)
        for project in projects:
            self.collect_project_tools(project)

        # Рекурсивно обрабатываем подкаталоги
        subcatalogs = Catalog.objects.filter(parent=catalog, date_delete__isnull=True)
        for subcatalog in subcatalogs:
            self.collect_catalog_tools(subcatalog)

    def export_to_excel(self, filename="tools_export.xlsx"):
        """Экспортирует собранные данные в Excel"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Инструменты")

        # Стили для заголовков
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1
        })

        # Стили для данных
        data_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        number_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '0.00'
        })

        # Заголовки
        headers = [
            'Название инструмента',
            'Диаметр (мм)',
            'Длина (мм)',
            'Ресурс',
            'Количество',
            'Время (сек)'
        ]

        # Устанавливаем ширину столбцов
        worksheet.set_column(0, 0, 40)  # Название
        worksheet.set_column(1, 5, 15)  # Остальные столбцы

        # Записываем заголовки
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Записываем данные
        row = 1
        for (tool_id, name, diameter, length, resource), data in self.tools_data.items():
            worksheet.write(row, 0, name, data_format)
            worksheet.write(row, 1, diameter, number_format)
            worksheet.write(row, 2, length, number_format)
            worksheet.write(row, 3, resource, number_format)
            worksheet.write(row, 4, float(data['quantity']), number_format)
            worksheet.write(row, 5, data['time'], number_format)
            row += 1

        workbook.close()
        return output.getvalue()