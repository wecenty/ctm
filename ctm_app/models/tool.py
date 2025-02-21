
from django.db import models
from django.contrib.auth.models import User

from .base import SoftDeletableModel

class Tool(SoftDeletableModel):
    """Модель для справочника инструментов"""
    article = models.IntegerField(verbose_name="Артикул")
    name = models.CharField(max_length=200, verbose_name="Название инструмента")
    resource = models.IntegerField(verbose_name="Ресурс")
    diameter = models.FloatField(verbose_name="Диаметр (мм)")
    length = models.FloatField(verbose_name="Длина (мм)")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)
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
