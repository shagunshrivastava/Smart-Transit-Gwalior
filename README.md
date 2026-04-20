# Smart Transit Gwalior 🚌

Smart Transit Gwalior is a full-stack, smart transport booking and route management web application. It transitions legacy static operations into a dynamic, production-ready system to help passengers easily compute fares, find optimal routes, and book trips within Gwalior. 

The application utilizes a **Flask (Python) REST API** backend paired with a **vanilla HTML/JS/CSS** frontend to deliver a smooth and responsive end-to-end booking flow.

## 🌟 Features

* **Authentication System**: Secure passenger signup and login functionality. Distinct `Admin` and `Passenger` roles limit unauthorized data tampering.
* **Optimal Route Calculation**: Utilizes a graph-based Dijkstra algorithm implementation on the backend to dynamically combine connections and find the shortest paths and most accurate fares between any two stops.
* **Vehicle Options**: Variable fare multipliers depending on the ride type (e.g., City Bus, AC Bus, Cab).
* **Booking Simulation**: Generates trips on the fly with random driver assignments, vehicle plates, and OTP verifications for a realistic app flow.
* **Admin Dashboard**: A secure portal available only to `Admin` accounts allowing CRUD operations on existing Routes and Fares in the database.
* **Responsive Visuals**: A custom UI theme emphasizing a clean end-to-end user experience with built-in map visualizations.
* **Database Driven**: Uses SQLite3 directly embedded into the application without relying on unstable hard-coded lists.

## 🛠️ Technologies Used

- **Backend**: Python 3.11+, Flask Web Framework, Flask-CORS
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6)

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shagunshrivastava/Smart-Transit-Gwalior.git
   cd Smart-Transit-Gwalior
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
   * Activate the environment:
     * **Windows**: `venv\Scripts\activate`
     * **Mac/Linux**: `source venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(If you don't have a `requirements.txt`, install Flask individually: `pip install Flask Flask-Cors`)*

4. **Run the Application:**
   ```bash
   python api.py
   ```
   The script will automatically initialize the database `transport.db`, seed the initial Gwalior routes data, and start the local development server.

5. **Access the App:**
   Open your browser and navigate to `http://127.0.0.1:5000`

## 🚏 Seeded Routes (Gwalior)
By default, standard locations such as Gwalior Railway Station, Bus Stand (ISBT), City Centre, Lashkar, Jiwaji University, DD Mall, and more are pre-loaded in the transit map data.

## 🔐 Credentials
If you need to access the Admin dashboard, a default admin account is seeded at runtime:
* **Username**: `admin`
* **Password**: `admin123`

---
*Created for the ongoing modernization of the Gwalior Transport System.*
