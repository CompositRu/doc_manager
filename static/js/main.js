document.addEventListener('DOMContentLoaded', function() {
    // Переключение вложенных документов
    document.querySelectorAll('.toggle-icon').forEach(icon => {
        icon.addEventListener('click', function() {
            const nestedList = this.closest('.document-node').querySelector('.nested-list');
            nestedList.classList.toggle('d-none');
            this.classList.toggle('rotated');
        });
    });
    
    // Обработка кнопок подсказок
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            const value = this.dataset.value;
            const activeTab = document.querySelector('.nav-link.active').getAttribute('href');
            
            if (activeTab === '#add-document') {
                document.querySelector(`form[name="add_document"] input[name="${type}"]`).value = value;
            } else if (activeTab === '#filters') {
                document.querySelector(`#filterForm input[name="${type}"]`).value = value;
                document.getElementById('filterForm').submit();
            }
        });
    });
    
    // Обработка модальных окон
    const commentModal = document.getElementById('commentModal');
    if (commentModal) {
        commentModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const docId = button.dataset.docId;
            document.getElementById('commentDocId').value = docId;
        });
    }
    
    const editModal = document.getElementById('editModal');
    if (editModal) {
        editModal.addEventListener('show.bs.modal', async function (event) {
            const button = event.relatedTarget;
            const docId = button.dataset.docId;
            document.getElementById('editDocId').value = docId;
            
            // Загрузка данных документа для редактирования
            const response = await fetch(`/api/document/${docId}`);
            const data = await response.json();
            
            document.querySelector('#editForm [name="organization"]').value = data.organization;
            document.querySelector('#editForm [name="department"]').value = data.department || '';
            document.querySelector('#editForm [name="surname"]').value = data.surname || '';
            document.querySelector('#editForm [name="date"]').value = data.date;
            document.querySelector('#editForm [name="doc_type"]').value = data.doc_type;
            document.querySelector('#editForm [name="status"]').value = data.status;
        });
    }
    
    // Удаление документа
    window.deleteDocument = function(docId) {
        if (confirm('Вы уверены, что хотите переместить документ в корзину?')) {
            fetch(`/delete/${docId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                }
            })
            .then(response => {
                if (response.ok) location.reload();
                else alert('Ошибка при удалении документа');
            });
        }
    };
    
    // Всплывающие уведомления
    window.showToast = function(message) {
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-bg-primary border-0 show';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        setTimeout(() => {
            bsToast.hide();
            toast.addEventListener('hidden.bs.toast', () => toast.remove());
        }, 3000);
    };
});

// TODO: Добавить в будущем:
// 1. Валидацию форм на клиенте
// 2. Автосохранение черновиков
// 3. Drag-and-drop для загрузки файлов
// 4. Горячие клавиши для навигации
// 5. Поиск с автодополнением