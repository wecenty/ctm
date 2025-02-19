from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ctm_app.models import Project, Tool, ProjectTool, Catalog


class Command(BaseCommand):
    help = 'Creates default user groups with permissions'

    def handle(self, *args, **kwargs):
        # Delete existing groups to avoid permission duplication
        Group.objects.filter(name__in=['Creator', 'Typical_user']).delete()

        # Get content types
        catalog_ct = ContentType.objects.get_for_model(Catalog)
        project_ct = ContentType.objects.get_for_model(Project)
        tool_ct = ContentType.objects.get_for_model(Tool)
        project_tool_ct = ContentType.objects.get_for_model(ProjectTool)

        # Create Creator group
        creator_group = Group.objects.create(name='Creator')
        creator_permissions = {
            catalog_ct: ['add', 'change', 'delete', 'view'],
            project_ct: ['add', 'change', 'delete', 'view'],
            tool_ct: ['add', 'change', 'delete', 'view'],
            project_tool_ct: ['add', 'change', 'delete', 'view']
        }

        # Create Typical_user group
        typical_user_group = Group.objects.create(name='Typical_user')
        typical_user_permissions = {
            catalog_ct: ['view'],
            project_ct: ['view'],
            tool_ct: ['view'],
            project_tool_ct: ['view']
        }

        # Assign Creator permissions
        for content_type, actions in creator_permissions.items():
            for action in actions:
                permission = Permission.objects.get(
                    codename=f'{action}_{content_type.model}',
                    content_type=content_type,
                )
                creator_group.permissions.add(permission)

        # Assign Typical_user permissions
        for content_type, actions in typical_user_permissions.items():
            for action in actions:
                permission = Permission.objects.get(
                    codename=f'{action}_{content_type.model}',
                    content_type=content_type,
                )
                typical_user_group.permissions.add(permission)

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created groups with permissions:\n'
                f'Creator: {creator_group.permissions.count()} permissions\n'
                f'Typical_user: {typical_user_group.permissions.count()} permissions'
            )
        )
