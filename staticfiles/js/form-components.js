// static/js/form-components.js

class CatalogFormHandler {
    constructor(formElement) {
        this.form = formElement;
        this.nameInput = this.form.querySelector('[name="name"]');
        this.parentSelect = this.form.querySelector('[name="parent"]');
        this.init();
    }

    init() {
        // Живая валидация имени каталога
        this.nameInput.addEventListener('input', this.validateName.bind(this));

        // Улучшенный выбор родительского каталога
        if (this.parentSelect) {
            $(this.parentSelect).select2({
                theme: 'bootstrap-5',
                placeholder: 'Выберите родительский каталог',
                allowClear: true,
                templateResult: this.formatCatalogOption
            });
        }
    }

    validateName() {
        const name = this.nameInput.value.trim();
        const feedback = document.createElement('div');

        if (name.length < 3) {
            feedback.className = 'invalid-feedback d-block';
            feedback.textContent = 'Название должно содержать минимум 3 символа';
            this.nameInput.classList.add('is-invalid');
        } else {
            feedback.className = 'valid-feedback d-block';
            feedback.textContent = 'Отличное название!';
            this.nameInput.classList.remove('is-invalid');
            this.nameInput.classList.add('is-valid');
        }

        const existingFeedback = this.nameInput.nextElementSibling;
        if (existingFeedback) {
            existingFeedback.replaceWith(feedback);
        } else {
            this.nameInput.parentNode.appendChild(feedback);
        }
    }

    formatCatalogOption(catalog) {
        if (!catalog.id) return catalog.text;
        return $(`<span><i class="bi bi-folder me-2"></i>${catalog.text}</span>`);
    }
}

class ToolFormHandler {
    constructor(formElement) {
        this.form = formElement;
        this.init();
    }

    init() {
        this.initNumericInputs();
        this.initResourceCalculator();
        this.addDimensionPreviewer();
    }

    initNumericInputs() {
        this.form.querySelectorAll('input[type="number"]').forEach(input => {
            const wrapper = document.createElement('div');
            wrapper.className = 'numeric-input';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            const unit = document.createElement('span');
            unit.className = 'unit';
            unit.textContent = input.name.includes('diameter') || input.name.includes('length') ? 'мм' : '';
            wrapper.appendChild(unit);

            // Добавляем кнопки +/-
            const controls = document.createElement('div');
            controls.className = 'numeric-controls';
            controls.innerHTML = `
                <button type="button" class="btn btn-sm btn-outline-secondary" data-action="increment">+</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" data-action="decrement">-</button>
            `;
            wrapper.appendChild(controls);

            controls.addEventListener('click', (e) => {
                const button = e.target.closest('button');
                if (!button) return;

                const step = parseFloat(input.step) || 1;
                const value = parseFloat(input.value) || 0;

                if (button.dataset.action === 'increment') {
                    input.value = value + step;
                } else {
                    input.value = value - step;
                }

                input.dispatchEvent(new Event('change'));
            });
        });
    }

    initResourceCalculator() {
        const resourceInput = this.form.querySelector('[name="resource"]');
        if (!resourceInput) return;

        const calculator = document.createElement('div');
        calculator.className = 'resource-calculator mt-2';
        calculator.innerHTML = `
            <small class="text-muted">
                Рекомендуемый ресурс: 
                <span class="recommended-resource">Заполните параметры</span>
            </small>
        `;
        resourceInput.parentNode.appendChild(calculator);

        const updateRecommendation = () => {
            const diameter = parseFloat(this.form.querySelector('[name="diameter"]').value) || 0;
            const length = parseFloat(this.form.querySelector('[name="length"]').value) || 0;

            if (diameter && length) {
                // Простая формула для примера
                const recommended = Math.round((diameter * length) / 10);
                calculator.querySelector('.recommended-resource').textContent =
                    `${recommended} (базовый расчет)`;
            }
        };

        this.form.querySelectorAll('[name="diameter"], [name="length"]')
            .forEach(input => input.addEventListener('change', updateRecommendation));
    }

    addDimensionPreviewer() {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'dimension-preview mt-3';
        previewContainer.innerHTML = `
            <div class="text-center">
                <svg width="200" height="100" class="tool-preview-svg"></svg>
            </div>
        `;
        this.form.appendChild(previewContainer);

        const updatePreview = () => {
            const diameter = parseFloat(this.form.querySelector('[name="diameter"]').value) || 0;
            const length = parseFloat(this.form.querySelector('[name="length"]').value) || 0;

            if (diameter && length) {
                const svg = previewContainer.querySelector('svg');
                // Масштабируем размеры для отображения
                const scale = Math.min(180 / length, 60 / diameter);
                const scaledLength = length * scale;
                const scaledDiameter = diameter * scale;

                svg.innerHTML = `
                    <rect x="${(200 - scaledLength) / 2}" 
                          y="${(100 - scaledDiameter) / 2}"
                          width="${scaledLength}"
                          height="${scaledDiameter}"
                          fill="#e9ecef"
                          stroke="#0d6efd"
                          rx="2"/>
                    <text x="100" y="90" text-anchor="middle" fill="#6c757d" font-size="12">
                        ${length}мм x ⌀${diameter}мм
                    </text>
                `;
            }
        };

        this.form.querySelectorAll('[name="diameter"], [name="length"]')
            .forEach(input => input.addEventListener('change', updatePreview));
    }
}

