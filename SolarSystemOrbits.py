import math
from datetime import datetime
import matplotlib.pyplot as plt

# Constants
DEG2RAD = math.pi / 180  # Convert degrees to radians

# Orbital elements for all planets (simplified, approximate, referenced to J2000)
planet_data = {
    'Mercury': {'a': 0.387, 'e': 0.206, 'i': 7.0,   'Ω': 48.3,  'ω': 29.1,  'M0': 174.8, 'T': 88},
    'Venus':   {'a': 0.723, 'e': 0.007, 'i': 3.4,   'Ω': 76.7,  'ω': 54.9,  'M0': 50.4,  'T': 224.7},
    'Earth':   {'a': 1.000, 'e': 0.017, 'i': 0.0,   'Ω': -11.3, 'ω': 114.2, 'M0': 358.6, 'T': 365.25},
    'Mars':    {'a': 1.524, 'e': 0.093, 'i': 1.85,  'Ω': 49.6,  'ω': 286.5, 'M0': 19.4,  'T': 687},
    'Jupiter': {'a': 5.203, 'e': 0.049, 'i': 1.3,   'Ω': 100.5, 'ω': 273.9, 'M0': 20.0,  'T': 4331},
    'Saturn':  {'a': 9.537, 'e': 0.056, 'i': 2.5,   'Ω': 113.7, 'ω': 339.4, 'M0': 317.0, 'T': 10747},
    'Uranus':  {'a': 19.191,'e': 0.046, 'i': 0.8,   'Ω': 74.0,  'ω': 96.9,  'M0': 142.2, 'T': 30589},
    'Neptune': {'a': 30.07, 'e': 0.010, 'i': 1.8,   'Ω': 131.8, 'ω': 272.8, 'M0': 256.1, 'T': 59800},
    'Pluto':   {'a': 39.482,'e': 0.2488,'i': 17.14, 'Ω': 110.3, 'ω': 224.1, 'M0': 14.9,  'T': 90560}
}

def kepler_equation(M, e, tol=1e-6):
    """Solve Kepler's Equation: M = E - e*sin(E) using Newton-Raphson iteration."""
    M = math.radians(M)
    E = M if e < 0.8 else math.pi  # Initial guess for eccentric anomaly
    while True:
        dE = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))  # Newton's method
        E -= dE
        if abs(dE) < tol:
            break
    return E

def get_planet_position(planet, days_since_epoch):
    """Return the current (x, y) position of a planet in AU."""
    p = planet_data[planet]
    # Mean anomaly evolves with time
    M = (p['M0'] + 360 * days_since_epoch / p['T']) % 360
    E = kepler_equation(M, p['e'])  # Solve for eccentric anomaly

    # Convert to polar coordinates
    r = p['a'] * (1 - p['e'] * math.cos(E))  # Orbital radius
    v = 2 * math.atan2(math.sqrt(1 + p['e']) * math.sin(E / 2),
                       math.sqrt(1 - p['e']) * math.cos(E / 2))  # True anomaly

    # Convert to Cartesian coordinates
    x = r * math.cos(v)
    y = r * math.sin(v)
    return x, y

def draw_solar_system(ax, zoom_level):
    """Render all planets and their orbits on the matplotlib axis."""
    ax.clear()  # Clear previous frame

    # Compute days since J2000 epoch
    now = datetime.utcnow()
    epoch = datetime(2000, 1, 1)
    days_since_epoch = (now - epoch).days

    # Draw the Sun
    ax.plot(0, 0, 'yo', label='Sun', markersize=10)

    # Draw each planet
    for name in planet_data:
        # Get planet position
        x, y = get_planet_position(name, days_since_epoch)
        ax.plot(x, y, 'o', label=name)
        ax.text(x + 0.3, y + 0.3, name, fontsize=8)

        # Draw orbit path (dotted line around the Sun)
        orbit_x, orbit_y = [], []
        for deg in range(360):
            E = kepler_equation(deg, planet_data[name]['e'])
            r = planet_data[name]['a'] * (1 - planet_data[name]['e'] * math.cos(E))
            v = 2 * math.atan2(math.sqrt(1 + planet_data[name]['e']) * math.sin(E / 2),
                               math.sqrt(1 - planet_data[name]['e']) * math.cos(E / 2))
            orbit_x.append(r * math.cos(v))
            orbit_y.append(r * math.sin(v))
        ax.plot(orbit_x, orbit_y, linestyle='--', alpha=0.2)

    # Viewport / zoom controls
    ax.set_xlim(-zoom_level, zoom_level)
    ax.set_ylim(-zoom_level, zoom_level)
    ax.set_title("Real-Time Solar System Orbits (2D)")
    ax.set_aspect('equal')
    ax.set_xlabel("x (AU)")
    ax.set_ylabel("y (AU)")
    ax.grid(True)
    ax.legend(loc='upper right', fontsize=7)

def on_key(event):
    """Keyboard handler for zooming in and out using + / - / 0 keys."""
    global zoom
    if event.key == '=':
        zoom = max(zoom / 1.2, 0.1)  # Zoom in
    elif event.key == '-':
        zoom = min(zoom * 1.2, 100)  # Zoom out
    elif event.key == '0':
        zoom = default_zoom  # Reset zoom
    draw_solar_system(ax, zoom)
    plt.draw()

# --- Main Program ---

# Set initial zoom level and plot window
default_zoom = 45
zoom = default_zoom

# Create matplotlib figure
fig, ax = plt.subplots(figsize=(10, 10))
fig.canvas.mpl_connect('key_press_event', on_key)  # Enable keyboard input
draw_solar_system(ax, zoom)  # Initial draw
plt.show()