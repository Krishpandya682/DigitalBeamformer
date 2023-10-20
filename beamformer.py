import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import warnings
warnings.filterwarnings("ignore")

plt.rcParams["figure.figsize"] = (8, 8)
plt.rcParams["font.size"] = 14
plt.style.use('dark_background') # dark theme

# 2*pi*r/lambda is the phase of the emitter from the focus point x,y
def CalculatePhaseFromFocus(x, y, e):
    return np.sqrt(np.sum((e.r-np.array([x, y]))**2))*(2*np.pi/e.lambda0)

# Create an animated/moving emitter based on it's position (x,y), speed (c), frequecy(f),
# phase(phi), Other variables necessary for the plotting part of the program
class Emitter():

    def __init__(self, x, y, c, f, phi, rMax=100, color="tab:blue", alpha=0.6):
        self.r, self.c, self.f, self.rMax, self.alpha = np.array(
            [x, y]), c, f, rMax, alpha
        self.color = color
        self.SetUp()
        self.SetPhase(phi)

    # For the animation increment the time function. Also increase the size 
    # of each circle appropriately
    def Increment(self, dt):
        self.t += dt
        if self.t < self.t0:
            return
        for i, circle in enumerate(self.circles):
            r = i*self.lambda0 + self.Wrap(self.lambda0*self.phi/(2*np.pi) +
                                           self.c * self.t, self.lambda0)
            circle.set_height(2*r)
            circle.set_width(2*r)
            circle.set_alpha(self.alpha if i < ((self.t-self.t0)/self.T) else 0)

    # Set phase and an offset time(this is in order to display the animation correctly)
    def SetPhase(self, phi):
        self.phi = self.Wrap(phi, 2*np.pi)
        self.t0 = self.T*(1-self.phi/(2*np.pi))
        self.t = 0

    # Setup to calculate different values necessary
    def SetUp(self):
        self.lambda0 = self.c/self.f 
        self.T = 1./self.f
        self.N = np.int64(np.ceil(self.rMax/self.lambda0))
        self.circles = [plt.Circle(xy=tuple(self.r), fill=False, lw=2,
                                   radius=0, alpha=self.alpha,
                                   color=self.color)
                        for i in range(self.N)]
    # In order to wrap the circles back after every iteration so that it keeps looping
    def Wrap(self, x, x_max):
        if x >= 0:
            return x - np.floor(x/x_max) * x_max
        if x < 0:
            return x_max - (-x - np.floor(-x/x_max) * x_max)

# Array of emmiters which basically increments each emmtier
class EmitterArray():

    def __init__(self):
        self.emitters = []

    def AddEmitter(self, e):
        self.emitters.append(e)

    def Increment(self, dt):
        for emitter in self.emitters:
            emitter.Increment(dt)

    def GetCircles(self):
        """Get all the circles from all the emitters"""
        circles = []
        for emitter in self.emitters:
            circles.extend(emitter.circles)
        return circles

    def RemoveOffset(self):
        """Only run this one time after all emitters have been added"""
        offsets = []
        for emitter in self.emitters:
            offsets.append(emitter.t0)
        offset_min = np.min(offsets)
        for emitter in self.emitters:
            emitter.Increment(offset_min)

    @property
    def circles(self):
        return self.GetCircles()


FPS = 30
X, Y = 100, 100
c, f = 3, 0.2
lambda0 = c/f

N = 10

emitter_array = EmitterArray()

# Main code!
# ########################################################
# #Focussed Array
xs = np.linspace(-lambda0, lambda0, N)
ys = np.zeros_like(xs)

inp = input("Give the x,y coordinates of where you want the beam to be focused in the format 'x,y' ")
x,y = inp.split(',')
x = int(x)
y = int(y)
print ("Directing the emmiter to point to",x,",",y)
for i in range(N):
    #create an array of N emmiters on the x axis from -lambda to lambda at equal distance
    e = Emitter(xs[i], ys[i], c, f, 0)
    # Calculate the phase for each emmiter in order to connverge on the user given point
    phase = CalculatePhaseFromFocus(x, y, e)
    # update the emmiter's phase to that
    e.SetPhase(phase)
    # Add the emitter to the array
    emitter_array.AddEmitter(e)
# #######################################################
emitter_array.RemoveOffset()



# Plot the animation
fig, ax = plt.subplots()
ax.set_xlim([-X/2, Y/2])
ax.set_ylim([-X/2, Y/2])
ax.set_aspect(1)
ax.grid(alpha=0.2)
fig.tight_layout()

for circle in emitter_array.circles:
    ax.add_patch(circle)

for emitter in emitter_array.emitters:
    ax.add_patch(plt.Circle(tuple(emitter.r), 0.4, color="purple"))


def init():
    return tuple(emitter_array.circles)


def update(frame_number):
    emitter_array.Increment(1/FPS)
    return tuple(emitter_array.circles)


if __name__ == "__main__":
    ani = FuncAnimation(fig, update, init_func=init,
                        interval=1000/FPS, blit=True)
    plt.plot(x,y,'ro')
    plt.show()
    