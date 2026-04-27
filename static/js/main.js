// ==================== MOBILE MENU ==================== 
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.navbar-menu');

    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking on a nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.navbar-container')) {
                navMenu.classList.remove('active');
            }
        });
    }
});

// ==================== SMOOTH SCROLL ==================== 
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== SEARCH FUNCTIONALITY ==================== 
const searchInputs = document.querySelectorAll('.search-input, .search-input-large');
searchInputs.forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            this.closest('form').submit();
        }
    });

    // Add debounce for search suggestions (optional)
    input.addEventListener('input', function(e) {
        const query = e.target.value;
        if (query.length > 0) {
            // Could add real-time search suggestions here
        }
    });
});

// ==================== LAZY LOADING ==================== 
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.src || img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ==================== CARD ANIMATIONS ==================== 
const cards = document.querySelectorAll('.anime-card, .manga-card, .stat-card, .list-item');
const cardObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            cardObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1
});

cards.forEach(card => cardObserver.observe(card));

// Add keyframe animation
if (!document.querySelector('#animations-style')) {
    const style = document.createElement('style');
    style.id = 'animations-style';
    style.innerHTML = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// ==================== NOTIFICATION SYSTEM ==================== 
function showNotification(message, type = 'success', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ==================== FORM VALIDATION ==================== 
const forms = document.querySelectorAll('.auth-form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = this.querySelectorAll('input[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });

        if (!isValid) {
            e.preventDefault();
            showNotification('Please fill in all required fields', 'error');
        }
    });

    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.remove('error');
        });
    });
});

// ==================== PASSWORD STRENGTH ==================== 
const passwordInputs = document.querySelectorAll('input[type="password"]');
passwordInputs.forEach(input => {
    input.addEventListener('input', function() {
        const password = this.value;
        let strength = 0;

        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[!@#$%^&*]/.test(password)) strength++;

        // Could add visual indicator here
    });
});

// ==================== FILTER FUNCTIONALITY ==================== 
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const allBtns = this.parentElement.querySelectorAll('.filter-btn');
        allBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        const filter = this.getAttribute('data-filter');
        const items = document.querySelectorAll('.list-item');

        items.forEach(item => {
            if (filter === 'all' || item.getAttribute('data-status') === filter) {
                item.style.display = 'block';
                setTimeout(() => item.style.opacity = '1', 10);
            } else {
                item.style.opacity = '0';
                setTimeout(() => item.style.display = 'none', 300);
            }
        });
    });
});

// ==================== COUNTDOWN TIMER ==================== 
function startCountdown(elementSelector, seconds) {
    const element = document.querySelector(elementSelector);
    if (!element) return;

    let remaining = seconds;
    const interval = setInterval(() => {
        remaining--;
        element.textContent = `${remaining}s`;

        if (remaining <= 0) {
            clearInterval(interval);
            element.remove();
        }
    }, 1000);
}

// ==================== RESPONSIVE IMAGES ==================== 
function setResponsiveImages() {
    const images = document.querySelectorAll('img[data-src]');
    images.forEach(img => {
        if (!img.src) {
            img.src = img.dataset.src;
        }
    });
}

// ==================== KEYBOARD SHORTCUTS ==================== 
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input, .search-input-large');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close modals (if any)
    if (e.key === 'Escape') {
        const navMenu = document.querySelector('.navbar-menu');
        if (navMenu) {
            navMenu.classList.remove('active');
        }
    }
});

// ==================== INTERSECTION OBSERVER FOR ANIMATIONS ==================== 
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.content-section, .detail-section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    sectionObserver.observe(section);
});

// ==================== PERFORMANCE OPTIMIZATION ==================== 
// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Optimize scroll events
window.addEventListener('scroll', throttle(() => {
    // Add scroll effects here if needed
}, 100));

// ==================== DYNAMIC CONTENT LOADING ==================== 
async function loadMoreContent(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading content:', error);
        showNotification('Error loading content', 'error');
    }
}

// ==================== INITIALIZE ON PAGE LOAD ==================== 
document.addEventListener('DOMContentLoaded', function() {
    setResponsiveImages();
    console.log('AnimeHub loaded successfully!');
});

// ==================== ERROR HANDLING ==================== 
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // Could send error logs to server
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});

// ==================== ACCESSIBILITY ==================== 
// Add focus visible styles
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-nav');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-nav');
});
