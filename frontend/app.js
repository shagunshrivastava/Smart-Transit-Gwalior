// SPA Routing Logic
function navigate(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show target page
    const targetPage = document.getElementById('page-' + pageId);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`.nav-link[onclick="navigate('${pageId}')"]`);
    if (activeLink) activeLink.classList.add('active');

    // Special logic when entering dashboard
    if (pageId === 'dashboard') {
        document.getElementById('main-nav').style.display = 'block';
    } else if (pageId === 'landing') {
        document.getElementById('main-nav').style.display = 'none';
    }
}

// Authentication Logic
function toggleAuth(type) {
    document.querySelectorAll('.form-view').forEach(f => f.classList.remove('active'));
    document.getElementById(type + '-form').classList.add('active');
}

function handleLoginSubmit() {
    // Mock login success
    navigate('dashboard');
}

function handleLogout() {
    document.getElementById('profile-dropdown').classList.remove('show');
    navigate('landing');
}

// Profile Dropdown
function toggleProfileMenu() {
    document.getElementById('profile-dropdown').classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const isClickInside = document.querySelector('.profile-menu').contains(event.target);
    if (!isClickInside) {
        document.getElementById('profile-dropdown').classList.remove('show');
    }
});

// Dashboard Logic
let selectedVehicleData = null;

function calculateMockDistance() {
    const src = document.getElementById('source-select').value;
    const dst = document.getElementById('dest-select').value;
    if (src && dst && src !== dst) {
        document.getElementById('distance-info').style.display = 'block';
    } else {
        document.getElementById('distance-info').style.display = 'none';
    }
}

document.getElementById('source-select').addEventListener('change', calculateMockDistance);
document.getElementById('dest-select').addEventListener('change', calculateMockDistance);

function selectVehicle(cardElement, type) {
    document.querySelectorAll('.vehicle-card').forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');
    
    const name = cardElement.querySelector('h4').innerText;
    const price = cardElement.querySelector('.v-price').innerText;
    let iconName = 'car';
    if(type.includes('bus')) iconName = type === 'bus-ac' ? 'bus' : 'bus-front';
    if(type === 'erickshaw') iconName = 'zap';

    selectedVehicleData = { name, price, iconName, type };
}

function goToRideDetails() {
    const src = document.getElementById('source-select').value;
    const dst = document.getElementById('dest-select').value;

    if (!src || !dst) {
        alert("Please select a Source and Destination.");
        return;
    }
    if (src === dst) {
        alert("Source and Destination cannot be the same.");
        return;
    }
    if (!selectedVehicleData) {
        alert("Please select a vehicle type.");
        return;
    }

    // Update details page before navigating
    document.getElementById('detail-vehicle-name').innerText = selectedVehicleData.name;
    
    // Update Lucide icon on the detail page
    const detailIconContainer = document.getElementById('detail-icon');
    // Lucide replaces the i tag with an SVG, so we need to recreate the i tag to update it if it was already rendered
    const parent = detailIconContainer.parentNode;
    parent.removeChild(detailIconContainer);
    
    const newIcon = document.createElement('i');
    newIcon.id = 'detail-icon';
    newIcon.setAttribute('data-lucide', selectedVehicleData.iconName);
    newIcon.style.color = "var(--primary)";
    parent.insertBefore(newIcon, parent.firstChild);
    lucide.createIcons();

    navigate('ridedetails');
}

// Booking Flow Logic
let bookingTimeout1, bookingTimeout2;

function startBookingFlow() {
    const modal = document.getElementById('booking-modal');
    modal.classList.add('active');
    
    // Reset steps
    document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));
    document.getElementById('step-search').classList.add('active');

    // Simulate search delay
    bookingTimeout1 = setTimeout(() => {
        nextBookingStep('step-found');
    }, 3000);
}

function nextBookingStep(stepId) {
    document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));
    document.getElementById(stepId).classList.add('active');
    // Ensure Lucide icons render in new active steps
    lucide.createIcons();
}

function closeBookingModal() {
    document.getElementById('booking-modal').classList.remove('active');
    clearTimeout(bookingTimeout1);
    clearTimeout(bookingTimeout2);
    // After booking, go to history
    navigate('history');
}
