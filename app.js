// ==========================================
// app.js (Unified Frontend Logic hooked to api.py)
// ==========================================

const API = 'http://127.0.0.1:5000';
let map = null;
let currentRouteLayer = null;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial Checks & Icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    const username = sessionStorage.getItem('username');
    const path = window.location.pathname;

    // Secure Navigation Logic
    if (!username && !path.includes('index.html') && path !== '/' && path !== '') {
        window.location.href = 'index.html';
        return;
    }

    if (username) {
        const nbUser = document.getElementById('nav-username');
        if (nbUser) nbUser.textContent = username;
    }

    // 2. Page Specific Bootstrapping
    if (document.getElementById('source') && document.getElementById('gwalior-map')) {
        initLeafletMap();
        loadLocations();
    }

    if (document.getElementById('booking-content') && path.includes('booking')) {
        renderTicketDetails();
    }

    if (document.getElementById('routes-table')) {
        loadAdminRoutes();
    }
});

function toggleTheme() {
    const body = document.body;
    body.classList.toggle('light-theme');
    const isLight = body.classList.contains('light-theme');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    
    document.querySelectorAll('.icon-sun').forEach(el => el.style.display = isLight ? 'inline-block' : 'none');
    document.querySelectorAll('.icon-moon').forEach(el => el.style.display = isLight ? 'none' : 'inline-block');
}

// ── AUTHENTICATION ──
let currentRole = 'passenger';
let isSignup = false;

function switchTab(role) {
    currentRole = role;
    isSignup = false; 
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const tabEl = document.getElementById('tab-' + role);
    if(tabEl) tabEl.classList.add('active');
    
    const signupDiv = document.getElementById('signup-toggle-div');
    if(signupDiv) signupDiv.style.display = role === 'admin' ? 'none' : 'block';
    
    updateBtnText();
}

function toggleAuthMode() {
    isSignup = !isSignup;
    const tDesc = document.getElementById('toggle-desc');
    const tLink = document.getElementById('toggle-link');
    if(tDesc) tDesc.textContent = isSignup ? "Already have an account?" : "New user?";
    if(tLink) tLink.textContent = isSignup ? "Login" : "Sign up";
    updateBtnText();
}

function updateBtnText() {
    const btnText = document.getElementById('btn-text');
    if(btnText) btnText.textContent = `${isSignup ? "Sign Up" : "Login"} as ${currentRole === 'admin' ? "Admin" : "Passenger"}`;
}

async function handleLoginSubmit() {
    const uEl = document.getElementById('username');
    const pEl = document.getElementById('password');
    if(!uEl || !pEl) return;
    
    const username = uEl.value.trim();
    const password = pEl.value.trim();

    if (!username || !password) return alert('Please enter credentials.');

    const btn = document.getElementById('login-btn');
    if(btn) btn.disabled = true;

    try {
        const endpoint = isSignup ? "/api/signup" : "/api/login";
        const res  = await fetch(`${API}${endpoint}`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ username, password, role: currentRole })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            sessionStorage.setItem('username', data.username);
            sessionStorage.setItem('role',     data.role);
            window.location.href = data.role === 'admin' ? 'admin.html' : 'selection.html';
        } else {
            alert(data.error || 'Authentication failed.');
        }
    } catch {
        alert('Cannot connect to server. Ensure Flask backend is running.');
    } finally {
        if(btn) btn.disabled = false;
    }
}

function handleLogout() {
    sessionStorage.clear();
    window.location.href = 'index.html';
}

// ── PASSENGER / SELECTION FLOW ──
const LOCATIONS = {
  "Gwalior Railway Station": [26.2163, 78.1772],
  "Bus Stand (ISBT)": [26.2100, 78.1750],
  "City Centre": [26.2000, 78.1650],
  "Lashkar": [26.1950, 78.1500],
  "Jiwaji University": [26.1900, 78.1800],
  "Morar": [26.2200, 78.2200],
  "Gwalior Airport": [26.2900, 78.2300],
  "DD Nagar": [26.2300, 78.1900],
  "Gandhi Nagar": [26.2050, 78.1850],
  "Kampoo Bus Stand": [26.1950, 78.1600],
  "Phool Bagh": [26.2080, 78.1680],
  "Thatipur": [26.2150, 78.2000],
  "DB Mall": [26.2020, 78.1620],
  "Padav": [26.2100, 78.1700],
  "Baija Taal": [26.2050, 78.1650],
  "Jai Vilas Palace": [26.2030, 78.1690],
  "Gwalior Fort": [26.2300, 78.1700],
  "GRMC Gwalior": [26.2010, 78.1600],
  "Jayarogya Hospital (JAH)": [26.2000, 78.1610],
  "Sun Temple": [26.2400, 78.2000],
  "DD Mall": [26.1980, 78.1550],
  "Patel Nagar": [26.1900, 78.1580],
  "Birla Nagar": [26.2350, 78.1750],
  "Keshar Towers": [26.1920, 78.1520],
  "ITM University Gwalior": [26.1000, 78.1700],
  "MITS Gwalior": [26.2120, 78.1820],
  "Cancer Hospital & Research Institute": [26.1950, 78.1400],
  "Tansen Tomb": [26.2250, 78.1720],
  "Govindpuri": [26.2080, 78.1950]
};

