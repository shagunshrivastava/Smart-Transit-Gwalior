import re

# Update index.html
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. Replace the wrapper
    pattern1 = r'<div class="page-center".*?<div class="login-card card"[^\>]*>'
    replacement1 = '''<div class="login-split-wrapper">
  
  <div class="login-image-panel" id="desktop-image-panel">
    <img src="login-hero.jpg" alt="Smart City Transit">
  </div>

  <div class="login-form-panel">
    <div class="login-card card" style="width: 100%; max-width: 440px;">'''
    html = re.sub(pattern1, replacement1, html, flags=re.DOTALL)
    
    # 2. Add the extra closing div required for the new wrapper
    pattern2 = r'(<script src="app\.js"></script>)'
    replacement2 = r'  </div>\n</div>\n\n\1'
    html = re.sub(pattern2, replacement2, html)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("index.html updated successfully.")
except Exception as e:
    print(f"Error updating index.html: {e}")

# Update selection.html
try:
    with open('selection.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # We need to preserve the result-card structure but inject Journey Details
    # Let's find result-card contents.
    # We want: 
    # Source / Destination, Distance, Rate per km, Total fare.
    
    # Current Result Card inner structure:
    """
          <!-- Result Card -->
          <div class="result-card" id="result-card">
            <div class="result-route-timeline" id="res-timeline">
              <!-- Rendered via JS -->
            </div>

            <div class="result-fare">
              <div class="fare-label">Total Fare</div>
              <div class="fare-amount">
                <span class="fare-symbol">₹</span>
                <span id="res-fare">0</span>
              </div>
            </div>

            <div class="result-details">
              <div class="result-detail-item">
                <div class="detail-label">Distance</div>
                <div class="detail-value" id="res-distance">– km</div>
              </div>
              <div class="result-detail-item">
                <div class="detail-label">Route Type</div>
                <div class="detail-value">🚌 City Bus</div>
              </div>
              <div class="result-detail-item">
                <div class="detail-label">Category</div>
                <div class="detail-value">General</div>
              </div>
              <div class="result-detail-item">
                <div class="detail-label">Est. Travel Time</div>
                <div class="detail-value" id="res-time">– mins</div>
              </div>
            </div>

            <div class="result-actions">
              ... book btn ...
    """

    new_result_card = '''          <!-- Result Card -->
          <div class="result-card" id="result-card">
            
            <div style="margin-bottom: 20px; text-align: center;">
               <h3 style="margin:0; font-size: 18px; color: var(--text-primary);">Journey Details</h3>
            </div>

            <div class="result-details" style="grid-template-columns: 1fr 1fr; margin-bottom: 24px;">
              <div class="result-detail-item">
                <div class="detail-label">Source</div>
                <div class="detail-value" id="res-source-disp" style="font-size: 13px;">–</div>
              </div>
              <div class="result-detail-item">
                <div class="detail-label">Destination</div>
                <div class="detail-value" id="res-dest-disp" style="font-size: 13px;">–</div>
              </div>
              <div class="result-detail-item">
                <div class="detail-label">Distance</div>
                <div class="detail-value" id="res-distance">–</div>
              </div>
              <div class="result-detail-item">
                <div class="detail-label">Rate (per km)</div>
                <div class="detail-value" id="res-rate">₹ 0.00 / km</div>
              </div>
            </div>

            <div class="result-fare">
              <div class="fare-label">Total Fare</div>
              <div class="fare-amount">
                <span class="fare-symbol">₹</span>
                <span id="res-fare">0</span>
              </div>
            </div>

            <div class="result-actions">
              <button class="btn btn-emerald btn-book" id="book-btn" onclick="startBookingFlow()">
                ⚡ Book Now
              </button>
            </div>
          </div>'''
          
    pattern_rc = r'<!-- Result Card -->\s*<div class="result-card" id="result-card">.*?</div>\s*</div> <!-- ends route-controls -->'
    replacement_rc = new_result_card + '\n\n        </div> <!-- ends route-controls -->'
    
    html = re.sub(pattern_rc, replacement_rc, html, flags=re.DOTALL)
    
    with open('selection.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("selection.html updated successfully.")
except Exception as e:
    print(f"Error updating selection.html: {e}")

# Update app.js
try:
    with open('app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # Look for the fare calculation rendering logic
    pattern_js = r"document\.getElementById\('res-fare'\)\.textContent = data\.fare;\s*document\.getElementById\('res-distance'\)\.textContent = data\.distance \+ ' km';\s*document\.getElementById\('res-time'\)\.textContent = Math\.round\(data\.distance \* 2\.5\) \+ ' mins';"
    
    replacement_js = """document.getElementById('res-fare').textContent = data.fare;
            document.getElementById('res-distance').textContent = data.distance + ' km';
            
            // New Journey details population
            let parsedDist = parseFloat(data.distance);
            let parsedFare = parseFloat(data.fare);
            let ratePerKm = (parsedDist > 0 && !isNaN(parsedDist)) ? (parsedFare / parsedDist).toFixed(2) : "0.00";
            
            if(document.getElementById('res-rate')) document.getElementById('res-rate').textContent = '₹ ' + ratePerKm + ' / km';
            if(document.getElementById('res-source-disp')) document.getElementById('res-source-disp').textContent = src;
            if(document.getElementById('res-dest-disp')) document.getElementById('res-dest-disp').textContent = dest;"""
            
    js = re.sub(pattern_js, replacement_js, js)
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("app.js updated successfully.")
except Exception as e:
    print(f"Error updating app.js: {e}")
