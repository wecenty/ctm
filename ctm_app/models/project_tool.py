
from decimal import Decimal
from django.db import models
from .project import Project
from .tool import Tool

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
