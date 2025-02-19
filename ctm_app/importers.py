import io
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Tool


class ToolImporter:
    def __init__(self, file, user):
        self.file = file
        self.user = user
        self.errors = []
        self.preview_data = []
        self.processed_data = []

    def validate_and_preview(self):
        try:
            df = pd.read_excel(self.file)
            required_columns = ['article', 'name', 'resource', 'diameter', 'length']

            # Проверка наличия всех необходимых колонок
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")
                return False

            # Проверка данных
            for index, row in df.iterrows():
                row_data = {
                    'article': row['article'],
                    'name': row['name'],
                    'resource': row['resource'],
                    'diameter': row['diameter'],
                    'length': row['length'],
                    'errors': [],
                    'row_number': index + 2  # +2 т.к. Excel начинается с 1 и есть заголовок
                }

                # Проверка артикула
                try:
                    article = int(row['article'])
                    if article <= 0:
                        row_data['errors'].append("Артикул должен быть положительным числом")
                    elif Tool.objects.filter(article=article, date_delete__isnull=True).exists():
                        row_data['errors'].append(f"Артикул {article} уже существует")
                except (ValueError, TypeError):
                    row_data['errors'].append("Артикул должен быть целым числом")

                # Проверка названия
                if pd.isna(row['name']) or str(row['name']).strip() == '':
                    row_data['errors'].append("Название не может быть пустым")
                elif len(str(row['name'])) > 200:
                    row_data['errors'].append("Название слишком длинное (максимум 200 символов)")

                # Проверка ресурса
                try:
                    resource = int(row['resource'])
                    if resource <= 0:
                        row_data['errors'].append("Ресурс должен быть положительным числом")
                except (ValueError, TypeError):
                    row_data['errors'].append("Ресурс должен быть целым числом")

                # Проверка диаметра
                try:
                    diameter = float(row['diameter'])
                    if diameter <= 0:
                        row_data['errors'].append("Диаметр должен быть положительным числом")
                except (ValueError, TypeError):
                    row_data['errors'].append("Диаметр должен быть числом")

                # Проверка длины
                try:
                    length = float(row['length'])
                    if length <= 0:
                        row_data['errors'].append("Длина должна быть положительным числом")
                except (ValueError, TypeError):
                    row_data['errors'].append("Длина должна быть числом")

                self.preview_data.append(row_data)

            return len([row for row in self.preview_data if row['errors']]) == 0

        except Exception as e:
            self.errors.append(f"Ошибка обработки файла: {str(e)}")
            return False

    def import_tools(self):
        successful = 0
        failed = 0

        # Сначала выполняем валидацию
        if not self.preview_data:
            self.validate_and_preview()

        for data in self.preview_data:
            try:
                if not data.get('errors'):  # Проверяем отсутствие ошибок
                    Tool.objects.create(
                        article=int(data['article']),
                        name=str(data['name']),
                        resource=int(data['resource']),
                        diameter=float(data['diameter']),
                        length=float(data['length']),
                        creator=self.user
                    )
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Error importing row: {data}, error: {str(e)}")  # Для отладки
                failed += 1
                self.errors.append(f"Ошибка импорта строки {data.get('row_number', '?')}: {str(e)}")

        print(f"Import results: successful={successful}, failed={failed}")  # Для отладки
        return successful, failed


def create_example_file():
    """Создает пример Excel файла для импорта инструментов"""
    data = {
        'article': [1001, 1002, 1003],
        'name': [
            'Фреза концевая 10мм',
            'Сверло 8мм',
            'Метчик М12'
        ],
        'resource': [1000, 500, 300],
        'diameter': [10.0, 8.0, 12.0],
        'length': [75.0, 80.0, 90.0]
    }

    df = pd.DataFrame(data)

    # Создаем буфер в памяти
    buffer = io.BytesIO()

    # Создаем writer для Excel
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Инструменты')

        # Получаем объект workbook и worksheet
        workbook = writer.book
        worksheet = writer.sheets['Инструменты']

        # Форматы для заголовков и данных
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1
        })

        # Устанавливаем ширину колонок
        worksheet.set_column('A:A', 12)  # Артикул
        worksheet.set_column('B:B', 30)  # Название
        worksheet.set_column('C:C', 15)  # Ресурс
        worksheet.set_column('D:D', 15)  # Диаметр
        worksheet.set_column('E:E', 15)  # Длина

        # Форматируем заголовки
        for col_num, column in enumerate(df.columns):
            worksheet.write(0, col_num, column, header_format)

        # Добавляем инструкции на новый лист
        instructions = workbook.add_worksheet('Инструкция')
        instructions.write('A1', 'Инструкция по заполнению', workbook.add_format({'bold': True, 'font_size': 12}))
        instructions.write('A3', 'Требования к данным:')
        instructions.write('A4', '1. Артикул - уникальное целое число')
        instructions.write('A5', '2. Название - текст (не пустой)')
        instructions.write('A6', '3. Ресурс - целое положительное число')
        instructions.write('A7', '4. Диаметр - положительное число (мм)')
        instructions.write('A8', '5. Длина - положительное число (мм)')

        instructions.write('A10', 'Особые условия:')
        instructions.write('A11', '• Артикул должен быть уникальным')
        instructions.write('A12', '• Все числовые значения должны быть положительными')
        instructions.write('A13', '• Название не может быть пустым')

        # Устанавливаем ширину колонок в инструкции
        instructions.set_column('A:A', 50)

    buffer.seek(0)
    return buffer