function initLeafletMap() {
    map = L.map('gwalior-map').setView([26.2183, 78.1828], 13);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CartoDB',
        maxZoom: 19
    }).addTo(map);
}

function drawRouteOnMap(srcName, dstName) {
    if(!map) return;
    if (currentRouteLayer) {
        map.removeLayer(currentRouteLayer);
    }
    const c1 = LOCATIONS[srcName];
    const c2 = LOCATIONS[dstName];
    if (c1 && c2) {
        const line = [c1, c2];
        currentRouteLayer = L.polyline(line, {
            color: 'var(--brown)',
            weight: 5,
            opacity: 0.8,
            dashArray: '10, 10',
            lineCap: 'round'
        }).addTo(map);

        const bounds = L.latLngBounds([c1, c2]);
        map.fitBounds(bounds, { padding: [50, 50] });

        L.circleMarker(c1, { color: '#059669', radius: 8, fillOpacity: 1 }).addTo(map).bindPopup("Source: " + srcName);
        L.circleMarker(c2, { color: '#dc2626', radius: 8, fillOpacity: 1 }).addTo(map).bindPopup("Destination: " + dstName);
    }
}

async function loadLocations() {
    try {
        const res = await fetch(`${API}/api/locations`);
        const locs = await res.json();
        const srcEl = document.getElementById('source');
        const dstEl = document.getElementById('destination');
        if(!srcEl || !dstEl) return;
        
        let html = '<option value="">-- Select --</option>';
        locs.forEach(loc => html += `<option value="${loc}">${loc}</option>`);
        
        srcEl.innerHTML = html;
        dstEl.innerHTML = html;
        
        // Add listeners directly here so html inline events aren't strictly needed!
        srcEl.addEventListener('change', calculateFare);
        dstEl.addEventListener('change', calculateFare);
    } catch {
        console.error("Locations failed.");
    }
}

function swapStops() {
    const src = document.getElementById('source');
    const dst = document.getElementById('destination');
    if (!src || !dst) return;
    
    const temp = src.value;
    src.value = dst.value;
    dst.value = temp;
    calculateFare();
}

function selectVehicle(cardEl, vType) {
    document.querySelectorAll('.vehicle-card').forEach(c => {
        c.style.border = '1px solid var(--border)';
        c.classList.remove('selected');
    });
    cardEl.style.border = '2px solid var(--brown)';
    cardEl.classList.add('selected');
    
    const vInput = document.getElementById('vehicle_type');
    if(vInput) {
        vInput.value = vType;
        calculateFare();
    }
}

let lastTripData = null;

async function calculateFare() {
    const src = document.getElementById('source')?.value;
    const dest = document.getElementById('destination')?.value;
    const vType = document.getElementById('vehicle_type')?.value;

    if (!src || !dest || !vType) return;
    if (src === dest) {
        alert('Source and destination cannot be the same');
        return;
    }

    const spinner = document.getElementById('calc-spinner-container');
    if(spinner) spinner.innerHTML = '<div class="loader" style="width:20px;height:20px;border-width:2px;margin-right:8px;"></div> Calculating...';

    try {
        const res = await fetch(`${API}/api/calculateFare?source=${encodeURIComponent(src)}&destination=${encodeURIComponent(dest)}&vehicle_type=${encodeURIComponent(vType)}`);
        const data = await res.json();

        if (res.ok) {
            document.getElementById('res-fare').textContent = data.fare;
            document.getElementById('res-distance').textContent = data.distance + ' km';
            document.getElementById('res-time').textContent = Math.round(data.distance * 2.5) + ' mins';
            
            lastTripData = {
                source: src,
                destination: dest,
                fare: data.fare,
                distance: data.distance,
                vehicle_type: vType,
                route: data.route
            };

            const card = document.getElementById('result-card');
            if(card) {
                card.style.display = 'block';
                card.classList.add('show');
            }

            drawRouteOnMap(src, dest);
            lucide.createIcons();
        } else {
            alert(data.error);
        }
    } catch {
        alert('Calculation failed.');
    } finally {
        if(spinner) spinner.innerHTML = '';
    }
}

// ── BOOKING MODAL & FLOW ──
function nextBookingStep(stepId) {
    document.querySelectorAll('.booking-step').forEach(s => {
        s.style.display = 'none';
        s.classList.remove('active');
    });
    const t = document.getElementById(stepId);
    if(t) {
        t.style.display = 'block';
        t.classList.add('active');
    }
}

