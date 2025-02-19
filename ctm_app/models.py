# projects/models.py

from django.db import models
from django.contrib.auth.models import User

class Catalog(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название каталога", db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                             related_name='children', verbose_name="Родительский каталог", db_index=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель",
                              related_name='created_catalogs', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    date_delete = models.DateTimeField(null=True, blank=True, verbose_name="Дата удаления")
    who_delete = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name="Кто удалил", related_name='deleted_catalogs')

    class Meta:
        indexes = [
            models.Index(fields=['name', 'parent', 'creator']),
            models.Index(fields=['date_delete']),
        ]
        verbose_name = "Каталог"
        verbose_name_plural = "Каталоги"

    def __str__(self):
        return self.name

    def soft_delete(self, user):
        """Мягкое удаление каталога"""
        from django.utils import timezone
        self.date_delete = timezone.now()
        self.who_delete = user
        self.save()


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название проекта", db_index=True)
    version = models.IntegerField(default=0, verbose_name="Версия")
    quantity = models.IntegerField(default=1, verbose_name="Количество")  # Новое поле
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE,
                              related_name='projects', verbose_name="Каталог", db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                             related_name='children', verbose_name="Родительский проект", db_index=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель",
                              related_name='created_projects', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    date_delete = models.DateTimeField(null=True, blank=True, verbose_name="Дата удаления")
    who_delete = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name="Кто удалил", related_name='deleted_projects')

    class Meta:
        indexes = [
            models.Index(fields=['name', 'catalog', 'parent', 'creator']),
            models.Index(fields=['date_delete']),
        ]

    def __str__(self):
        base_name = self.name
        if self.version > 0:
            base_name += f" (вер. {self.version})"
        if self.quantity > 1:
            base_name += f" x{self.quantity}"
        return base_name

    def soft_delete(self, user):
        """Мягкое удаление проекта"""
        from django.utils import timezone
        self.date_delete = timezone.now()
        self.who_delete = user
        self.save()


class Tool(models.Model):
    """Модель для справочника инструментов"""
    article = models.IntegerField(verbose_name="Артикул")
    name = models.CharField(max_length=200, verbose_name="Название инструмента")
    resource = models.IntegerField(verbose_name="Ресурс")
    diameter = models.FloatField(verbose_name="Диаметр (мм)")
    length = models.FloatField(verbose_name="Длина (мм)")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)
    # Добавляем поля для мягкого удаления
    date_delete = models.DateTimeField(null=True, blank=True, verbose_name="Дата удаления")
    who_delete = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Кто удалил",
        related_name='deleted_tools'
    )

    def soft_delete(self, user):
        """Мягкое удаление инструмента"""
        from django.utils import timezone
        self.date_delete = timezone.now()
        self.who_delete = user
        self.save()

    def __str__(self):
        return f"{self.article} - {self.name} (⌀{self.diameter}мм, L={self.length}мм)"

    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"


from decimal import Decimal

class ProjectTool(models.Model):
    """Модель для инструментов в проекте"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tools')
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, verbose_name="Инструмент")
    application_time = models.IntegerField(verbose_name="Время применения (сек)")
    quantity = models.DecimalField(
        verbose_name="Количество инструментов",
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    def save(self, *args, force_recalc=True, **kwargs):
        if force_recalc:
            self.quantity = self.calculate_quantity()
        super().save(*args, **kwargs)

    def calculate_quantity(self):
        """Рассчитывает количество инструментов по формуле"""
        if self.application_time > 0 and hasattr(self, 'project') and hasattr(self, 'tool'):
            try:
                # Используем Decimal для точных вычислений
                return Decimal(str(self.tool.resource)) / Decimal(str(self.application_time)) * Decimal(str(self.project.quantity))
            except (ZeroDivisionError, AttributeError):
                return Decimal('0.00')
        return Decimal('0.00')

    def recalculate_quantity(self):
        """Метод для пересчета количества с сохранением в базе"""
        new_quantity = self.calculate_quantity()
        if new_quantity != self.quantity:
            self.quantity = new_quantity
            self.save(force_recalc=False)

    def __str__(self):
        return f"{self.tool.name} ({self.quantity:.2f} шт.) в проекте {self.project.name}"

    class Meta:
        verbose_name = "Инструмент проекта"
        verbose_name_plural = "Инструменты проекта"