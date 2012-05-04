from random import randrange, uniform
from math import sin, cos, pi, pow, sqrt, atan2

from geometry import *

class Entity:
    def __init__(self, pos, v, r):
        self.pos = pos # position vector
        self.v = v # velocity vector (units/sec)
        self.r = r # rotation in radians, 0=down
        self.age = 0.0 # time elapsed
        self.rs = 0.0 # rotation speed (radians/sec)
        self.radius = 0.0 # radius (units)

    def update(self, millis):
        # update position
        v = (self.v[0] * (millis/1000.0), self.v[1] * (millis/1000.0))
        self.pos = (self.pos[0] + v[0], self.pos[1] + v[1])
        
        # update age
        self.age = self.age + millis
        
        # update rotation
        self.r = self.r + (self.rs * (millis/1000.0))
    
    def thrust(self, dv):
        # increase velocity by dv in direction of rotation
        v = (-dv*sin(self.r), dv*cos(self.r))
        self.v = (self.v[0] + v[0], self.v[1] + v[1])
    
    def rotate_relative(self, r):
        self.r = self.r + r
    
    # return entity from entity_list if this entity collides with it
    def check_collisions(self, entity_list):
        #for e in entity_list:
        #    if distance2d(self.pos, e.pos) < e.radius + self.radius:
        #        return e
        #return None
        (e, dist) = self.closest_entity(entity_list)
        if dist and dist < e.radius + self.radius:
            return e
        return None

    # return (entity, dist) tuple for distance of closest entity in list
    def closest_entity(self, entity_list):
        closest_dist = None
        closest_e = None
        for e in entity_list:
            dist = distance2d(self.pos, e.pos)
            if dist < closest_dist or not closest_dist:
                closest_dist = dist
                closest_e = e
        return (closest_e, closest_dist)
        

class World:
    def __init__(self):
        self.SPIN_SPEED = pi # radians per second
        self.PLAYER_ACCEL = 100.0 # units/second^2
        self.BULLET_SPEED = 100.0 # units/second
        self.BULLET_INTERVAL = 500 # millis
        self.BULLET_LIFE = 2000 # millis
        self.ROCK_MAX_RS = pi/4 # radians/sec
        self.SHIP_RADIUS = 25.0 # units
        self.ROCK_RADIUS = 20.0 # units
        self.ROCKS_NUMBER = 5
        self.ROCKS_SPREAD = 100 # units
        self.NEW_ROCKS_DIST = 500 # units
        self.EXPLOSION_LIFE = 1000 # millis
        
        self.last_bullet_time = 0
        self.rocks_center = (0,0) # center of current rocks
        
        self.l_down = False
        self.r_down = False
        self.u_down = False
        self.space_down = False
        
        player = Entity((0,0), (0,0), pi)
        player.radius = self.SHIP_RADIUS
        self.player = player
        self.entities = [self.player]
        self.bullets = []
        self.rocks = []
        self.explosions = []
        
        #self.create_rocks((0, 0))
    
    # return the (angle, entity) from the player to the closest rock
    def get_indicator_data(self):
        (e, dist) = self.player.closest_entity(self.rocks)
        if e:
            x = e.pos[0] - self.player.pos[0]
            y = e.pos[1] - self.player.pos[1]
            return (-1 * atan2(x, y), e)
        return (None, None)
    
    # create some new rocks
    def create_rocks(self, center):
        new_rocks = []
        for x in xrange(0, self.ROCKS_NUMBER):
            pos = (randrange(-1*self.ROCKS_SPREAD, self.ROCKS_SPREAD), randrange(-1*self.ROCKS_SPREAD, self.ROCKS_SPREAD))
            pos = translate2d([pos], center)[0]
            v = (randrange(-10, 10), randrange(-10, 10))
            r = uniform(0, 2*pi)
            rock = Entity(pos, v, r)
            rock.rs = uniform(-1*self.ROCK_MAX_RS, self.ROCK_MAX_RS)
            rock.radius = self.ROCK_RADIUS
            new_rocks.append(rock)
        self.entities = self.entities + new_rocks
        self.rocks = self.rocks + new_rocks
    
    def update(self, millis):
        # if there are no rocks, create some new ones
        if len(self.rocks) + len(self.explosions) == 0:
            # choose position away from player
            pos = scale2d([unit_vector(uniform(0, 2*pi))], self.NEW_ROCKS_DIST)[0]
            pos = translate2d([pos], self.player.pos)[0]
            self.create_rocks(pos)
            self.rocks_center = pos
        
        self.last_bullet_time = self.last_bullet_time + millis
        
        # handle key presses
        spin = self.SPIN_SPEED * (millis/1000.0)
        delta_v = self.PLAYER_ACCEL * (millis/1000.0)
        if self.l_down:
            self.player.rotate_relative(-1*spin)
        if self.r_down:
            self.player.rotate_relative(spin)
        if self.u_down:
            self.player.thrust(delta_v)
        if self.space_down:
            if self.last_bullet_time > self.BULLET_INTERVAL:
                # create bullet
                r = self.player.r
                v = unit_vector(r + pi)
                v = scale2d([v], self.BULLET_SPEED)[0]
                v = vec_sum(v, self.player.v) # add ship v to bullet v
                b = Entity(self.player.pos, v, r)
                self.entities.append(b)
                self.bullets.append(b)
                self.last_bullet_time = 0
        
        # update the grid entities
        for e in self.entities:
            e.update(millis)
        
        # remove expired bullets
        for b in self.bullets:
            if b.age > self.BULLET_LIFE:
                self.bullets.remove(b)
                self.entities.remove(b)
        
        # remove expired explosions
        for e in self.explosions:
            if e.age > self.EXPLOSION_LIFE:
                self.explosions.remove(e)
                self.entities.remove(e)
        
        # handle collisions
        # if player hits rock, remove rock
        e = self.player.check_collisions(self.rocks)
        if e:
            self.entities.remove(e)
            self.rocks.remove(e)
        # if bullet hits rock, remove rock and bullet, add explosion
        for b in self.bullets:
            r = b.check_collisions(self.rocks)
            if r:
                #self.entities.remove(r)
                self.explosions.append(r)
                self.rocks.remove(r)
                r.age = 0.0
                self.entities.remove(b)
                self.bullets.remove(b)
    
