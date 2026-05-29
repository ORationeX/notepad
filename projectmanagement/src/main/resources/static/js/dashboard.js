document.addEventListener('DOMContentLoaded', () => {
    // Dom elements
    const navUserEmailEl = document.getElementById('navUserEmail');
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    
    // Page-specific elements (if they exist in index.html)
    const userEmailEl = document.getElementById('userEmail');
    const userRoleEl = document.getElementById('userRole');
    const infoEmailEl = document.getElementById('infoEmail');
    const infoExpiryEl = document.getElementById('infoExpiry');

    // Show Toast Notification helper
    function showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' 
            ? '<i class="fa-solid fa-circle-check"></i>' 
            : '<i class="fa-solid fa-triangle-exclamation"></i>';
        
        toast.innerHTML = `
            ${icon}
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    // Get cookie by name
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Delete cookie
    function deleteCookie(name) {
        document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict`;
    }

    // Decode JWT and set auth states
    const token = getCookie('token');
    if (token) {
        try {
            const payloadBase64 = token.split('.')[1];
            const decodedPayload = JSON.parse(atob(payloadBase64.replace(/-/g, '+').replace(/_/g, '/')));
            
            const email = decodedPayload.sub;
            const role = decodedPayload.auth || 'USER';
            
            // Set navbar email
            if (navUserEmailEl) {
                navUserEmailEl.textContent = email;
            }
            
            // Set index.html specific elements
            if (userEmailEl) userEmailEl.textContent = email;
            if (infoEmailEl) infoEmailEl.textContent = email;
            if (userRoleEl) userRoleEl.textContent = role;

            if (infoExpiryEl) {
                if (decodedPayload.exp) {
                    const expiryDate = new Date(decodedPayload.exp * 1000);
                    infoExpiryEl.textContent = expiryDate.toLocaleTimeString();
                } else {
                    infoExpiryEl.textContent = '알 수 없음';
                }
            }
        } catch (e) {
            console.error('Failed to decode token:', e);
            showToast('토큰 정보가 올바르지 않습니다.', 'error');
        }
    } else {
        if (userEmailEl) userEmailEl.textContent = 'Guest';
        showToast('로그인이 되어있지 않습니다. 로그인 페이지로 이동합니다.', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
    }

    // Handle Mobile Menu Toggle
    if (mobileMenuToggle && navMenu) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('open');
            const icon = mobileMenuToggle.querySelector('i');
            if (icon) {
                if (navMenu.classList.contains('open')) {
                    icon.className = 'fa-solid fa-xmark';
                } else {
                    icon.className = 'fa-solid fa-bars';
                }
            }
        });
    }

    // Handle Logout (delegated or direct)
    const handleLogout = () => {
        deleteCookie('token');
        showToast('성공적으로 로그아웃되었습니다. 로그인 페이지로 이동합니다.', 'success');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1200);
    };

    document.addEventListener('click', (e) => {
        if (e.target.closest('.btn-logout-nav') || e.target.closest('#btnLogout')) {
            e.preventDefault();
            handleLogout();
        }
    });
});
