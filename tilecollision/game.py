import pygame
from random import uniform
from math import ceil, floor, sin, cos, atan2

import map_generation
import particles
from blocks import Block


class HUD:
    """The onscreen area for showing info. 
    
    For now it just shows the net number of blocks destroyed versus added.
    """
    def __init__(self, rect):
        """ Init the HUD.
        
        rect gives the area of the screen which will be drawn to.
        """
        self.rect = rect
        self.surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        self.font = pygame.font.Font(None, self.rect[3])
        
        self.BG_COL = (255, 255, 255, 200)
        self.BORDER_COL = (255, 255, 255, 128)
        self.BORDER = 5
        
        self.blocks = 0 # the number which is displayed
        
    def draw(self, surf):
        """Draw to the surface given."""
        self.surf.fill(self.BORDER_COL)
        pygame.draw.rect(self.surf, self.BG_COL, 
                         (self.BORDER, self.BORDER, 
                          self.rect[2]-self.BORDER*2, 
                          self.rect[3]-self.BORDER*2))
        font_surf = self.font.render(str(self.blocks), True, (0,0,0))
        self.surf.blit(font_surf, (self.BORDER,self.BORDER))
        surf.blit(self.surf, (self.rect[0], self.rect[1]))


class MapEntity:
    """Something that can be drawn on and collide with the map.
    
    For now there's player-specific code in here.
    """
    def __init__(self, x, y, w, h, dx, dy):
        """Create entity with given position, size, and velocity."""
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.dx = dx # block/sec
        self.dy = dy # block/sec
        
        self.is_falling = True # whether the entity is in the air
        
        self.grav_a = 5.0 # blocks/sec/sec
        self.max_fall = 10.0 # block/sec
        self.jump_v = -4.5 # block/sec
        self.walk_a = 6.0 # blocks/sec/sec
        self.max_walk = 6.0 # block/sec
        
        # actions entity can be trying to do
        self.walk_left = False
        self.walk_right = False
        self.jump = False
        
        self.normal_surf = pygame.image.load('player_normal.png')
        self.falling_surf = pygame.image.load('player_falling.png')
        
        self.fist_surf = pygame.image.load('fist.png')
        self.PUNCH_LENGTH = 250 # ms
        self.punch_time = self.PUNCH_LENGTH # ms
        self.punch_angle = 0 # degrees
        
    def get_rect(self):
        """Return collision box rect."""
        return (self.x, self.y, self.width, self.height)
    
    def punch(self, angle):
        """Activate the punch animation toward the given angle."""
        self.punch_time = 0
        self.punch_angle = angle
    
    def draw(self, px, py, pw, ph, surf):
        """Draw the entity.
        
        This is called by Map to draw this entity to the given location.
        """
        # draw fist animation
        if self.punch_time != self.PUNCH_LENGTH:
            prog = self.punch_time / self.PUNCH_LENGTH
            extension = 1 - pow(prog-0.5,2) * 4
            extension_length = extension * self.fist_surf.get_size()[1]
            ext_x = extension_length * sin((3.141/180)*self.punch_angle)
            ext_y = extension_length * cos((3.141/180)*self.punch_angle)
            surf_rot = pygame.transform.rotate(self.fist_surf, 
                                               180+self.punch_angle)
            fist_size = surf_rot.get_size()
            #TODO: center the fist properly
            surf.blit(surf_rot, (px + ext_x + pw/2 - fist_size[0]/2, 
                                 py + ext_y))
        
        # draw body
        e_surf = self.falling_surf if self.is_falling else self.normal_surf
        surf.blit(e_surf, (px, py))
    
    def rect_colliding(self, rect, map):
        """Return true if the given rect will collide with the given map.
        
        This works by finding all the map blocks inside the rect, and 
        returning true if any of them are solid blocks.
        
        rect should be a (x, y, w, h) tuple since pygame Rects don't use 
        floats.
        """
        # TODO: move this method to Map?
        r_x = rect[0]
        r_y = rect[1]
        r_w = rect[2]
        r_h = rect[3]
        # get range of blocks inside the given rect
        x_range = (int(r_x), int(ceil(r_x + r_w)))
        y_range = (int(r_y), int(ceil(r_y + r_h)))
        for x in xrange(x_range[0], x_range[1]):
            for y in xrange(y_range[0], y_range[1]):
                if map.is_solid_block(x, y):
                    return True
        return False
    
    def update(self, millis, map):
        """Update the physics of this entity and resolve collisions.
        
        This is where the guts of the collision resolution is. If the next
        position will cause a collision, then try moving only in the x or y
        component before giving up. If there is a collision, snap to the 
        next grid point in that direction.
        """
        # update punch animation
        self.punch_time += millis
        if self.punch_time > self.PUNCH_LENGTH:
            self.punch_time = self.PUNCH_LENGTH
        
        # apply gravity
        if (self.is_falling):
            self.dy += (self.grav_a * millis/1000)
            if (self.dy > self.max_fall):
                self.dy = self.max_fall
        else:
            self.dy = 0.01 # have to keep some small dy so we can start falling
        
        # apply jumping
        if (not self.is_falling and self.jump):
            self.dy = self.jump_v
            self.is_falling = True
        
        # apply walking
        if (self.walk_right and not self.walk_left):
            self.dx += (self.walk_a * millis/1000)
            if abs(self.dx) > self.max_walk:
                self.dx = self.max_walk
        elif (self.walk_left and not self.walk_right):
            self.dx -= (self.walk_a * millis/1000)
            if abs(self.dx) > self.max_walk:
                self.dx = -1 * self.max_walk
        else:
            self.dx = 0 # stop instantly?
        
        # new x and y components
        new_x = self.x + (self.dx * millis/1000)
        new_y = self.y + (self.dy * millis/1000)
        
        # next position using given next components
        next_xy = (new_x, new_y, self.width, self.height)
        next_y = (self.x, new_y, self.width, self.height)
        next_x = (new_x, self.y, self.width, self.height)
        
        y_increasing = (new_y > self.y) # entity is falling
        y_decreasing = (new_y < self.y) # entity is ascending
        y_collision = False
        y_snap_dir = 1 if y_increasing else -1
        x_snap_dir = 1 if (new_x > self.x) else -1
        
        if not self.rect_colliding(next_xy, map):
            # no collision, so move to next position
            self.x = new_x
            self.y = new_y
        else:
            # collision, so try moving in x or y only
            if not self.rect_colliding(next_x, map):
                # moving in x is fine
                self.x = new_x
                y_collision = True
                self.snap_edge_to_grid(0, y_snap_dir)
            elif not self.rect_colliding(next_y, map):
                # moving in y is fine
                self.y = new_y
                self.snap_edge_to_grid(x_snap_dir, 0)
            else:
                # can't move
                y_collision = True
                self.snap_edge_to_grid(x_snap_dir, y_snap_dir)
                
        if (y_increasing and not y_collision):
            self.is_falling = True
        if (y_increasing and y_collision):
            self.is_falling = False
        if (y_decreasing and y_collision):
            # bumped head, so loose vertical velocity
            self.dy = 0
    
    def snap_edge_to_grid(self, x_dir, y_dir):
        """Move this entity to snap the specified edges to the grid."""
        if x_dir == 1:
            # snap right edge of entity to grid line
            self.x += ceil(self.x + self.width) - (self.x + self.width)
        elif x_dir == -1:
            # snap left edge of entity to grid line
            self.x = floor(self.x)
        if y_dir == 1:
            # snap bottom edge of entity to grid line
            self.y += ceil(self.y + self.height) - (self.y + self.height)
        elif y_dir == -1:
            # snap top edge of entity to grid line
            self.y = floor(self.y)


