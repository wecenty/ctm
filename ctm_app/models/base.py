
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SoftDeletableModel(models.Model):
    """
    Абстрактная модель для поддержки мягкого удаления.
    """
    date_delete = models.DateTimeField(null=True, blank=True, verbose_name="Дата удаления", db_index=True)
    who_delete = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Кто удалил",
        related_name="deleted_%(class)ss"
    )

    class Meta:
        abstract = True

    def soft_delete(self, user):
        """Мягкое удаление объекта"""
        self.date_delete = timezone.now()
        self.who_delete = user
        self.save()
