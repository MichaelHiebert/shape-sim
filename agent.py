import numpy as np
import random

class Agent:
    def __init__(self, world, pos, vel, acc):
        """
            world :: World :
                the `World` object that this agent exists within
            pos :: tuple of int :
                the `x,y` coordinates of this object
            vel :: tuple of int :
                the `v_x, v_y` velocity vector of this object
            acc :: tuple of int :
                the `a_x, a_y` acceleration vector of this object
        """

        self.world = world
        self.pos = pos
        self.vel = vel
        self.acc = acc

    def update(self):
        """
            Update the acceleration, velocity, and position of this agent.
        """
        a_x,a_y = self.acc
        v_x,v_y = self.vel
        x,y     = self.pos

        a_x += self._acceleration_delta()
        a_y += self._acceleration_delta()

        v_x += a_x
        v_y = a_y

        x += v_x
        y += v_y

        self._keep_coordinates_in_bounds()
        self._handle_bounce()

        return Agent(self.world, (x,y), (v_x,v_y), (a_x, a_y))

    def _handle_bounce(self):
        x,y = self.pos
        v_x,v_y = self.vel
        a_x,a_y = self.acc

        if x in [0, self.world.width - 1]:
            v_x *= -1
            a_x *= -1
        
        if y in [0, self.world.height - 1]:
            v_y *= -1
            a_y *= -1

        self.vel = (v_x,v_y)
        self.acc = (a_x,a_y)

    def _keep_coordinates_in_bounds(self):
        x,y = self.pos

        if x < 0:
            x = 0
        
        if y < 0:
            y = 0

        if x > self.world.width - 1:
            x = self.world.width - 1

        if y > self.world.height - 1:
            y = self.world.height - 1

        self.pos = (x,y)

    def _acceleration_delta(self):
        direction = random.choice([-1, 0, 0, 0, 0, 1])
        magnitude = np.random.geometric(0.8) - 1

        return direction * magnitude

    def _digest(self):
        """
        Returns a tuple of the properties of this Agent like so:
            world, pos, vel, acc
        """

        return self.world, self.pos, self.vel, self.acc

    def _absorb_agent(self, other_agent):
        """Mutates this Agent to have the same properties as `other_agent`"""
        self.world, self.pos, self.vel, self.acc = other_agent._digest()

    def is_moving(self):
        v_x,v_y = self.vel
        a_x,a_y = self.acc

        return not (v_x == 0 and v_y == 0 and a_x == 0 and a_y == 0)

    def get_sector(self, view, height, width): # TODO does not support occlusion currently???
        """
            Given a height and a width, returns a tuple:
                (int((float(self.y) / float(self.height)) * height), 
                    int((float(self.x) / float(self.width))))
        """
        x,y = self.pos

        if view.contains(x, y) and self.is_moving():
            rel_x = x - view.tlx
            rel_y = y - view.tly

            return (
                int((float(rel_y) / float(view.bry - view.tly)) * height),
                int((float(rel_x) / float(view.brx - view.tlx)) * width)
            )
        else:
            return False
        

class VisualAgent(Agent):
    def __init__(self, agent, color=None):
        super(VisualAgent, self).__init__(*agent._digest())

        if color is None:
            self.color = self._random_color()
        else:
            self.color = color

    def _random_color(self):
        return (np.random.randint(256), np.random.randint(256), np.random.randint(256))

    def draw(self, image, color=None):
        raise NotImplementedError()

    def draw_motion_mask(self, image):
        if self.is_moving():
            return self.draw(image, color=(255,255,255))
        else:
            return image

    def draw_static_mask(self, image):
        if self.is_moving():
            return image
        else:
            return self.draw(image, color=(255,255,255))

# class StaticAgent(VisualAgent):
#     def __init__(self, agent, color=None):
#         super(StaticAgent, self).__init__(*agent.digest(), color=color)

#         self.v_x = 0
#         self.v_y = 0
#         self.a_x = 0
#         self.a_y = 0

#     def update(self):
#         return StaticAgent(Agent(self.world, self.pos, self.vel, self.acc), color=self.color)

        

        