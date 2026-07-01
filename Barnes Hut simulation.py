from vpython import sphere, vector, rate, canvas, color
import math
# ----------------- Particle Class -----------------
class Particle:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.fx = 0.0
        self.fy = 0.0
        self.body = sphere(pos=vector(x, y, 0), radius=2e9, color=color.cyan, make_trail=True,trail_type='points',interval=10,retain=50)
    def reset_force(self):
        self.fx = 0.0
        self.fy = 0.0

    def update(self, dt):
        ax = self.fx / self.mass
        ay = self.fy / self.mass

        # Half-step velocity update
        self.vx += 0.5 * ax * dt
        self.vy += 0.5 * ay * dt

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.body.pos = vector(self.x, self.y, 0)

# ----------------- Quad Class -----------------
class Quad:
    def __init__(self, xc, yc, length):
        self.xc = xc
        self.yc = yc
        self.length = length

    def contains(self, p):
        half = self.length / 2
        return (self.xc - half <= p.x <= self.xc + half) and (self.yc - half <= p.y <= self.yc + half)

    def NW(self):
        return Quad(self.xc - self.length / 4, self.yc + self.length / 4, self.length / 2)

    def NE(self):
        return Quad(self.xc + self.length / 4, self.yc + self.length / 4, self.length / 2)

    def SW(self):
        return Quad(self.xc - self.length / 4, self.yc - self.length / 4, self.length / 2)

    def SE(self):
        return Quad(self.xc + self.length / 4, self.yc - self.length / 4, self.length / 2)

# ----------------- Barnes-Hut Tree -----------------
class BHTree:
    def __init__(self, quad):
        self.quad = quad
        self.particle = None
        self.mass = 0.0
        self.cx = 0.0
        self.cy = 0.0
        self.NW = None
        self.NE = None
        self.SW = None
        self.SE = None

    def insert(self, p):
        if not self.quad.contains(p):
            return

        if self.mass == 0:
            self.particle = p
            self.mass = p.mass
            self.cx = p.x
            self.cy = p.y
            return

        if self.NW is None:
            self.subdivide()
            if self.particle:
                self._put_in_child(self.particle)
                self.particle = None

        self._put_in_child(p)

        total_mass = self.mass + p.mass
        self.cx = (self.cx * self.mass + p.x * p.mass) / total_mass
        self.cy = (self.cy * self.mass + p.y * p.mass) / total_mass
        self.mass = total_mass

    def subdivide(self):
        self.NW = BHTree(self.quad.NW())
        self.NE = BHTree(self.quad.NE())
        self.SW = BHTree(self.quad.SW())
        self.SE = BHTree(self.quad.SE())

    def _put_in_child(self, p):
        if self.quad.NW().contains(p):
            self.NW.insert(p)
        elif self.quad.NE().contains(p):
            self.NE.insert(p)
        elif self.quad.SW().contains(p):
            self.SW.insert(p)
        elif self.quad.SE().contains(p):
            self.SE.insert(p)

    def update_force(self, p, theta=0.5):
        if self.particle is p:
            return

        dx = self.cx - p.x
        dy = self.cy - p.y
        epsilon = 5e8 # Softening factor to prevent singularity
        dist = math.sqrt(dx**2 + dy**2 + epsilon**2)
        s = self.quad.length

        if self.NW is None or (s / dist) < theta:
            G = 6.6743e-11
            force = G * p.mass * self.mass / (dist ** 2)
            fx = force * dx / dist
            fy = force * dy / dist
            p.fx += fx
            p.fy += fy
        else:
            if self.NW: self.NW.update_force(p, theta)
            if self.NE: self.NE.update_force(p, theta)
            if self.SW: self.SW.update_force(p, theta)
            if self.SE: self.SE.update_force(p, theta)
def compute_center_of_mass(particles):
    total_mass = sum(p.mass for p in particles)
    x_com = sum(p.x * p.mass for p in particles) / total_mass
    y_com = sum(p.y * p.mass for p in particles) / total_mass
    z_com = 0  # Assuming 2D motion
    return (x_com, y_com, z_com)
# ----------------- Simulation Setup -----------------
canvas(title="Barnes-Hut Simulation", width=800, height=800, background=vector(0, 0, 0), range=2e11)

# ----------------- Particle List -----------------
# Add particles manually here
G = 6.6743e-11
M = 2e30  # central mass

def orbital_velocity(r):
    return math.sqrt(G * M / r)


particles = [
    ]#Add particle deetails

# ----------------- Simulation Parameters -----------------
# ---- Correct the Central Body's Velocity to Fix Drifting COM ----
total_px = sum(p.mass * p.vx for p in particles[1:])  # skip the central body
total_py = sum(p.mass * p.vy for p in particles[1:])

central = particles[0]  # Assuming first particle is central mass

central.vx = -total_px / central.mass
central.vy = -total_py / central.mass
# ------------------------------------------------------------------
dt = 100  # Small for accuracy
steps =2000
rate_value = 100
boundary = Quad(0, 0, 6e11)
from vpython import label

# Label to display COM and positions (initial dummy text)
info_label = label(
    pos=vector(0, 0, 0), 
    text="Initializing...", 
    xoffset=0, yoffset=250, 
    space=30, height=15, border=10, 
    font='monospace', 
    box=False, 
    color=color.white,
    line=False
    )

# ----------------- Main Simulation Loop -----------------
for step in range(steps):
    rate(rate_value)

    # Step 1: Insert all particles into the tree
    tree = BHTree(boundary)
    for p in particles:
        if boundary.contains(p):
            tree.insert(p)

    # Step 2: Compute initial forces and half-step velocity update
    for p in particles:
        p.reset_force()
        tree.update_force(p)

        # First half of Velocity Verlet
        ax = p.fx / p.mass
        ay = p.fy / p.mass
        p.vx += 0.5 * ax * dt
        p.vy += 0.5 * ay * dt

        # Update position using half-step velocity
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.body.pos = vector(p.x, p.y, 0)

    # Step 3: Rebuild tree with new positions
    tree = BHTree(boundary)
    for p in particles:
        if boundary.contains(p):
            tree.insert(p)

    # Step 4: Recompute force and second half of velocity update
    for p in particles:
        p.reset_force()
        tree.update_force(p)

        ax = p.fx / p.mass
        ay = p.fy / p.mass
        p.vx += 0.5 * ax * dt
        p.vy += 0.5 * ay * dt

    # Step 5: Compute and show COM
    com = compute_center_of_mass(particles)
    masses = [p.mass for p in particles]
    print(f"Step {step}: COM = ({com[0]:.2e}, {com[1]:.2e}, {com[2]:.2e})")

    if step == 0:
        com_dot = sphere(pos=vector(*com), radius=4e9, color=color.red)
    else:
        com_dot.pos = vector(*com)

    display_text = f"COM: ({com[0]:.2e}, {com[1]:.2e})\n"
    for i, p in enumerate(particles[:5]):
        display_text += f"P{i+1}: ({p.x:.2e}, {p.y:.2e})\n"
    info_label.text = display_text