class Map:
    """Stores map tile data, entity positions, and draws the map.
    
    The map is made of 1.0x1.0 blocks.
    
    The map is rendered in square chunks of blocks, which are cached as 
    surfaces to reduce the number of blits needed to draw the map. A chunk
    only needs to be redrawn when a block it contains is changed.
    """
    def __init__(self, size):
        """Create map of size*size tiles."""
        self.TILE_SIZE = 20 # pixels
        self.CHUNK_SIZE = 8 # blocks square
        
        self._blocks = [] # block_ids of the map in row-major order
        self.size = size # (width, height) of the map in blocks
        self.entities = [] # list of MapEntities in the map
        
        self._blocks = map_generation.generate_map(size)
        
        self._particle_systems = [] # (ParticleSystem, pos) tuples
        
        # prime the chunk cache by rendering every chunk in the map
        self._chunk_cache = {}
        print "priming chunk cache..."
        for chunk in self.get_chunks_in_rect(((0, 0) + self.size)):
            s = pygame.Surface((self.CHUNK_SIZE * self.TILE_SIZE, 
                                self.CHUNK_SIZE * self.TILE_SIZE))
            self.draw_chunk(s, chunk)
            self._chunk_cache[chunk] = s
        print "cached %i chunks" % len(self._chunk_cache)
    
    def get_block(self, x, y):
        """Return the block id at coordinates, or None if out of range."""
        if (x in xrange(0, self.size[0]) and y in xrange(0, self.size[1])):
            i = (y * self.size[1]) + x
            return self._blocks[i]
        else:
            return None
    
    def set_block(self, x, y, block_id):
        """Set the block at coordinates to block_id.
        
        Fails if block coords are out of range.
        """
        assert self.get_block(x, y) != None
        i = (y * self.size[1]) + x
        self._blocks[i] = block_id
        # invalidate the chunk cache
        cx = x / self.CHUNK_SIZE * self.CHUNK_SIZE
        cy = y / self.CHUNK_SIZE * self.CHUNK_SIZE
        if (cx, cy) in self._chunk_cache:
            del self._chunk_cache[(cx, cy)] # TODO: reuse surface?

    def is_solid_block(self, x, y):
        """Return True if block at given coordinates is solid. 
        
        Assumes blocks outside map are not solid.
        """
        block_id = self.get_block(x, y)
        return (block_id != None and Block(block_id).is_solid)

    def draw_chunk(self, surf, pos):
        """Draw a self.CHUNK_SIZE square of the map tiles.
        
        surf: Surface to draw to.
        pos: The top-left position of the map chunk to draw.
        """
        surf.fill((100, 100, 255))
        # figure out range of tiles in this chunk
        tile_range = [(int(pos[i]), 
                       int(ceil(pos[i] + surf.get_size()[i] / self.TILE_SIZE)))
                       for i in [0, 1]]
        tiles_drawn = 0
        for x in xrange(*(tile_range[0])):
            for y in xrange(*(tile_range[1])):
                if self.is_solid_block(x, y):
                    (px, py) = self.grid_to_px(pos, (x,y))
                    block_id = self.get_block(x, y)
                    block_surf = Block(block_id).surf
                    # center the surf on the collision rect
                    (sw, sh) = block_surf.get_size()
                    surf.blit(block_surf, (px-(sw - self.TILE_SIZE)/2, 
                              py-(sh - self.TILE_SIZE)/2))
                    tiles_drawn += 1

    def get_chunks_in_rect(self, rect):
        """Generate the list of chunks inside a rect."""
        x_min = rect[0]
        x_max = rect[0] + rect[2]
        y_min = rect[1]
        y_max = rect[1] + rect[3]
        chunks_x = (int(x_min) / self.CHUNK_SIZE * self.CHUNK_SIZE, 
                    int(x_max) / self.CHUNK_SIZE * self.CHUNK_SIZE)
        chunks_y = (int(y_min) / self.CHUNK_SIZE * self.CHUNK_SIZE, 
                    int(y_max) / self.CHUNK_SIZE * self.CHUNK_SIZE)
        # loop over every chunk and yield it
        for x in [c for c in xrange(chunks_x[0], chunks_x[1]+1) 
                  if c % self.CHUNK_SIZE == 0]:
            for y in [c for c in xrange(chunks_y[0], chunks_y[1]+1) 
                      if c % self.CHUNK_SIZE == 0]:
                yield (x, y)

    def draw(self, surf, pos):
        """Draw the map tiles and entites.
        
        surf: Surface to draw to.
        pos: Top-left grid position to draw.
        surf_size: 
        
        Note: negative chunks will causing rounding in the wrong direction, 
        causing undrawn margins. Fix this by not drawing empty chunks.
        """
        # figure out which chunks are onscreen
        # get topleft and bottomright grid positions of viewport
        topleft = pos
        bottomright = self.px_to_grid(pos, surf.get_size())
        # get min and max grid positions inside viewport
        x_min = topleft[0]
        x_max = bottomright[0]
        y_min = topleft[1]
        y_max = bottomright[1]
        # get min and max chunk positions inside viewport
        chunks_x = (int(x_min) / self.CHUNK_SIZE * self.CHUNK_SIZE, 
                    int(x_max) / self.CHUNK_SIZE * self.CHUNK_SIZE)
        chunks_y = (int(y_min) / self.CHUNK_SIZE * self.CHUNK_SIZE, 
                    int(y_max) / self.CHUNK_SIZE * self.CHUNK_SIZE)
        # loop over every chunk to draw
        for x in [c for c in xrange(chunks_x[0], chunks_x[1]+1) 
                  if c % self.CHUNK_SIZE == 0]:
            for y in [c for c in xrange(chunks_y[0], chunks_y[1]+1) 
                      if c % self.CHUNK_SIZE == 0]:
                # redraw the chunk if it's not cached
                if (x, y) not in self._chunk_cache:
                    print "chunk cache miss on %i,%i" % (x, y)
                    now = pygame.time.get_ticks()
                    # TODO: add margin to allow tile overlapping between chunks
                    s = pygame.Surface((self.CHUNK_SIZE * self.TILE_SIZE, 
                                        self.CHUNK_SIZE * self.TILE_SIZE))
                    self.draw_chunk(s, (x, y))
                    self._chunk_cache[(x, y)] = s
                    elapsed = pygame.time.get_ticks() - now
                    print "cached new chunk in %i ms" % elapsed
                surf.blit(self._chunk_cache[(x, y)], 
                          self.grid_to_px(pos, (x, y)))
        
        # figure out which entities are onscreen and draw them
        for entity in self.entities:
            topleft = (entity.x, entity.y)
            p_tl = self.grid_to_px(pos, topleft)
            # TODO: clip entities offscreen
            entity.draw(p_tl[0], p_tl[1], entity.width * self.TILE_SIZE,
                        entity.height * self.TILE_SIZE, surf=surf)
    
        # draw particle systems
        for ps_pos in self._particle_systems:
            (ps, g_pos) = ps_pos
            p_pos = self.grid_to_px(pos, g_pos)
            # TODO: clip
            ps.draw(surf, p_pos)
    
    def grid_to_px(self, topleft, pos):
        """Return pixel coordinate from a grid coordinate.
        
        topleft: top-left of map being drawn.
        pos: grid position to convert.
        """
        return ((pos[0] - topleft[0]) * self.TILE_SIZE, 
                (pos[1] - topleft[1]) * self.TILE_SIZE)

    def px_to_grid(self, topleft, pos):
        """Return grid coordinate from a pixel coordinate.
        
        topleft: top-left of map being drawn.
        pos: pixel position to convert.
        """
        return ((float(pos[0]) / self.TILE_SIZE) + topleft[0], 
                (float(pos[1]) / self.TILE_SIZE) + topleft[1])

    def update(self, millis):
        """Update all entities and particle systems in the map."""
        for entity in self.entities:
            entity.update(millis, self)
        for ps_pos in self._particle_systems:
            (ps, pos) = ps_pos
            ps.update(millis)
            if ps.is_expired():
                self._particle_systems.remove(ps_pos)


