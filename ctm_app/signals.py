from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Project, ProjectTool


@receiver(post_save, sender=Project)
def update_project_tools_quantity(sender, instance, **kwargs):
    """
    Пересчитывает количество инструментов при изменении количества проекта
    """
    # Используем транзакцию для обеспечения целостности данных
    with transaction.atomic():
        # Получаем все инструменты проекта одним запросом
        project_tools = ProjectTool.objects.select_related('tool').filter(project=instance)

        # Пересчитываем количество для каждого инструмента
        for tool in project_tools:
            tool.recalculate_quantity()
