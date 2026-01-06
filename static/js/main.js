// BOOPING App - Main JavaScript
// Created by Claude Opus 4.5

// Utility functions

function formatNumber(num) {
    return num.toLocaleString();
}

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 3000);
    });
});
