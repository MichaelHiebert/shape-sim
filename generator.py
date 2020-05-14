import random
from world import World
import numpy as np

class SimulationGenerator:
    def __init__(self):
        pass

    def generate(self, num_batches, num_frames, output_size, vids_in_batch=5, world=(800,800), view=(400,400), num_agents=400, all_noisy=False):
        for batch in range(num_batches):
            batch_x = []
            batch_y = []
            for vid in range(vids_in_batch):
                # set up world
                if all_noisy:
                    w = World(*world, agents=num_agents, color='noise', noisy=True, view_size=view)
                else:
                    w = random.choice([
                        World(*world, agents=num_agents, noisy=True, view_size=view),
                        World(*world, agents=num_agents, color='noise', view_size=view),
                        World(*world, agents=num_agents, view_size=view),
                        World(*world, agents=num_agents, color='noise', noisy=True, view_size=view)
                    ])

                x = []
                y = []

                for frame in range(num_frames):
                    x.append(w.draw())
                    y.append(w.draw_motion_map(*output_size))

                    w.update()

                x = np.array(x)
                y = np.array(y)

                batch_x.append(x)
                batch_y.append(y)

            batch_x = np.array(batch_x)
            batch_y = np.array(batch_y)

            yield batch_x, batch_y
            