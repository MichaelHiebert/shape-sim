import numpy as np
import math
import random
from shapes import generate_circle_agent,generate_static_circle_agent,generate_big_static_circle

class World:
    def __init__(self, width, height, cur_view=None, agents=None, color=None, noisy=False, view_size=(400,400)):
        """
            width :: int :
                the width (in pixels) of this world
            height :: int :
                the height (in pixels) of this world
            cur_view :: View :
                the current view of this world
            agents :: list or int or None :
                ::list : a predefined list of agents
                ::int : the number of agents to randomly generate
                ::None : generate a completely random number of random agents
            color :: tuple of int, str, or None :
                ::tuple of int : an rgb color value
                ::str : a predifined pattern, must be one of ('noise',)
                ::None : generate a completely random color
        """

        self.width = width
        self.height = height

        if cur_view is not None:
            self.view = cur_view
        else:
            self.view = self._generate_view(size=view_size)

        self.agents = self._handle_agents(agents, noisy)

        self.color = self._handle_color(color)

        if self.color == 'noise':
            self.noise = self._generate_noise()

    def update(self):
        self.view = self.view.update()

        self.agents = [agent.update() for agent in self.agents]

    def draw(self):
        world = np.zeros((self.height,self.width,3), np.uint8)

        if self.color == 'noise':
            world = self.noise.copy()
        else:
            world[:,:,0],world[:,:,1],world[:,:,2] = self.color

        for agent in self.agents:
            if agent.is_moving():
                world = agent.draw(world)
        for agent in self.agents:
            if not agent.is_moving():
                world = agent.draw(world)

        return world[self.view.tly:self.view.bry,self.view.tlx:self.view.brx,:]

    def draw_motion_mask(self):
        static = np.zeros((self.height,self.width,3), np.uint8)
        dynamic = np.zeros((self.height,self.width,3), np.uint8)

        for agent in self.agents:
            static = agent.draw_static_mask(static)
            dynamic = agent.draw_motion_mask(dynamic)

        dynamic[np.where(static == dynamic)] = 0

        return dynamic[self.view.tly:self.view.bry,self.view.tlx:self.view.brx,:]

    def draw_motion_map(self, height, width):
        world = np.zeros((height, width))
        
        for agent in self.agents:
            sec = agent.get_sector(self.view, height,width)
            if sec:
                world[sec] = 1

        return world

    def _generate_noise(self):
        # return np.random.randint(256, size=(self.height,self.width,3), dtype=np.uint8)
        return np.random.default_rng().integers(255, size=(self.height,self.width, 3), dtype=np.uint8)

    def _random_color(self):
        return (np.random.randint(256), np.random.randint(256), np.random.randint(256))
        
    def _handle_agents(self, agents, noisy=False):
        if agents is None:
            # First we choose some density of agents that we want per a given 100x100 area of space
            min_density = 25
            max_density = 75
            true_density = int(np.random.binomial(max_density - min_density, 0.5)) + min_density

            # Next we determine how large a volume we are dealing with
            subset_volume = 100 * 100
            total_volume = self.width * self.height

            # calculate the number of agents
            num_agents = int((float(total_volume) / float(subset_volume)) * true_density)

            return self._generate_agents(num_agents, noisy)

        elif type(agents) == list:
            return agents
        elif type(agents) == int:
            return self._generate_agents(agents, noisy)
        else:
            raise RuntimeError('Expected agents to be of type list or int or None')

    def _generate_agents(self, num_agents, noisy=False):
        return [self._generate_agent(noisy) for i in range(num_agents)]

    def _generate_agent(self, noise=False):
        """
        Choose a generation function and return that agent.

        Dynamic agents appear ~twice as often as static agents
        """
        if noise:
            return random.choice([
                generate_circle_agent,
                generate_circle_agent,
                generate_circle_agent,
                # generate_static_circle_agent,
                # generate_big_static_circle,
            ])(self, True)
        else:
            return random.choice([
                generate_circle_agent,
                generate_circle_agent,
                generate_circle_agent,
                # generate_static_circle_agent,
                # generate_big_static_circle,
            ])(self)

    def _random_color(self):
        return (np.random.randint(256), np.random.randint(256), np.random.randint(256))

    def _handle_color(self, color):
        if color is None:
            return self._random_color()
        elif type(color) == str:
            return color
        elif type(color) == tuple:
            return color
        else:
            raise RuntimeError('Expected color to be of type str or tuple or None')

    def _generate_view(self, size=(400, 400)):
        cx,cy = (self.width // 2, self.height // 2)
        hx,hy = size[0] // 2, size[1] // 2
        return View(self, (cx - hx, cy - hy), (cx + hx, cy + hy))

def merge_list_of_tuples(l1, l2):
    max_len = max(len(l1), len(l2))

    while len(l1) < max_len:
        l1.append((0,0))
    while len(l2) < max_len:
        l2.append((0,0))

    to_ret = []

    for i in range(len(l1)):
        x1,y1 = l1[i]
        x2,y2 = l2[i]

        to_ret.append((x1 + x2, y1 + y2))

    return to_ret

class View:
    def __init__(self, world, tl, br, movement_queue=[]):
        """
            tl :: tuple of int :
                x,y coordinate of 
        """

        self.world = world
        self.tlx,self.tly = tl
        self.brx,self.bry = br

        self.move_queue = movement_queue

    def update(self):
        width = self.brx - self.tlx
        height = self.bry - self.tly

        if len(self.move_queue) > 0:
            dx,dy = self.move_queue.pop(0) # get the first instruction of the queue

            self.tlx += dx
            self.tly += dy
            self.brx += dx
            self.bry += dy

        if self.tlx < 0:
            self.tlx = 0
            self.brx = width

        if self.brx >= self.world.width:
            self.brx = self.world.width - 1
            self.tlx = self.world.width - 1 - width

        if self.tly < 0:
            self.tly = 0
            self.bry = height

        if self.bry >= self.world.height:
            self.bry = self.world.height - 1
            self.tly = self.world.height - 1 - height

        return View(self.world, (self.tlx, self.tly), (self.brx, self.bry), movement_queue=self.move_queue)

    def shake(self, timesteps, freq=1, mag=10, vertical=True, merge=False):
        return View(self.world, (self.tlx, self.tly), (self.brx, self.bry), movement_queue=self._shake(timesteps, freq, mag, vertical, merge))

    def _shake(self, timesteps, freq=1, mag=10, vertical=True, merge=False):
        """
            timesteps :: int :
                the number of timesteps to shake for
            freq :: int or float :
                the frequency of one full shake wave, 1 = full shake cycle after 2pi timesteps
            mag :: int or float :
                the magnitude of one full shake wave
            vertical :: bool :
                true if vertical shake, false if horizontal shake
            merge :: bool :
                if true, will merge these movements into existing movement_queue, else will append

            Returns the new movement queue.
        """
        to_ret = self.move_queue

        shake_queue = []

        for x in range(1, timesteps + 1):
            amt = int(mag * math.sin(freq * x))

            if vertical:
                shake_queue.append((0,amt))
            else:
                shake_queue.append((amt,0))

        if merge:
            to_ret = merge_list_of_tuples(to_ret, shake_queue)
        else:
            to_ret.extend(shake_queue)

        return to_ret

    def pan(self, timesteps, speed=2, vertical=True, merge=False):
        return View(self.world, (self.tlx, self.tly), (self.brx, self.bry), movement_queue=self._pan(timesteps, speed, vertical, merge))

    def _pan(self, timesteps, speed=2, vertical=True, merge=False):
        """
            timesteps :: int :
                the number of timesteps to pan for
            speed :: int or float :
                the speed at which the view will pan
            vertical :: bool :
                true if vertical pan, false if horizontal pan
            merge :: bool :
                if true, will merge these movements into existing movement_queue, else will append

            Returns the new movement queue.
        """

        to_ret = self.move_queue

        pan_queue = []

        for x in range(1, timesteps + 1):
            amt = x * speed

            if vertical:
                pan_queue.append((0, amt))
            else:
                pan_queue.append((amt,0))

        if merge:
            to_ret = merge_list_of_tuples(to_ret, pan_queue)
        else:
            to_ret.extend(pan_queue)

        return to_ret

    def contains(self, x, y):
        return x in range(self.tlx, self.brx) and y in range(self.tly, self.bry)




