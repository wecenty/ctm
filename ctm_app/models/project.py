
from django.db import models
from django.contrib.auth.models import User
from .catalog import Catalog
from .base import SoftDeletableModel

class Project(SoftDeletableModel):
    """
    Модель проекта обработки.
    
    Проект может быть:
    - Самостоятельным или иметь родительский проект (поле parent)
    - Иметь несколько версий (поле version)
    - Содержать количество изделий (поле quantity)
    
    Проекты организованы в каталоги для удобной навигации.
    Поддерживает систему версионирования и мягкое удаление.
    """
    name = models.CharField(max_length=200, verbose_name="Название проекта", db_index=True)
    version = models.IntegerField(default=0, verbose_name="Версия")
    quantity = models.IntegerField(default=1, verbose_name="Количество")
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