async function startBookingFlow() {
    const btn = document.getElementById('book-btn');
    if (!lastTripData) return;

    if(btn) {
        btn.disabled = true;
        btn.innerHTML = '⌛ Booking...';
    }

    const modal = document.getElementById('booking-modal');
    if(modal) {
        modal.classList.add('active');
        modal.style.display = 'flex';
    }
    nextBookingStep('step-search');

    try {
        const res = await fetch(`${API}/api/book`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lastTripData)
        });
        const data = await res.json();

        if (data.success) {
            sessionStorage.setItem('booking_data', JSON.stringify(data));
            
            const driverName = document.getElementById('modal-driver-name');
            const driverVeh = document.getElementById('modal-driver-vehicle');
            if(driverName) driverName.textContent = data.driver_name;
            if(driverVeh) driverVeh.textContent = data.vehicle_no;
            
            const otpC = document.getElementById('modal-otp-container');
            if(otpC) {
                otpC.innerHTML = data.otp.split('').map(num => 
                    `<input type="text" value="${num}" readonly style="width:48px; height:56px; text-align:center; font-size:24px; font-weight:700; border:1px solid var(--border); border-radius:8px; background:var(--bg-dark); box-shadow:inset 0 2px 4px rgba(0,0,0,0.05); color:var(--text-primary);">`
                ).join('');
            }

            setTimeout(() => {
                nextBookingStep('step-found');
            }, 2000);

        } else {
            if(modal) { modal.style.display = 'none'; modal.classList.remove('active'); }
            alert('Booking failed: ' + (data.error || 'Unknown error'));
        }
    } catch {
        if(modal) { modal.style.display = 'none'; modal.classList.remove('active'); }
        alert('Could not connect to the server.');
    } finally {
        if(btn) {
            btn.disabled = false;
            btn.innerHTML = '⚡ Book Now';
        }
    }
}

function proceedToBooking() {
    window.location.href = 'booking.html';
}

function renderTicketDetails() {
    const dataStr = sessionStorage.getItem('booking_data');
    if (!dataStr) {
        window.location.href = 'selection.html';
        return;
    }

    const data = JSON.parse(dataStr);
    const trip = data.trip_details;

    if(document.getElementById('booking-otp')) document.getElementById('booking-otp').textContent = data.otp;
    if(document.getElementById('driver-name')) document.getElementById('driver-name').textContent = data.driver_name;
    if(document.getElementById('vehicle-no')) document.getElementById('vehicle-no').textContent = data.vehicle_no;
    if(document.getElementById('booking-id')) document.getElementById('booking-id').textContent = data.booking_id;
    
    if(trip) {
        if(document.getElementById('trip-source')) document.getElementById('trip-source').textContent = trip.source;
        if(document.getElementById('trip-destination')) document.getElementById('trip-destination').textContent = trip.destination;
        if(document.getElementById('trip-distance')) document.getElementById('trip-distance').textContent = trip.distance + ' km';
        if(document.getElementById('trip-fare')) document.getElementById('trip-fare').textContent = trip.fare;
        if(document.getElementById('trip-vehicle')) document.getElementById('trip-vehicle').textContent = trip.vehicle_type;
    }
    
    if(document.getElementById('booking-content')) document.getElementById('booking-content').style.display = 'block';
}

// ── ADMIN ROUTES ──
async function loadAdminRoutes() {
    try {
        const res = await fetch(`${API}/api/routes/withFares`);
        const routes = await res.json();
        const tbody = document.getElementById('routes-tbody');
        if(!tbody) return;

        tbody.innerHTML = '';
        routes.forEach((r, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="badge badge-green">${idx + 1}</span></td>
                <td style="font-weight: 500;">${r.source}</td>
                <td style="font-weight: 500;">${r.destination}</td>
                <td><i data-lucide="map" style="width:14px; margin-right:4px;"></i> ${r.distance} km</td>
                <td><span style="font-weight:700; color:var(--text-primary);">₹ ${r.fare}</span></td>
                <td>
                    <div class="actions-cell">
                        <button class="btn btn-danger btn-sm" onclick="deleteRoute(${r.id})" title="Delete Route" style="padding:6px 12px; font-size:12px;">Delete</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        lucide.createIcons();
    } catch {
        console.error("Admin route load failed.");
    }
}

async function handleAddRoute(e) {
    if(e) e.preventDefault();
    const btn = document.getElementById('add-route-btn');
    if(btn) btn.disabled = true;

    const data = {
        source: document.getElementById('new-source').value,
        destination: document.getElementById('new-destination').value,
        distance: parseFloat(document.getElementById('new-distance').value),
        fare: parseFloat(document.getElementById('new-fare').value)
    };

    try {
        const res = await fetch(`${API}/api/routes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
            document.getElementById('add-route-form').reset();
            loadAdminRoutes();
        } else {
            alert('Error: ' + result.error);
        }
    } catch {
        alert('Server unreachable');
    } finally {
        if(btn) btn.disabled = false;
    }
}

async function deleteRoute(id) {
    if (!confirm('Are you sure you want to delete this route?')) return;
    try {
        const res = await fetch(`${API}/api/routes/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadAdminRoutes();
        } else {
            alert('Delete failed');
        }
    } catch {
        alert('Server unreachable');
    }
}
