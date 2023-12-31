# Importing useful packages
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d

# Useful physical constants
e = 1.60217663e-19 # charge of positron, C
me = 9.1093837e-31 # mass of electron, kg
mp = 1.67262192e-27 # mass of proton, kg

# Function to calculate electric field
def E(r):
    return np.array([0, 0, 0]) # N/C
    # return np.array([1, 0, 0]) # N/C

# Function to calculate magnetic field
def B(r):
    # return np.array([0, 0, 0]) # T
    return np.array([0, 1e-10, 0]) # T

# Function to calculate gravitational field
def g(r):
    return np.array([0, 0, 0]) # m/s
    # return np.array([0, 0, -9.8]) # m/s

# Function for acceleration
def a(qByM, r, v):
    return qByM*(E(r) + np.cross(v, B(r))) + g(r)

def set_axes_equal(ax):
    """
    Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

# Object for a charged particle
class Particle():

    # Constructor
    def __init__(self, q, m, rs, vs):
        self.q = q
        self.m = m
        self.rs = rs
        self.vs = vs

    # Euler timestep
    def updateEuler(self, dt):

        # Initial position
        ri = self.rs[-1]

        # Initial velocity
        vi = self.vs[-1]

        # Charge by mass ratio
        qByM = self.q/self.m # C/kg

        # Update velocity
        vf = vi + a(qByM, ri, vi)*dt
        self.vs = np.append(self.vs, np.array([vf]), axis=0)

        # Update position
        rf = ri + vi*dt
        rf = ri + ((vi+vf)/2)*dt
        self.rs = np.append(self.rs, np.array([rf]), axis=0)

    # Runge-kutta-4 timestep
    def updateRK4(self, dt):

        # Initial position
        ri = self.rs[-1]

        # Initial velocity
        vi = self.vs[-1]

        # Charge by mass ratio
        qByM = self.q/self.m # C/kg

        # Calculating constants
        k1v = a(qByM, ri, vi)
        k1r = vi

        k2v = a(qByM, ri + k1r*(dt/2), k1r)
        k2r = vi + k1v*(dt/2)

        k3v = a(qByM, ri + k2r*(dt/2), k2r)
        k3r = vi + k2v*(dt/2)

        k4v = a(qByM, ri + k3r*dt, k3r)
        k4r = vi + k3v*dt

        # Update velocity
        vf = vi + (dt/6)*(k1v + 2*k2v + 2*k3v + k4v)
        self.vs = np.append(self.vs, np.array([vf]), axis=0)

        # Update position
        rf = ri + (dt/6)*(k1r + 2*k2r + 2*k3r + k4r)
        self.rs = np.append(self.rs, np.array([rf]), axis=0)

# Function to plot results
def plotResults(particles, plotFields=False):

    # Creating axes
    ax = plt.axes(projection='3d')

    # For every particle
    for pNum, particle in enumerate(particles):

        # Redistributing coordinates
        coords = particles[pNum].rs.T
        xs = coords[0]
        ys = coords[1]
        zs = coords[2]

        if pNum == 0:
            # Plotting trajectory
            ax.plot(xs, ys, zs, 'black', label='trajectory')

            # Plotting start and end
            ax.scatter(xs[0], ys[0], zs[0], color='green', label='start')
            ax.scatter(xs[-1], ys[-1], zs[-1], color='red', label='end')

        else:
            # Plotting trajectory
            ax.plot(xs, ys, zs, 'black')

            # Plotting start and end
            ax.scatter(xs[0], ys[0], zs[0], color='green')
            ax.scatter(xs[-1], ys[-1], zs[-1], color='red')

    # If you want to plot EM fields
    if plotFields:

        # Creating meshgrid for EM field
        x, y, z = np.meshgrid(np.arange(-5, 5, 1),
                              np.arange(-5, 5, 1),
                              np.arange(-5, 5, 1))

        # Finding E field
        Egrid = E(np.array([x, y, z]).T).T

        # Finding B field
        Bgrid = B(np.array([x, y, z]).T).T

        # Plotting Electric field
        ax.quiver(x, y, z, Egrid[0], Egrid[1], Egrid[2], length=0.3, normalize=True, color='magenta', alpha=0.3, label='E-field')

        # Plotting Magnetic field
        ax.quiver(x, y, z, Bgrid[0], Bgrid[1], Bgrid[2], length=0.3, normalize=True, color='blue', alpha=0.3, label='B-field')

    # Displaying plot
    ax.legend()
    ax.set_xlabel('$x$, (m)', fontsize=10)
    ax.set_ylabel('$y$, (m)', fontsize=10)
    ax.set_zlabel('$z$, (m)', fontsize=10)
    set_axes_equal(ax)
    plt.show()

# Main functioning of script
def main(particles, t, dt, integrator='euler'):

    # Iterations
    n = int(t/dt)

    # Simulate over number of iterations
    for i in range(n):
        if i%1000==0:
            print(f'{(100*i/n):.1f}%')

        # Update every particle position
        for particle in particles:
            if integrator=='RK4':
                particle.updateRK4(dt)
            else:
                particle.updateEuler(dt)

    # Plotting results
    plotResults(particles)

    # Return all particles
    # return particles

if __name__ == '__main__':

    # List of particles
    particles = []

    # Defining particles
    particles.append(Particle(-e, me, np.array([[0, 0, 0]]), np.array([[1e1, 1, 0]])))
    particles.append(Particle(e, 2*me, np.array([[-1, 0, 0]]), np.array([[1e1, 1, 0]])))
    particles.append(Particle(-e, 3*me, np.array([[0, -1, 0]]), np.array([[-1e1, -1, 0]])))

    # Total simulation time
    t = 2 # s

    # Timestep
    dt = 1e-4 # s

    # Run main functioning of script
    # results = main(particles, t, dt, 'euler')
    results = main(particles, t, dt, 'RK4')