import pygame
from sys import exit
import random

# easy_install noise
# use the pure-python implementation since it allows randomization
from noise import perlin


def add(col1, col2):
    """Return sum of two brighness values."""
    return col1 + col2 if col1 + col2 <= 1.0 else 1.0


def sub(col1, col2):
    """Return difference of two brightness values."""
    return col1 - col2 if col1 - col2 >= 0.0 else 0.0


def normalized_noise(noise_func, x_scale, y_scale, x, y):
    """Return a point of noise.
    
    noise_func should be instance of perlin.SimplexNoise
    """
    col = noise_func.noise2(x_scale * float(x), y_scale * float(y))
    col = int(col * 127 + 128)/255.0
    return col


def threshold(col, thresh):
    """Returns 1.0 for col > thresh, and 0.0 otherwise."""
    return 1.0 if col > thresh else 0.0


def v_gradient(y_start, y_end, x, y):
    """Return brightness at (x, y) of vertical gradient.
    
    y_start: point where brightness=1.0
    y_end: point where brightness=0.0
    """
    assert y_start > y_end # TODO: remove limitation
    if y > y_start:
        return 1.0
    elif y < y_end:
        return 0.0
    else:
        return float(y - y_end) / (y_start - y_end)


def generate_map(size):
    """Return list of block ids in row-major order."""
    blocks = []
    
    # tuneables
    HEIGHTMAP_X_SCALE = 0.04 # lower -> smoother terrian
    HEIGHTMAP_Y_SCALE = 0.04 # lower -> fewer overhangs and islands
    CAVE_SCALE = (0.1, 0.1)
    
    # create noise functions
    heightmap_noise = perlin.SimplexNoise(period=64)
    cave_noise = perlin.SimplexNoise(period=64)
    rock_noise = perlin.SimplexNoise(period=64)
    
    for y in xrange(size[1]):
        for x in xrange(size[0]):
            # ground heightmap
            g = v_gradient(40, 20, x, y)
            heightmap = normalized_noise(heightmap_noise, HEIGHTMAP_X_SCALE,
                                         HEIGHTMAP_Y_SCALE, x, y)
            g = threshold(g, heightmap)
            
            # caves, 1.0=cave
            caves = normalized_noise(cave_noise, CAVE_SCALE[0], CAVE_SCALE[1],
                                     x, y)
            cave_freq = 1 - v_gradient(80, -60, x, y) # most caves at bottom
            caves = add(caves, cave_freq)
            caves = threshold(caves, 0.5)
            
            comp = sub(g, sub(1, caves))
            
            # rocks
            rock = normalized_noise(rock_noise, 0.1, 0.1, x, y)
            rock_freq = 1 - v_gradient(80, -100, x, y)
            rock = add(rock, rock_freq)
            rock = threshold(rock, 0.3)
            
            if comp == 1:
                b = 1
                if rock == 0:
                    b = 2
            else:
                b = 0
            
            #blocks.append(int(comp))
            blocks.append(b)
    return blocks


def main():
    """Test program for generate_map()."""
    pygame.init()
    screen_size = (600,600) # pixels
    blocks_size = (100,100) # blocks
    screen = pygame.display.set_mode(screen_size)
    blocks = pygame.Surface(blocks_size)

    heightmap_noise = perlin.SimplexNoise(period=64)

    m = generate_map(blocks_size)

    cols = {0: (0, 0, 255), 1: (0, 255, 0), 2: (100, 100, 100)}

    for y in xrange(blocks_size[1]):
        for x in xrange(blocks_size[0]):
            raw = m[x + y*blocks_size[1]]
            col = cols[raw]
            blocks.set_at((x,y), col)
    
    blocks = pygame.transform.scale(blocks, screen_size)
    screen.blit(blocks, (0,0))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)


if __name__ == "__main__":
    main()

