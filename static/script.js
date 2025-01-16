// Function to toggle the categories list visibility
document.getElementById('categories-toggle').addEventListener('click', function() {
    const categoryList = document.getElementById('category-list');
    const arrow = document.querySelector('.arrow');
    
    // Toggle the visibility of the categories list
    categoryList.classList.toggle('show');
    
    // Rotate the arrow icon when the categories are shown or hidden
    if (categoryList.classList.contains('show')) {
        arrow.style.transform = 'rotate(180deg)';
    } else {
        arrow.style.transform = 'rotate(0deg)';
    }
});

// Function to filter products based on search input
document.getElementById('search-bar').addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const products = document.querySelectorAll('.product-card');
    
    products.forEach(product => {
        const productName = product.querySelector('h3').textContent.toLowerCase();
        if (productName.includes(query)) {
            product.style.display = 'block'; // Show the product if it matches
        } else {
            product.style.display = 'none'; // Hide the product if it doesn't match
        }
    });
});

// Optional: Add category filtering functionality
document.querySelectorAll('.category-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        const category = e.target.textContent.toLowerCase();
        const products = document.querySelectorAll('.product-card');
        
        products.forEach(product => {
            const productName = product.querySelector('h3').textContent.toLowerCase();
            // Example: Filter products by category (adjust as needed)
            if (category === 'all products' || productName.includes(category)) {
                product.style.display = 'block';
            } else {
                product.style.display = 'none';
            }
        });
    });
});


