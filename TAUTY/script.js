// Add interactivity (e.g., cart functionality, animations)
document.addEventListener('DOMContentLoaded', function () {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function () {
            alert('Added to cart!');
            // Add more functionality here
        });
    });
});