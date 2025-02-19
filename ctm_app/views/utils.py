def get_projects_tree(projects):
    """Построение дерева проектов"""
    projects_dict = {project.id: {
        'project': project,
        'children': []
    } for project in projects}

    tree = []

    for project in projects:
        node = projects_dict[project.id]
        if project.parent_id is None:
            tree.append(node)
        else:
            if project.parent_id in projects_dict:
                projects_dict[project.parent_id]['children'].append(node)

    return tree