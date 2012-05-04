from sys import exit
from random import randrange, seed, uniform
from math import pow, sqrt, ceil, pi, atan2
import pygame

from simulator import *
from geometry import *
from interpolation import *

# constants
FPS = 60
TILE_SIZE = 128
NUM_STARS = 4
WIDTH = 800
HEIGHT = 600
INDICATOR_SIZE = 8

# return rock centered on 0,0 with num_verts vertices with avg radius radius
def draw_rock(num_verts, radius):
    step = 2*pi/num_verts
    v = []
    r_range = (radius - radius/2, radius + radius/2)
    for x in range(0, num_verts):
        a = step*x
        l = uniform(r_range[0], r_range[1])
        v = v + rotate2d([(0.0, l)], a)
    return v

# apply explosion effect to vert with given progress 0 to 1
# return lines of individual lines
def explode_rock(verts, progress, radius):
    lines = []
    # for every line
    for i in xrange(0, len(verts)):
        a = verts[i]
        b = verts[(i+1)%len(verts)]
        # find midpoint
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        # displace line based on midpoint and progress
        a = (a[0] + mid[0] * progress, a[1] + mid[1] * progress)
        b = (b[0] + mid[0] * progress, b[1] + mid[1] * progress)
        lines.append([a, b])
    return lines

# float-compatible range
def f_range(start, end, step):
    r = [start]
    while start < end:
        start = start + step
        r.append(start)
    return r[:-1]

# draw tile of stars on given surf at given position and size
def draw_star_tile(surf, sid, x, y, height, width, zoom):
    rect = pygame.Rect(x, y, height, width)
    white = (255, 255, 255, 100)
    gray = (50, 50, 50)
    seed(sid)
    for star in xrange(NUM_STARS):
        sx = randrange(x, x+width)
        sy = randrange(y, y+height)
        pygame.draw.circle(surf, (255,255,255), (sx,sy), int(round(2*zoom)))
    #pygame.draw.rect(surf, white, rect, 1)
    #pygame.draw.line(surf, gray, (x, y), (x+width, y+height), 1)
    #pygame.draw.line(surf, gray, (x+width, y), (x, y+height), 1)

