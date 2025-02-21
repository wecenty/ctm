
from django.db import models
from django.contrib.auth.models import User
from .base import SoftDeletableModel

class Catalog(SoftDeletableModel):
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