class ProjectToolFormHandler {
    constructor(formElement) {
        this.form = formElement;
        this.init();
    }

    init() {
        this.initToolSelect();
        this.initApplicationTimeHandler();
        this.initQuantityPreview();
    }

    initToolSelect() {
        const toolSelect = this.form.querySelector('[name="tool"]');
        if (!toolSelect) return;

        $(toolSelect).select2({
            theme: 'bootstrap-5',
            templateResult: this.formatToolOption,
            templateSelection: this.formatToolOption
        }).on('select2:select', (e) => {
            this.updateToolPreview(e.params.data);
        });
    }

    formatToolOption(tool) {
        if (!tool.id) return tool.text;
        return $(`
            <div class="d-flex align-items-center">
                <i class="bi bi-tools me-2"></i>
                <div>
                    <div>${tool.text}</div>
                    <small class="text-muted">
                        Ресурс: ${tool.resource || '?'} | 
                        ⌀${tool.diameter || '?'}мм x ${tool.length || '?'}мм
                    </small>
                </div>
            </div>
        `);
    }

    updateToolPreview(toolData) {
        const previewEl = this.form.querySelector('.tool-preview');
        if (!previewEl) return;

        previewEl.classList.add('active');
        previewEl.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h6>${toolData.text}</h6>
                    <div class="small text-muted">
                        <div>Диаметр: ${toolData.diameter}мм</div>
                        <div>Длина: ${toolData.length}мм</div>
                        <div>Ресурс: ${toolData.resource}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="tool-preview-icon text-center">
                        <i class="bi bi-tools" style="font-size: 2rem;"></i>
                    </div>
                </div>
            </div>
        `;
    }

    initApplicationTimeHandler() {
        const timeInput = this.form.querySelector('[name="application_time"]');
        if (!timeInput) return;

        // Добавляем ползунок
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.className = 'form-range mt-2';
        slider.min = '1';
        slider.max = '3600'; // 1 час
        slider.value = timeInput.value || '60';

        timeInput.parentNode.appendChild(slider);

        // Синхронизируем значения
        slider.addEventListener('input', () => {
            timeInput.value = slider.value;
            this.updateQuantityPreview();
        });

        timeInput.addEventListener('input', () => {
            slider.value = timeInput.value;
            this.updateQuantityPreview();
        });

        // Добавляем метки времени
        const timeMarks = document.createElement('div');
        timeMarks.className = 'time-marks d-flex justify-content-between mt-1';
        timeMarks.innerHTML = `
            <small class="text-muted">1 сек</small>
            <small class="text-muted">30 мин</small>
            <small class="text-muted">1 час</small>
        `;
        timeInput.parentNode.appendChild(timeMarks);
    }

    initQuantityPreview() {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'quantity-preview alert alert-info mt-3';
        this.form.appendChild(previewContainer);

        this.updateQuantityPreview = () => {
            const toolSelect = this.form.querySelector('[name="tool"]');
            const timeInput = this.form.querySelector('[name="application_time"]');
            const projectQuantity = this.form.dataset.projectQuantity || 1;

            if (toolSelect.value && timeInput.value) {
                const tool = $(toolSelect).select2('data')[0];
                const time = parseInt(timeInput.value);
                const quantity = (tool.resource / time) * projectQuantity;

                previewContainer.innerHTML = `
                    <div class="text-center">
                        <h6>Расчетное количество инструментов:</h6>
                        <div class="display-4">${quantity.toFixed(2)}</div>
                        <small class="text-muted">
                            ${tool.resource} / ${time} сек × ${projectQuantity} шт.
                        </small>
                    </div>
                `;
            }
        };

        // Вызываем первичный расчет
        this.updateQuantityPreview();
    }
}

// Инициализация обработчиков форм
document.addEventListener('DOMContentLoaded', () => {
    const formModal = document.getElementById('formModal');
    if (!formModal) return;

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                const form = formModal.querySelector('form');
                if (form) {
                    if (form.classList.contains('catalog-form')) {
                        new CatalogFormHandler(form);
                    } else if (form.classList.contains('tool-form')) {
                        new ToolFormHandler(form);
                    } else if (form.classList.contains('project-tool-form')) {
                        new ProjectToolFormHandler(form);
                    }
                }
            }
        });
    });

    observer.observe(formModal, { childList: true, subtree: true });
});