document.addEventListener('DOMContentLoaded', function() {
    // POS System functionality
    if (document.querySelector('.pos-container')) {
        initPOSSystem();
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#e74c3c';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

function initPOSSystem() {
    const quantityInputs = document.querySelectorAll('.quantity-control input');
    const orderItems = document.getElementById('order-items');
    const totalAmount = document.getElementById('total-amount');
    const checkoutForm = document.getElementById('checkout-form');
    
    let cart = {};
    
    // Initialize cart
    quantityInputs.forEach(input => {
        const productId = input.name.split('_')[1];
        cart[productId] = 0;
        
        input.addEventListener('change', function() {
            updateCart(productId, parseInt(this.value) || 0);
            updateOrderSummary();
        });
    });
    
    function updateCart(productId, quantity) {
        cart[productId] = quantity;
    }
    
    function updateOrderSummary() {
        // Clear previous items
        orderItems.innerHTML = '';
        let total = 0;
        
        // Add items to summary
        for (const productId in cart) {
            if (cart[productId] > 0) {
                const productElement = document.querySelector(`.product-card input[name="product_${productId}"]`).closest('.product-card');
                const productName = productElement.querySelector('h4').textContent;
                const productPrice = parseFloat(productElement.querySelector('.price').textContent.replace('$', ''));
                const itemTotal = productPrice * cart[productId];
                
                total += itemTotal;
                
                const itemElement = document.createElement('div');
                itemElement.className = 'order-item';
                itemElement.innerHTML = `
                    <div>${productName} x ${cart[productId]}</div>
                    <div>$${itemTotal.toFixed(2)}</div>
                `;
                
                orderItems.appendChild(itemElement);
            }
        }
        
        // Update total
        totalAmount.textContent = total.toFixed(2);
        
        // Add hidden fields for products in cart
        document.querySelectorAll('input[type="hidden"][name^="product_"]').forEach(input => {
            input.remove();
        });
        
        for (const productId in cart) {
            if (cart[productId] > 0) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = `product_${productId}`;
                hiddenInput.value = cart[productId];
                checkoutForm.appendChild(hiddenInput);
            }
        }
    }
    
    // Initial update
    updateOrderSummary();
}
