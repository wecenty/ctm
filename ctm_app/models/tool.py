
from django.db import models
from django.contrib.auth.models import User

from .base import SoftDeletableModel

class Tool(SoftDeletableModel):
    """
    Модель для справочника режущих инструментов.
    
    Содержит основные характеристики инструмента:
    - артикул для уникальной идентификации
    - название инструмента
    - ресурс (время работы в минутах)
    - геометрические параметры (диаметр, длина)
    
    Поддерживает мягкое удаление через SoftDeletableModel.
    """
    article = models.IntegerField(verbose_name="Артикул")
    name = models.CharField(max_length=200, verbose_name="Название инструмента")
    resource = models.IntegerField(verbose_name="Ресурс")
    diameter = models.FloatField(verbose_name="Диаметр (мм)")
    length = models.FloatField(verbose_name="Длина (мм)")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.article} - {self.name} (⌀{self.diameter}мм, L={self.length}мм)"

    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"