class Game:
    """Main class which handles input, drawing, and updating."""
    def __init__(self):
        """Init pygame and the map."""
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        self.MAP_SIZE = (100, 100)
        self.PLAYER_POS = (0.5, 0.5)
        self.PLAYER_SIZE = (1.5, 1.5)
        self.HUD_HEIGHT = 50
        
        pygame.init()
        pygame.font.init()
        self.screen_size = (self.WIDTH, self.HEIGHT)
        self.screen = pygame.display.set_mode(self.screen_size)
        
        self.clock = pygame.time.Clock()
        
        self.map = Map(self.MAP_SIZE)
        self.player = MapEntity(*(self.PLAYER_POS + self.PLAYER_SIZE + (0, 0)))
        self.map.entities.append(self.player)
        
        hud_rect = (0, self.screen_size[1] - self.HUD_HEIGHT, 
                    self.screen_size[0], self.HUD_HEIGHT)
        self.hud = HUD(hud_rect)
        
        self.blocks_collected = 0
        
        self.topleft = (0, 0) # reset to center on player
        
    def do_events(self):
        """Handle events from pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == 273: #up
                    self.player.jump = True
                elif event.key == 275: #right
                    self.player.walk_right = True
                elif event.key == 276: #left
                    self.player.walk_left = True
                elif event.key == 100: # d
                    print self.topleft
                else:
                    print event.key
            elif event.type == pygame.KEYUP:
                if event.key == 273: #up
                    self.player.jump = False
                elif event.key == 275: #right
                    self.player.walk_right = False
                elif event.key == 276: #left
                    self.player.walk_left = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # get coordinates and id of selected block
                    (gx, gy) = self.map.px_to_grid(self.topleft, event.pos)
                    (gx, gy) = (int(gx), int(gy))
                    block_id = self.map.get_block(gx, gy)
                    # swap the block's type
                    if block_id == Block(name="air").id:
                        # add block
                        self.map.set_block(gx, gy, Block(name="grass").id)
                        self.blocks_collected -= 1
                        self.hud.blocks -= 1
                    # allow solid blocks to be destroyed
                    elif Block(block_id).is_solid:
                        # remove block
                        self.map.set_block(gx, gy, Block(name="air").id)
                        self.blocks_collected += 1
                        self.hud.blocks += 1
                        surf = Block(block_id).surf
                        ps_pos = (particles.ParticleSystem(surf),
                                  (gx+0.5, gy+0.5))
                        self.map._particle_systems.append(ps_pos)
                        angle = atan2(gx - self.player.x, gy - self.player.y)
                        self.player.punch((180/3.141) * angle)
                      
    def do_update(self, elapsed):
        """Update the game state."""
        self.map.update(elapsed)
    
    def do_draw(self):
        """Draw the game."""
        # fill bg red for now to show errors
        self.screen.fill((255, 0, 0))
        
        # calculate top left coordinates such that player is draw on map center
        self.topleft = (self.player.x - self.WIDTH / 2 / self.map.TILE_SIZE,
                        self.player.y - self.HEIGHT / 2 / self.map.TILE_SIZE)
        # modify top left coordinates so viewport does not leave map
        max_x = self.MAP_SIZE[0] - self.WIDTH / self.map.TILE_SIZE
        max_y = self.MAP_SIZE[1] - self.HEIGHT / self.map.TILE_SIZE
        if self.topleft[0] < 0:
            self.topleft = (0, self.topleft[1])
        elif self.topleft[0] > max_x:
            self.topleft = (max_x, self.topleft[1])
        if self.topleft[1] < 0:
            self.topleft = (self.topleft[0], 0)
        elif self.topleft[1] > max_y:
            self.topleft = (self.topleft[0], max_y)
        
        self.map.draw(self.screen, self.topleft)
        self.hud.draw(self.screen)
        
        pygame.display.flip()
    
    def main(self):
        """Run the main loop.
        
        The game state updates on a fixed timestep. The update method may be
        called a varying number of times to catch up to the current time.
        """
        now = 0
        show_fps = 0
        update_time = 0
        UPDATE_STEP = 1000/60.0 # 60 Hz
        
        # main loop
        while True:
            elapsed = pygame.time.get_ticks() - now
            now = pygame.time.get_ticks()
            
            # update as many times as needed to catch up to the current time
            while (now - (update_time + UPDATE_STEP) >= 0):
                update_time += UPDATE_STEP
                self.do_update(UPDATE_STEP)
            
            # draw and check events
            self.do_draw()
            self.do_events()
            
            # wait until it's time for next frame
            self.clock.tick(self.FPS)
            show_fps = show_fps + 1
            if (show_fps % self.FPS == 0):
                print self.clock.get_fps()

if __name__ == '__main__':
    game = Game()
    game.main()
