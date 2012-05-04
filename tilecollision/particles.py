import pygame
from sys import exit
from random import uniform, randrange


class Particle:
    """Data structure for one particle."""
    def __init__(self, x, y, dx, dy, max_age, surf_rect):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.age = 0
        self.max_age = max_age
        self.surf_rect = surf_rect


class ParticleSystem:
    """A source of particles."""
    def __init__(self):
        """Init and set parameters.
        
        Parameters are currently hard-coded here for the block-break effect.
        """
        self.duration = 250 # ms
        self.spawn_rate = 0.1 # particles/ms
        self.gravity = 100.0 # units/sec/sec
        self.source_surf = pygame.image.load('grass.png')
        self.surf_size = self.source_surf.get_size()
        self.size = 5
        self.v_range = (-80, 80)
        self.life_range = (100, 1000) # ms
        
        self.age = 0
        self.particles = []
        
    def is_expired(self):
        """Return true if expired."""
        return (self.age > self.duration) and (len(self.particles) == 0)
    
    def update(self, millis):
        """Update particle positions and spawn new particles."""
        # update particle positions
        for p in self.particles:
            if p.age > p.max_age:
                self.particles.remove(p)
            else:
                p.dy += self.gravity * millis/1000
                p.x += p.dx * millis/1000
                p.y += p.dy * millis/1000
                p.age += millis
        
        # spawn new particles
        self.age += millis
        if self.age < self.duration:
            num_new = int(self.spawn_rate * millis)
            for i in xrange(num_new):
                surf_rect = (randrange(0, self.surf_size[0] - self.size),
                             randrange(0, self.surf_size[1] - self.size))
                p = Particle(0.0, 0.0, uniform(*self.v_range), 
                             uniform(*self.v_range), 
                             uniform(*self.life_range), surf_rect)
                self.particles.append(p)

    def draw(self, surf, pos):
        """Draw the particles to surf centered at pos."""
        for p in self.particles:
            rect = (p.x + pos[0], p.y + pos[1], self.size, self.size)
            surf.blit(self.source_surf, rect, (p.surf_rect[0], p.surf_rect[1],
                                               self.size, self.size))


def main():
    """Test program for ParticleSystem()."""
    pygame.init()
    screen_size = (600,600)
    screen = pygame.display.set_mode(screen_size)
    
    s2 = pygame.Surface(screen_size, pygame.SRCALPHA)
    ps = ParticleSystem()

    while True:
        
        # draw
        s2.fill((0,0,0))
        ps.update(16)
        ps.draw(s2, (300,300))
        
        screen.blit(s2, (0,0))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)


if __name__ == "__main__":
    main()

