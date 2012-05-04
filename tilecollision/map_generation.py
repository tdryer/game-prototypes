import pygame
from sys import exit
import random

# easy_install noise
# use the pure-python implementation since it allows randomization
from noise import perlin
simplex = perlin.SimplexNoise(period=512)

# noise resolution
x_size = 0.1
y_size = 0.1


def generate(map_size):
    """Return a new map.
    
    map_size: (x,y) number of blocks in map.
    
    Returns list of integers giving map in row-major order.
    """
    blocks = [] # block data in row-major order
    for y in xrange(map_size[1]):
        for x in xrange(map_size[0]):
            col = simplex.noise2(x_size * float(x), y_size * float(y))
            
            # normalise the output to 0-255 (not sure about this)
            col = int(col * 127 + 128)

            # apply gradient
            # use relative heights with top=1
            start = 1.0 # above this is pure white
            end = 0.8 # below this if untouched
            pos = 1 - (float(y) / map_size[1])
            if pos > start:
                col = 255
            elif pos < end:
                pass
            else:
                added = (pos - end) / (start - end)
                added *= 255
                col += added
                if col > 255:
                    col = 255
            
            # apply threshold
            threshold = 160 # higher -> more black
            if col > threshold:
                col = 255
            else:
                col = 0
            
            blocks.append(col)
    return blocks


def main():
    """Test program for generate()."""
    pygame.init()
    screen_size = (600,600)
    blocks_size = (100,100)
    screen = pygame.display.set_mode(screen_size)
    blocks = pygame.Surface(blocks_size)

    # get block data
    block_data = generate(blocks_size)
    
    # convert block data to pixels
    for y in xrange(blocks_size[1]):
        for x in xrange(blocks_size[0]):
            col = block_data[y*blocks_size[1]+x]
            blocks.set_at((x,y), (col,col,col))
    
    blocks = pygame.transform.scale(blocks, screen_size)
    screen.blit(blocks, (0,0))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)


if __name__ == "__main__":
    main()