class ToolImporter:
    def __init__(self, file, user):
        self.file = file
        self.user = user
        self.errors = []
        self.preview_data = []
        self.processed_data = []

    def validate_and_preview(self):
        try:
            df = pd.read_excel(self.file)
            required_columns = ['article', 'name', 'resource', 'diameter', 'length']

            # Проверка наличия всех необходимых колонок
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")
                return False

            # Проверка данных
            for index, row in df.iterrows():
                row_data = {
                    'article': row['article'],
                    'name': row['name'],
                    'resource': row['resource'],
                    'diameter': row['diameter'],
                    'length': row['length'],
                    'errors': [],
                    'row_number': index + 2  # +2 т.к. Excel начинается с 1 и есть заголовок
                }

                # Проверка артикула
                try:
                    article = int(row['article'])
                    if article <= 0:
                        row_data['errors'].append("Артикул должен быть положительным числом")
                    elif Tool.objects.filter(article=article, date_delete__isnull=True).exists():
                        row_data['errors'].append(f"Артикул {article} уже существует")
                except (ValueError, TypeError):
                    row_data['errors'].append("Артикул должен быть целым числом")

                # Проверка названия
                if pd.isna(row['name']) or str(row['name']).strip() == '':
                    row_data['errors'].append("Название не может быть пустым")
                elif len(str(row['name'])) > 200:
                    row_data['errors'].append("Название слишком длинное (максимум 200 символов)")

                # Проверка ресурса
                try:
                    resource = int(row['resource'])
                    if resource <= 0:
                        row_data['errors'].append("Ресурс должен быть положительным числом")
                except (ValueError, TypeError):
                    row_data['errors'].append("Ресурс должен быть целым числом")

                # Проверка диаметра
                try:
                    diameter = float(row['diameter'])
                    if diameter <= 0:
                        row_data['errors'].append("Диаметр должен быть положительным числом")
                except (ValueError, TypeError):
                    row_data['errors'].append("Диаметр должен быть числом")

                # Проверка длины
                try:
                    length = float(row['length'])
                    if length <= 0:
                        row_data['errors'].append("Длина должна быть положительным числом")
                except (ValueError, TypeError):
                    row_data['errors'].append("Длина должна быть числом")

                self.preview_data.append(row_data)

            return len([row for row in self.preview_data if row['errors']]) == 0

        except Exception as e:
            self.errors.append(f"Ошибка обработки файла: {str(e)}")
            return False

    def import_tools(self):
        successful = 0
        failed = 0
        skipped = 0

        # Сначала выполняем валидацию если еще не выполнена
        if not self.preview_data:
            self.validate_and_preview()

        for data in self.preview_data:
            try:
                # Импортируем только строки без ошибок
                if not data.get('errors'):
                    Tool.objects.create(
                        article=int(data['article']),
                        name=str(data['name']),
                        resource=int(data['resource']),
                        diameter=float(data['diameter']),
                        length=float(data['length']),
                        creator=self.user
                    )
                    successful += 1
                else:
                    skipped += 1  # Увеличиваем счетчик пропущенных строк
            except Exception as e:
                print(f"Error importing row: {data}, error: {str(e)}")  # Для отладки
                failed += 1
                self.errors.append(f"Ошибка импорта строки {data.get('row_number', '?')}: {str(e)}")

        print(f"Import results: successful={successful}, failed={failed}, skipped={skipped}")  # Для отладки
        return successful, failed, skipped
