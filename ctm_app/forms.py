# projects/forms.py

from django import forms
from .models import Project, Tool, ProjectTool, Catalog
from django.core.exceptions import ValidationError

class CatalogForm(forms.ModelForm):
    class Meta:
        model = Catalog
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исключаем удаленные каталоги из выбора родителя
        self.fields['parent'].queryset = Catalog.objects.filter(date_delete__isnull=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'version', 'quantity', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'version': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'parent': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, catalog=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if catalog:
            # Фильтруем проекты для поля parent
            self.fields['parent'].queryset = Project.objects.filter(
                catalog=catalog,
                date_delete__isnull=True
            )
            if self.instance and self.instance.id:
                # Исключаем текущий проект из списка возможных родителей
                self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(
                    pk=self.instance.id
                )
        else:
            self.fields['parent'].queryset = Project.objects.none()

        self.fields['parent'].label_from_instance = lambda obj: str(obj)

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['article', 'name', 'resource', 'diameter', 'length']
        widgets = {
            'article': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'resource': forms.NumberInput(attrs={'class': 'form-control'}),
            'diameter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'})
        }

    def clean_article(self):
        article = self.cleaned_data.get('article')
        if article:
            # Проверяем только неудаленные инструменты
            existing_tool = Tool.objects.filter(
                article=article,
                date_delete__isnull=True
            ).exists()
            if existing_tool:
                if not self.instance.pk or (self.instance.pk and self.instance.article != article):
                    raise ValidationError(f'Инструмент с артикулом {article} уже создан')
        return article

class ProjectToolForm(forms.ModelForm):
    class Meta:
        model = ProjectTool
        fields = ['tool', 'application_time']
        widgets = {
            'tool': forms.Select(attrs={'class': 'form-control'}),
            'application_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Введите время применения в секундах'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только неудаленные инструменты
        self.fields['tool'].queryset = Tool.objects.filter(date_delete__isnull=True)
        self.fields['tool'].help_text = "Выберите инструмент из справочника"
        self.fields['application_time'].help_text = ("Введите время применения инструмента в секундах. "
                                                   "Количество будет рассчитано автоматически.")

class ToolImportForm(forms.Form):
    file = forms.FileField(
        label='Excel файл',
        help_text='Поддерживаются форматы .xls и .xlsx',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xls,.xlsx'})
    )