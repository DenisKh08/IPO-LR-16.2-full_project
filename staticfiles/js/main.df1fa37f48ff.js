function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

async function addToCart(productId, productName) {
    const button = document.getElementById(`add-to-cart-${productId}`);
    
    try {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Добавление...';
        
        let response = await fetch('/cart/add/' + productId + '/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        });
        
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        
        if (!response.ok) {
            throw new Error('Ошибка добавления');
        }
        
        showToast('Товар "' + productName + '" добавлен в корзину', 'success');
        updateCartCount();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showToast('Ошибка добавления в корзину', 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-cart-plus"></i> Добавить в корзину';
    }
}

function updateCartCount() {
    // Django не даёт легко получить количество через API без авторизации
    // Можно оставить заглушку
    let countElement = document.getElementById('cart-count');
    if (countElement) {
        countElement.textContent = '';
    }
}

function showToast(message, type = 'success') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    let bgClass = type === 'success' ? 'bg-success' : 'bg-danger';
    
    let toastHTML = `
        <div class="toast align-items-center text-white ${bgClass} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    let toastElement = toastContainer.lastElementChild;
    let toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
});