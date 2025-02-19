class DeleteHandler {
    constructor() {
        this.modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        this.modalElement = document.getElementById('deleteConfirmModal');
        this.messageElement = document.getElementById('deleteConfirmMessage');
        this.confirmButton = document.getElementById('confirmDeleteBtn');
        this.currentForm = null;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Обработка всех форм удаления
        document.querySelectorAll('form[data-delete-form]').forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.showConfirmation(form);
            });
        });

        // Обработка кнопки подтверждения
        this.confirmButton.addEventListener('click', () => {
            this.handleDelete();
        });
    }

    showConfirmation(form) {
        this.currentForm = form;
        const entityType = form.dataset.entityType;
        const entityName = form.dataset.entityName;

        this.messageElement.textContent = `Вы уверены, что хотите удалить ${entityType} "${entityName}"?`;
        this.modal.show();
    }

    handleDelete() {
    if (!this.currentForm) return;

    const formData = new FormData(this.currentForm);
    const entityType = this.currentForm.dataset.entityType;
    const entityName = this.currentForm.dataset.entityName;

    fetch(this.currentForm.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            this.modal.hide();
            // Делаем первую букву заглавной
            const capitalizedType = entityType.charAt(0).toUpperCase() + entityType.slice(1);
            NotificationManager.show(`${capitalizedType} "${entityName}" успешно удален`);

                // Обновляем дерево если оно есть
                if (typeof treeViewInstance !== 'undefined') {
                    fetch(treeDataUrl)
                        .then(response => response.json())
                        .then(data => {
                            treeViewInstance.treeview('remove');
                            treeViewInstance.treeview({
                                data: processTreeData(data),
                                levels: 1,
                            });
                        });
                }

                // Перенаправляем или обновляем страницу через задержку
                setTimeout(() => {
                    if (this.currentForm.dataset.redirectUrl) {
                        window.location.href = this.currentForm.dataset.redirectUrl;
                    } else {
                        window.location.reload();
                    }
                }, 1000);
            }
        })
        .catch(() => {
            this.modal.hide();
            NotificationManager.show('Произошла ошибка при удалении', 'error');
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new DeleteHandler();
});