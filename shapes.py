import cv2
import numpy as np
from agent import Agent, VisualAgent

class CircleAgent(VisualAgent):
    def __init__(self, agent, color=None, radius=None, noise=None):
        super(CircleAgent, self).__init__(agent, color=color)

        self.radius = self._handle_radius(radius)
        self.noise = noise

        if self.noise is None and self.color == 'noise':
            self.noise = self._generate_noise()

    def _generate_noise(self):
        radius = self.radius
        z = np.zeros((2*radius, 2*radius, 3))
        # n = np.random.randint(256, size=(2*radius,2*radius,3), dtype=np.uint8)
        n = np.random.default_rng().integers(255, size=(2*radius, 2*radius, 3), dtype=np.uint8)

        z = cv2.circle(z, (radius,radius), radius, (1,1,1), -1)

        for y in range(2*radius):
            for x in range(2*radius):
                n[y,x,:] = self._random_color()

        return np.multiply(z,n)

    def _handle_radius(self, radius, min_rad=2, max_rad = 10):
        if radius is None:
            return np.random.binomial(max_rad - min_rad, 0.5) + min_rad
        else:
            return radius

    def draw(self, image, color=None):
        if self.noise is not None and color is None:
            cx,cy = self.pos
            r = self.radius
            h,w,_ = self.noise.shape
            height,width,_ = image.shape

            noise_mask = np.zeros(self.noise.shape)
            noise_mask[np.nonzero(self.noise)] = 1

            sub = image[cy-r:cy+r,cx-r:cx+r,:]

            image[cy-r:cy+r,cx-r:cx+r,:] = sub - np.multiply(sub, noise_mask[:sub.shape[0], :sub.shape[1], :]) + self.noise[:sub.shape[0], :sub.shape[1], :]
            
            return image
        else:
            return cv2.circle(image, self.pos, self.radius, color if color is not None else self.color, -1)

    def update(self):
        return CircleAgent(Agent(*super().update()._digest()), color=self.color, radius=self.radius, noise=self.noise)

def generate_circle_agent(world, noise=False):
    rand_pos = (np.random.randint(world.width), np.random.randint(world.height))
    rand_vel = (np.random.geometric(0.9) - 1, np.random.geometric(0.9) - 1)

    if noise:
        return CircleAgent(Agent(world, rand_pos, rand_vel, (0,0)), color='noise')
    else:
        return CircleAgent(Agent(world, rand_pos, rand_vel, (0,0)))

class StaticCircleAgent(CircleAgent):
    def __init__(self, agent, color=None, radius=None, noise=None):
        super().__init__(agent, color=color, radius=radius, noise=noise)

    def update(self):
        return StaticCircleAgent(Agent(self.world, self.pos, (0,0), (0,0)), color=self.color, radius=self.radius, noise=self.noise)

def generate_static_circle_agent(world, noise=False):
    rand_pos = (np.random.randint(world.width), np.random.randint(world.height))

    if noise:
        return StaticCircleAgent(Agent(world, rand_pos, (0,0), (0,0)), color='noise')
    else:
        return StaticCircleAgent(Agent(world, rand_pos, (0,0), (0,0)))



class BigStaticCircle(StaticCircleAgent):
    def __init__(self, agent, color=None, radius=None):
        super().__init__(agent, color=color, radius=radius)

    def _handle_radius(self, radius, min_rad=2, max_rad=10):
        return super()._handle_radius(radius, min_rad=20, max_rad=100)

def generate_big_static_circle(world, noise=False):
    rand_pos = (np.random.randint(world.width), np.random.randint(world.height))

    if noise:
        return BigStaticCircle(Agent(world, rand_pos, (0,0), (0,0)), color='noise')
    else:
        return BigStaticCircle(Agent(world, rand_pos, (0,0), (0,0)))

class RectangleAgent(VisualAgent):
    def __init__(self, agent, color=None, shape=None, noise=None):
        super(RectangleAgent, self).__init__(agent, color=color)

        self.shape = self._handle_shape(shape)
        self.noise = noise

        if self.noise is None and self.color == 'noise':
            self.noise = self._generate_noise()

    def _generate_noise(self):
        return np.random.default_rng().integers(255, size=(*self.shape, 3), dtype=np.uint8)

    def _handle_shape(self, shape, min_dim=2, max_dim=15):
        if shape is None:
            return (
                np.random.binomial(max_dim - min_dim, 0.5) + min_dim,
                np.random.binomial(max_dim - min_dim, 0.5) + min_dim
            )
        else:
            return shape

    def draw(self, image, color=None):
        x,y = self.pos
        h,w = self.shape

        if not (x in range(image.shape[1]) and y in range(image.shape[0])):
            return image

        hh = h // 2
        hw = w // 2

        tlx = max(x - hw,0)
        tly = max(y - hh,0)
        brx = min(x + hw, image.shape[1])
        bry = min(y + hh, image.shape[0])

        if self.noise is not None and color is None:
            # TODO this is calculated wrong.
            print(x,y)
            print(tly,bry,tlx,brx)
            image[tly:bry,tlx:brx,:] = self.noise[0:bry-tly, 0:brx-tlx,:]

            return image
        else:
            return cv2.rectangle(image, (tlx,tly), (brx,bry), color if color is not None else self.color, -1)

    def update(self):
        return RectangleAgent(Agent(*super().update()._digest()), color=self.color, shape=self.shape, noise=self.noise)

def generate_rectangle_agent(world, noise=False):
    rand_pos = (np.random.randint(world.width), np.random.randint(world.height))
    rand_vel = (np.random.geometric(0.9) - 1, np.random.geometric(0.9) - 1)

    if noise:
        return RectangleAgent(Agent(world, rand_pos, rand_vel, (0,0)), color='noise')
    else:
        return RectangleAgent(Agent(world, rand_pos, rand_vel, (0,0)))

class StaticRectangleAgent(RectangleAgent):
    def __init__(self, agent, color=None, shape=None, noise=None):
        super().__init__(agent, color=color, shape=shape, noise=noise)

    def update(self):
        return StaticRectangleAgent(Agent(self.world, self.pos, (0,0), (0,0)), color=self.color, shape=self.shape, noise=self.noise)

def generate_static_rectangle_agent(world, noise=False):
    rand_pos = (np.random.randint(world.width), np.random.randint(world.height))

    if noise:
        return StaticRectangleAgent(Agent(world, rand_pos, (0,0), (0,0)), color='noise')
    else:
        return StaticRectangleAgent(Agent(world, rand_pos, (0,0), (0,0)))
