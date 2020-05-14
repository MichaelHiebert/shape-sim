from world import World
import cv2
import numpy as np

from generator import SimulationGenerator

if __name__ == "__main__":
    # # w = World(800, 800, agents=400, noisy=True)
    # # w = World(800, 800, agents=400, color='noise')
    # # w = World(800, 800, agents=400)
    # w = World(800, 800, agents=400, color='noise', noisy=True)

    # # w.view = w.view.shake(50)
    # # w.view = w.view.shake(50, mag=20, vertical=False, merge=True)
    # # w.view = w.view.pan(50)

    # img = np.zeros((400, 1202, 3), np.uint8)

    # img[:, 400, 0] = 128
    
    # while True:
    #     img[:, :400, :] = w.draw()
    #     img[:, 401:801, :] = w.draw_motion_mask()

    #     mp = w.draw_motion_map(16, 16)
    #     mp = 255 * np.repeat(mp[:, :, np.newaxis], 3, axis=2)
    #     img[:, 802:, :] = cv2.resize(mp, (400,400))

    #     cv2.imshow('world', img)
    #     cv2.waitKey(0)
    #     w.update()

    sg = SimulationGenerator()
    x,y = next(sg.generate(1, 15, (32,32), 3))
    img = np.zeros((400, 1202, 3), np.uint8)
    for i in range(x.shape[1]):
        img[:, :400, :] = x[0,i,:,:,:]
        img[:, 401:801, :] = x[1,i,:,:,:]
        img[:, 802:, :] = x[2,i,:,:,:]

        cv2.imshow('word', img)
        cv2.waitKey(0)
