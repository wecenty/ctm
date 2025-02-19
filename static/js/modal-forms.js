class ModalFormHandler {
    constructor() {
        this.modal = new bootstrap.Modal(document.getElementById('formModal'));
        this.modalElement = document.getElementById('formModal');
        this.modalTitle = document.querySelector('#formModal .modal-title');
        this.modalBody = document.querySelector('#formModal .modal-body');

        this.setupEventListeners();
        console.log('ModalFormHandler initialized'); // Отладочный вывод
    }

    setupEventListeners() {
        const buttons = document.querySelectorAll('[data-modal-form]');
        console.log('Found modal buttons:', buttons.length); // Отладочный вывод

        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                console.log('Modal button clicked', button.href); // Отладочный вывод
                e.preventDefault();
                this.loadForm(button.href, button.getAttribute('data-modal-title'));
            });
        });
    }

    loadForm(url, title) {
        console.log('Loading form:', url); // Отладочный вывод
        if (!url.endsWith('/')) {
            url += '/';
        }

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.text())
            .then(html => {
                console.log('Form loaded successfully'); // Отладочный вывод
                this.modalTitle.textContent = title;
                this.modalBody.innerHTML = html;

                const form = this.modalBody.querySelector('form');
                if (form && !form.action.endsWith('/')) {
                    form.action += '/';
                }

                // Добавляем обработчик отправки формы
                if (form) {
                    form.addEventListener('submit', (e) => {
                        e.preventDefault();
                        this.submitForm(form);
                    });
                }

                this.modal.show();
            })
            .catch(error => {
                console.error('Error loading form:', error);
                NotificationManager.show('Ошибка загрузки формы', 'error');
            });
    }

    submitForm(form) {
        const formData = new FormData(form);
        const url = form.action;

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
            .then(response => response.text())
            .then(html => {
                // Проверяем, есть ли ошибка с артикулом
                if (html.includes('Инструмент с артикулом') && html.includes('уже создан')) {
                    const errorMessage = html.match(/Инструмент с артикулом \d+ уже создан/)[0];
                    NotificationManager.show(errorMessage, 'error');
                    return;
                }

                if (html.includes('form-error') || html.includes('errorlist')) {
                    this.modalBody.innerHTML = html;
                    this.setupFormListeners();
                } else {
                    this.modal.hide();

                    // Определяем сообщение
                    let message = 'Операция выполнена успешно';
                    if (url.includes('add_tool')) {
                        message = 'Инструмент успешно добавлен в проект';
                    } else if (url.includes('catalog/create')) {
                        message = 'Каталог успешно создан';
                    } else if (url.includes('catalog') && url.includes('edit')) {
                        message = 'Каталог успешно изменен';
                    } else if (url.includes('project/create') || url.includes('project/add')) {
                        message = 'Проект успешно создан';
                    } else if (url.includes('project') && url.includes('edit')) {
                        message = 'Проект успешно изменен';
                    } else if (url.includes('tool') && url.includes('edit')) {
                        message = 'Инструмент успешно изменен';
                    } else if (url.includes('tool/create')) {
                        message = 'Инструмент успешно добавлен';
                    }

                    NotificationManager.show(message);

                    setTimeout(() => {
                        // Обновляем дерево если оно есть
                        if (typeof treeViewInstance !== 'undefined') {
                            this.updateTreeView();
                        }

                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    }, 100);
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                NotificationManager.show('Произошла ошибка при сохранении', 'error');
            });
    }

    updateTreeView() {
        $.ajax({
            url: treeDataUrl,
            success: (data) => {  // Используем стрелочную функцию для сохранения контекста
                try {
                    // Сохраняем текущее состояние дерева
                    const currentState = treeViewInstance.treeview('getExpanded')
                        .map(node => node.nodeId)
                        .filter(id => id !== undefined);

                    // Пересоздаем дерево
                    treeViewInstance.treeview({
                        data: processTreeData(data),
                        levels: 1,
                        onNodeRendered: () => {
                            // Восстанавливаем состояние только после полной отрисовки
                            if (currentState.length > 0) {
                                setTimeout(() => {
                                    currentState.forEach(nodeId => {
                                        try {
                                            treeViewInstance.treeview('expandNode', [nodeId, {silent: true}]);
                                        } catch (e) {
                                            console.warn(`Unable to expand node ${nodeId}`, e);
                                        }
                                    });
                                }, 100);
                            }
                        }
                    });
                } catch (e) {
                    console.error('Error updating tree view:', e);
                    // В случае ошибки просто перезагружаем страницу
                    window.location.reload();
                }
            },
            error: (err) => {
                console.error('Error fetching tree data:', err);
                window.location.reload();
            }
        });
    }

    setupFormListeners() {
        const form = this.modalBody.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitForm(form);
            });
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ModalFormHandler'); // Отладочный вывод
    new ModalFormHandler();
});