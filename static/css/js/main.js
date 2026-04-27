function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

async function loadProductsFromAPI() {
    const container = document.getElementById('products-container');
    const spinner = document.getElementById('loading-spinner');
    
    if (!container) return;
    
    try {
        spinner?.classList.remove('d-none');
        
        const response = await fetch('/api/products/');
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки товаров');
        }
        
        const products = await response.json();
        renderProducts(products);
        
    } catch (error) {
        showAlert('Ошибка при загрузке товаров. Попробуйте позже.', 'danger');
    } finally {
        spinner?.classList.add('d-none');
    }
}

function renderProducts(products) {
    const container = document.getElementById('products-container');
    if (!container) return;
    
    if (products.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Товары не найдены</div>';
        return;
    }
    
    let html = '<div class="row">';
    
    products.results.forEach(product => {
        html += `
            <div class="col-sm-6 col-md-4 col-lg-4 mb-4">
                <div class="card h-100">
                    <img src="${product.image || '/static/images/placeholder.png'}" 
                         class="card-img-top" alt="${product.name}">
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text text-muted">${product.manufacturer_name}</p>
                        <p class="card-text fw-bold text-primary mt-auto">${product.price} руб.</p>
                        <a href="/product/${product.id}/" class="btn btn-outline-primary">Подробнее</a>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

async function addToCart(productId, productName) {
    const button = document.getElementById(`add-to-cart-${productId}`);
    
    try {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Добавление...';
        
        const response = await fetch('/api/cart-items/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                cart: 1,  
                product: productId,
                quantity: 1
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка добавления в корзину');
        }
        
        showToast(`Товар "${productName}" добавлен в корзину`, 'success');
        updateCartCount();
        
    } catch (error) {
        showToast(error.message, 'danger');
    } finally {
        button.disabled = false;
        button.innerHTML = 'Добавить в корзину';
    }
}

async function updateCartCount() {
    try {
        const response = await fetch('/api/carts/');
        const carts = await response.json();
        
        const countElement = document.getElementById('cart-count');
        if (countElement && carts.results && carts.results[0]) {
            countElement.textContent = carts.results[0].items_count || 0;
        }
    } catch (error) {
        console.error('Ошибка обновления счетчика корзины:', error);
    }
}

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    
    const toastHTML = `
        <div class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function showAlert(message, type = 'danger') {
    const container = document.getElementById('products-container');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    
    if (document.getElementById('dynamic-catalog')) {
        loadProductsFromAPI();
    }
});