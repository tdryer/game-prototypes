import pygame, collections
from math import pi
from geometry import *
FPS = 60

class AccelerationInterpolator:
    def __init__(self):
        self.pos = 1.0
        self.dest = 1.0
        self.v = 0.0
        self.a = 5000.0
        self.max_v = 5000.0
    
    def update(self, millis):
        # if animating
        if self.pos != self.dest:
            # set acceleration direction
            if self.pos < self.dest:
                da = self.a
            else:
                da = -1 * self.a
            # update velocity and position
            self.v = self.v + (da * millis/1000)
            self.pos = self.pos + (self.v * millis/1000)
            if self.pos > self.dest: #TODO: doesn't work in both directions
                self.pos = self.dest
                self.v = 0

# smoothstep for float or N-tuple of float values
class SmoothStepN:
    def __init__(self, initial_val, anim_length):
        self._pos = initial_val
        self._start = initial_val
        self._dest = initial_val
        self._anim_time = 0.0
        self._anim_length = float(anim_length)
    
    def get(self):
        return self._pos
    
    def set(self, dest):
        self._start = self._pos
        self._anim_time = 0.0
        self._dest = dest
    
    def set_now(self, dest):
        self._anim_time = 0.0
        self._dest = dest
        self._start = dest
        self._pos = dest
        assert(self.is_finished()) # catch looping bugs
    
    def is_finished(self):
        return self._start == self._dest
    
    def update(self, millis):
        if self._start != self._dest:
            self._anim_time = self._anim_time + millis
            if self._anim_time >= self._anim_length:
                self._anim_time = 0.0
                self._pos = self._dest
                self._start = self._dest
            step = self._anim_time / self._anim_length
            step = step * step * (3 - 2 * step) # smoothstep
            comp = []
            # handle N=1 and N>1
            if isinstance(self._pos, collections.Iterable):
                for i in range(0, len(self._pos)):
                    comp.append(self._dest[i] * step + self._start[i] * (1-step))
                self._pos = tuple(comp)
            else:
                self._pos = self._dest * step + self._start * (1-step)

# wrapper to make SmoothStepN appropriate for rotational interpolation
class RotationalSmoothStep1(SmoothStepN):
    def set(self, dest):
        diff = abs(dest - self._pos)
        if (diff > pi):
            if (dest > self._pos):
                self._pos = self._pos + 2*pi
            else:
                dest = dest + 2*pi
        SmoothStepN.set(self, dest)

class WAInterp:
    def __init__(self):
        self.pos = (0.0, 0.0)
        self.dest = (0.0, 0.0)
        self.slowness = 16
    
    def update(self, millis):
        # problem: frame rate dependent
        p = []
        for i in range(0, len(self.pos)):
            p.append(((self.pos[i] * (self.slowness-1)) + self.dest[i]) / self.slowness)
        self.pos = tuple(p)

class InterpTest:
    def __init__(self):
        pygame.init()
        self.screen_size = (800, 600)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        
        self.r = pygame.Rect(0, 0, 100, 100)
        #self.interp = SSInterp2D()
        #self.interp = WAInterp()
        self.pos = SmoothStepN((0,0), 250)
        
        test = SmoothStepN(0, 250)
        test.set(1)
        #print test.get()
        test.update(100)
        #print test.get()
        test.update(150)
        #print test.get()
        
        self.rot = RotationalSmoothStep1(pi/4, 250)
    
    def __do_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left
                    #self.interp.start = self.interp.pos
                    #self.interp.anim_time = 0
                    #self.interp.dest = (event.pos[0]-50,event.pos[1]-50)
                    self.pos.set((event.pos[0]-50,event.pos[1]-50))
                    
                    self.rot.set(0)
                elif event.button == 3: # right
                    self.rot.set(pi+0.1)
                elif event.button == 4: # up
                    pass
                elif event.button == 5: # down
                    pass
    
    def __do_draw(self, elapsed):
        self.screen.fill((0, 0, 0))
        self.pos.update(elapsed)
        self.r.left = self.pos.get()[0]
        self.r.top = self.pos.get()[1]
        pygame.draw.rect(self.screen, (255,255,255), self.r, 1)
        
        self.rot.update(elapsed)
        line = [(0,0), (0,1)]
        line = rotate2d(line, self.rot.get())
        line = scale2d(line, 100)
        line = translate2d(line, (400, 300))
        pygame.draw.aalines(self.screen, (255,255,255), False, line)
        
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
    game = InterpTest()
    game.main()