class Camera:
    def __init__(self, surf, world):
        # pixel size
        self.width = WIDTH
        self.height = HEIGHT
        
        self.zoom = SmoothStepN(1.0, 250)
        
        # world grid position
        #self.top = 0.0
        #self.left = 0.0
        # world grid position (top, left)
        self.pos = SmoothStepN((0.0, 0.0), 2000)
        
        self.surf = surf
        
        self.world = world
        
        self.rocks = {}
        
        self.indicator_rot = RotationalSmoothStep1(0, 250)
        self.indicator_e = None
        
        # related to panning effect for new rocks
        self.last_rocks_center = (0,0)
        self.is_panned_back = True # whether both pan stages complete
        self.pause_sim = False
        self.first_update = True
    
    def update(self, millis):
    	# update indicator position
        # TODO: if rock position has changed at end of animation, there will be a jump, weighted mean is prob the way to go
        # if animation is finished
        if self.indicator_rot.is_finished():
            (theta, e) = self.world.get_indicator_data()
            if theta:
                if (e == self.indicator_e):
                    # same target as last time
                    self.indicator_rot.set_now(theta)
                else:
                    # target has changed
                    self.indicator_rot.set(theta)
                    self.indicator_e = e
            self.indicator_e = e
        self.indicator_rot.update(millis)
        
        self.zoom.update(millis)
        
        # hack so the first pan animation starts from the ship instead of 0,0
        if (self.first_update):
            self.first_update = False
            p_pos = self.grid_to_px(*self.world.player.pos)
            center_px = (p_pos[0] - self.width * 0.5, p_pos[1] - self.height * 0.5)
            self.pos.set_now(self.px_to_grid(*center_px))
        
        # check whether new rocks have been spawned
        if (self.world.rocks_center != self.last_rocks_center):
            self.last_rocks_center = self.world.rocks_center
            # pan the screen to the new rocks
            p_pos = self.grid_to_px(*self.last_rocks_center)
            center_px = (p_pos[0] - self.width * 0.5, p_pos[1] - self.height * 0.5)
            self.pos.set(self.px_to_grid(*center_px))
            self.is_panned_back = False
            self.pause_sim = True
        
        # center the camera on the player position
        if self.pos.is_finished():
            p_pos = self.grid_to_px(*self.world.player.pos)
            center_px = (p_pos[0] - self.width * 0.5, p_pos[1] - self.height * 0.5)
            if (not self.is_panned_back):
                self.pos.set(self.px_to_grid(*center_px))
                self.is_panned_back = True
            else:
                self.pos.set_now(self.px_to_grid(*center_px))
                self.pause_sim = False
        
        self.pos.update(millis)
    
    def draw(self):
        self.surf.fill((0, 0, 0))
        
        zts = TILE_SIZE * self.zoom.get() # zoomed tile size
        left, top = self.pos.get()
        
        grid_range_x = [left, left + self.width/self.zoom.get()]
        grid_range_y = [top, top + self.height/self.zoom.get()]
        first_tile = [int(grid_range_x[0])/TILE_SIZE*TILE_SIZE, int(grid_range_y[0])/TILE_SIZE*TILE_SIZE]
        last_tile = [int(grid_range_x[1])/TILE_SIZE*TILE_SIZE, int(grid_range_y[1])/TILE_SIZE*TILE_SIZE]
        rx = f_range(first_tile[0], last_tile[0]+1, TILE_SIZE)
        ry = f_range(first_tile[1], last_tile[1]+1, TILE_SIZE)
    
        drawn = 0
        for x in rx:
            for y in ry:
                p = self.grid_to_px(x, y)
                sid = str((x,y))
                # round to try and eliminate gaps
                draw_star_tile(self.surf, sid, round(p[0]), round(p[1]), ceil(zts), ceil(zts), self.zoom.get())
                drawn = drawn + 1
        #print "%i tiles visible" % drawn
        
        # draw rocks
        for e in self.world.rocks:
            pos = self.grid_to_px(e.pos[0], e.pos[1])
            pos = (int(pos[0]), int(pos[1]))
            if pos[0] > 0 and pos[0] < self.width and pos[1] > 0 and pos[1] < self.height:
                if e not in self.rocks:
                    self.rocks[e] = draw_rock(8, e.radius)
                verts = scale2d(self.rocks[e], self.zoom.get())
                verts = rotate2d(verts, e.r)
                verts = translate2d(verts, pos)
                pygame.draw.aalines(self.surf, (255,255,255), True, verts)
        
        # draw player
        pos = self.world.player.pos
        pos = self.grid_to_px(pos[0], pos[1])
        r = self.world.player.r
        # roughly derive shortest side of triangle from ship radius
        size = (self.world.player.radius * 2) * self.zoom.get()
        tri = [(-1*size/2,-1*size/2), (size/2,-1*size/2), (0,size)]
        tri = translate2d(rotate2d(tri, r), pos)
        pygame.draw.aalines(self.surf, (255,255,255), True, tri)
        
        # draw bullets
        for b in self.world.bullets:
            pos = self.grid_to_px(b.pos[0], b.pos[1])
            pos = (int(pos[0]), int(pos[1]))
            if pos[0] > 0 and pos[0] < self.width and pos[1] > 0 and pos[1] < self.height:
                verts = [(0, 0), (0, 10)]
                verts = rotate2d(verts, b.r)
                verts = translate2d(verts, pos)
                pygame.draw.aalines(self.surf, (255,255,255), True, verts)
        
        # draw explosions
        for e in self.world.explosions:
            pos = self.grid_to_px(e.pos[0], e.pos[1])
            pos = (int(pos[0]), int(pos[1]))
            if pos[0] > 0 and pos[0] < self.width and pos[1] > 0 and pos[1] < self.height:
                progress = e.age / self.world.EXPLOSION_LIFE
                c = 255 * (1-progress)
                verts = self.rocks[e] # assuming explosion previously a rock
                lines = explode_rock(verts, progress, e.radius)
                for line in lines:
                    line = scale2d(line, self.zoom.get())
                    line = rotate2d(line, e.r)
                    line = translate2d(line, pos)
                    #pygame.draw.aaline(self.surf, (c,c,c), True, verts)
                    pygame.draw.line(self.surf, (c,c,c), line[0], line[1])
        
        # draw indicator
        #theta = self.world.get_indicator_angle()
        theta = self.indicator_rot.get()
        # if the indicator has a target
        if self.indicator_e:
            pos = self.world.player.pos
            pos = self.grid_to_px(pos[0], pos[1])
            dist = self.world.player.radius * 2 * self.zoom.get()
            s = INDICATOR_SIZE * self.zoom.get()
            verts = [(-1*s, dist-s), (0, dist), (s, dist-s)]
            verts = rotate2d(verts, theta)
            verts = translate2d(verts, pos)
            pygame.draw.aalines(self.surf, (255,255,255), False, verts)
    
    # zoom relative to the current zoom
    def zoom_to(self, dz):
        # TODO: this should zoom in relative to current animation's destination
        if (not self.zoom.is_finished()):
            return
        # adjust zoom
        z = self.zoom.get() + dz
        if (z < 0.2):
            z = 0.2
        self.zoom.set(z)

    def grid_to_px(self, gx, gy):
        left, top = self.pos.get()
        return ((gx - left) * self.zoom.get(), (gy - top) * self.zoom.get())
    
    def px_to_grid(self, px, py):
        left, top = self.pos.get()
        return (left + (px / self.zoom.get()), top + (py / self.zoom.get()))

class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = (WIDTH, HEIGHT)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        
        self.world = World()
        self.camera = Camera(self.screen, self.world)
    
    def __do_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # up
                    self.camera.zoom_to(0.1)
                elif event.button == 5: # down
                    self.camera.zoom_to(-0.1)
            elif event.type == pygame.KEYDOWN:
                if event.key == 273: #up
                    self.world.u_down = True
                elif event.key == 274: #down
                    pass
                elif event.key == 275: #right
                    self.world.r_down = True
                elif event.key == 276: #left
                    self.world.l_down = True
                elif event.key == 32: # space
                    self.world.space_down = True
                else:
                    print event.key
            elif event.type == pygame.KEYUP:
                if event.key == 273: #up
                    self.world.u_down = False
                elif event.key == 274: #down
                    pass
                elif event.key == 275: #right
                    self.world.r_down = False
                elif event.key == 276: #left
                    self.world.l_down = False
                elif event.key == 32: # space
                    self.world.space_down = False
                else:
                    print event.key
    
    def __do_draw(self, elapsed):
        if (not self.camera.pause_sim):
            self.world.update(elapsed)
        self.camera.update(elapsed)
        self.camera.draw()
        pygame.display.flip()
    
    def main(self):
        now = 0
        show_fps = 0
        while True:
            elapsed = pygame.time.get_ticks() - now
            now = pygame.time.get_ticks()
            self.__do_draw(elapsed)
            self.__do_events()
            self.clock.tick(FPS)
            show_fps = show_fps + 1
            if (show_fps % FPS == 0):
                print self.clock.get_fps()

if __name__ == '__main__':
    game = Game()
    game.main()

