import os
import re

# REBUILD selection.html
try:
    with open('selection.html', 'r', encoding='utf-8') as f:
        sel_html = f.read()
    
    # 1. ADD LEAFLET IN HEAD
    if 'leaflet' not in sel_html:
        sel_html = sel_html.replace('</head>', '  <!-- Leaflet -->\n  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n</head>')

    # 2. ADD APP.JS AT BOTTOM
    if '<script src="app.js"></script>' not in sel_html:
        sel_html = sel_html.replace('</body>', '<script src="app.js"></script>\n</body>')
    
    # 3. FIX iframe map to div map
    if '<iframe' in sel_html:
        sel_html = re.sub(r'<div class="map-placeholder"[^>]*>.*?</div>\s*<!-- Right Controls Column', 
        '<div class="map-placeholder" style="padding:0; overflow:hidden;" id="gwalior-map"></div>\n        <!-- Right Controls Column', 
        sel_html, flags=re.DOTALL)
        
    # 4. Fix dropdown to vehicle cars
    if '<select id="vehicle_type"' in sel_html:
        cards_html = """
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div class="vehicle-card selected" onclick="selectVehicle(this, 'City Bus')" style="padding:16px; border:2px solid var(--brown); border-radius:12px; cursor:pointer; text-align:center; background:var(--bg-glass);">
                    <div style="font-size:24px;">🚌</div><h4 style="margin:8px 0 0; font-size:14px;">City Bus</h4>
                </div>
                <div class="vehicle-card" onclick="selectVehicle(this, 'AC Bus')" style="padding:16px; border:1px solid var(--border); border-radius:12px; cursor:pointer; text-align:center; background:var(--bg-glass);">
                    <div style="font-size:24px;">❄️🚌</div><h4 style="margin:8px 0 0; font-size:14px;">AC Bus</h4>
                </div>
            </div>
            <input type="hidden" id="vehicle_type" value="City Bus">
"""
        sel_html = re.sub(r'<div class="input-icon-wrap with-icon">\s*<span class="icon">🎟️</span>\s*<select id="vehicle_type".*?</select>\s*</div>', cards_html, sel_html, flags=re.DOTALL)

    # 5. Fix Modal
    modal_html = """  <div class="modal-overlay" id="booking-modal" style="display:none; justify-content:center; align-items:center;">
    <div class="modal-content card" style="max-width:380px; width:100%; text-align:center;">
      <div class="booking-step active" id="step-search">
        <div class="loader" style="margin: 0 auto;"></div>
        <h3 style="font-size:20px; font-weight:700; margin-top:24px;">Finding your driver...</h3>
      </div>
      <div class="booking-step" id="step-found" style="display:none;">
        <div style="font-size:40px; color:var(--brown);">✓</div>
        <h3 style="font-size:20px; font-weight:700;">Driver Found!</h3>
        <div style="margin:16px 0; padding:16px; background:var(--bg-glass); border-radius:8px; text-align:left;">
           <div style="font-size:16px; font-weight:700; color:var(--text-primary);" id="modal-driver-name">Driver Name</div>
           <div style="font-size:14px; margin-top:4px; color:var(--text-secondary);">Vehicle: <span id="modal-driver-vehicle" style="color:var(--text-primary); font-weight:500;"></span></div>
        </div>
        <button class="btn btn-primary" onclick="proceedToBooking()" style="width: 100%;">View Details</button>
      </div>
    </div>
  </div>"""
  
    if 'id="booking-modal"' in sel_html:
        sel_html = re.sub(r'<div class="modal-overlay" id="booking-modal">.*?</div>\s*</div>', modal_html, sel_html, flags=re.DOTALL)

    with open('selection.html', 'w', encoding='utf-8') as f: f.write(sel_html)
except Exception as e:
    print("sel error", e)

# REBUILD index.html AND booking.html
for f_name in ['index.html', 'booking.html']:
    try:
        with open(f_name, 'r', encoding='utf-8') as f: h = f.read()
        if '<script src="app.js"></script>' not in h:
            h = h.replace('</body>', '<script src="app.js"></script>\n</body>')
        with open(f_name, 'w', encoding='utf-8') as f: f.write(h)
    except: pass

# REBUILD admin.html
try:
    with open('admin.html', 'r', encoding='utf-8') as f: adm = f.read()
    if '<script src="app.js"></script>' not in adm:
        adm = adm.replace('</body>', '<script src="app.js"></script>\n</body>')
    # Add back the inline admin scripts that were stripped
    admin_scripts = """<script>
function showTab(id) {
    document.querySelectorAll('.tab-panel').forEach(p=>p.style.display='none');
    document.getElementById(id).style.display='block';
    document.querySelectorAll('.admin-tab-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById(id.replace('tab-', 'btn-')).classList.add('active');
}
function filterTable() {
    const q = document.getElementById('route-search').value.toLowerCase();
    document.querySelectorAll('#routes-tbody tr').forEach(tr => {
        if(tr.innerText.toLowerCase().includes(q)) tr.style.display='';
        else tr.style.display='none';
    });
}
async function updateFare() {
   const r = document.getElementById('upd-route').value;
   const f = document.getElementById('upd-fare').value;
   if(!r||!f) return alert('Select route and entering fare');
   try {
      const res = await fetch(`${API}/api/updateFare/${r}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({new_fare: f})});
      if(res.ok) alert('Success');
      loadAdminRoutes();
   } catch(e){ alert(e); }
}
async function addRoute() {
   const s = document.getElementById('add-source').value;
   const d = document.getElementById('add-dest').value;
   const di = document.getElementById('add-distance').value;
   const fa = document.getElementById('add-fare').value;
   if(!s||!d||!di||!fa) return alert('Fill all');
   try {
      const res = await fetch(`${API}/api/routes`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({source:s, destination:d, distance:di, fare:fa})});
      if(res.ok) { alert('Success'); loadAdminRoutes(); }
   } catch(e){ alert(e); }
}
</script>
</body>"""
    if 'showTab(' not in adm and 'function showTab' not in adm:
         adm = adm.replace('</body>', admin_scripts)
    with open('admin.html', 'w', encoding='utf-8') as f: f.write(adm)
except: pass

print("Dom repaired!")
