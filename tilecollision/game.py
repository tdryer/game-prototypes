import pygame
from random import uniform, randrange
from math import ceil, floor, sin, cos, atan2, sqrt, pow

import map_generation
import particles
from blocks import Block
from hud import HUD
from light import Light

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
        
        if not map.rect_colliding(next_xy):
            # no collision, so move to next position
            self.x = new_x
            self.y = new_y
        else:
            # collision, so try moving in x or y only
            if not map.rect_colliding(next_x):
                # moving in x is fine
                self.x = new_x
                y_collision = True
                self.snap_edge_to_grid(0, y_snap_dir)
            elif not map.rect_colliding(next_y):
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
        self.BLOCK_UPDATE_SIZE = (40, 40) # rect size around player in blocks
        self.BLOCK_UPDATE_FREQ = 1000 # number of blocks to update per second
        
        self._blocks = [] # block_ids of the map in row-major order
        self.size = size # (width, height) of the map in blocks
        self.entities = [] # list of MapEntities in the map
        
        self._blocks = map_generation.generate_map(size)
        
        self._particle_systems = [] # (ParticleSystem, pos) tuples
        
        self.cursor_pos = None # pixel coords or None
        
        self.light = Light(self)
        
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
        
        # update lighting and invalidate changed chunks
        # for every block with changed lighting, invalidate its chunk
        changed_blocks = self.light.update_light(x, y)
        for block in changed_blocks:
            cx = block[0] / self.CHUNK_SIZE * self.CHUNK_SIZE
            cy = block[1] / self.CHUNK_SIZE * self.CHUNK_SIZE
            if (cx, cy) in self._chunk_cache:
                del self._chunk_cache[(cx, cy)]

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
        for x in xrange(*(tile_range[0])):
            for y in xrange(*(tile_range[1])):
                (px, py) = self.grid_to_px(pos, (x,y))
                bid = self.get_block(x, y)
                if bid != None:
                    block = Block(bid)
                    light_level = self.light.get_light(x, y)
                    block_surf = block.lit_surfs[light_level]
                    surf.blit(block_surf, (px, py))
                else:
                    pass #FIXME

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
                # rounding pos and blit_pos seems to fix edges between chunks
                blit_pos = self.grid_to_px((round(pos[0], 2), 
                                            round(pos[1], 2)), (x, y))
                blit_pos = (round(blit_pos[0]), round(blit_pos[1]))
                surf.blit(self._chunk_cache[(x, y)], 
                          blit_pos)
        
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
        
        # draw selected block
        if self.cursor_pos != None:
            selected_block = self.px_to_grid(pos, self.cursor_pos)
            selected_block = (int(selected_block[0]), int(selected_block[1]))
            rect = (self.grid_to_px(pos, selected_block) +
                    (self.TILE_SIZE, self.TILE_SIZE))
            pygame.draw.rect(surf, (255, 0, 0), rect, 2)
        
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
        """Update entities, particle systems, and blocks in the map.
        
        Blocks are updated in a rectangle around the player. Random blocks in
        this rectangle are chosen to be updated each call.
        """
        for entity in self.entities:
            entity.update(millis, self)
        
        for ps_pos in self._particle_systems:
            (ps, pos) = ps_pos
            ps.update(millis)
            if ps.is_expired():
                self._particle_systems.remove(ps_pos)
        
        # TODO: hack to get player pos
        update_center = (int(self.entities[0].x), int(self.entities[0].y))
        # loop so updates occur at specified frequency
        for i in xrange(int(ceil(millis /
                                 float(self.BLOCK_UPDATE_FREQ * 1000)))):
            x = randrange(update_center[0] - self.BLOCK_UPDATE_SIZE[0]/2, 
                          update_center[0] + self.BLOCK_UPDATE_SIZE[0]/2 + 1)
            y = randrange(update_center[1] - self.BLOCK_UPDATE_SIZE[1]/2, 
                          update_center[1] + self.BLOCK_UPDATE_SIZE[1]/2 + 1)
            # update block at (x, y)
            bid = self.get_block(x, y)
            if bid == Block(name="grass").id:
                
                # kill grass which is too dark
                if self.light.get_light(x, y) < self.light.MAX_LIGHT_LEVEL:
                    self.set_block(x, y, Block(name="dirt").id)
                
                # spread grass to adjacent blocks which are bright enough
                for pos in [(x-1,y),(x+1,y),(x,y-1),(x,y+1),(x-1,y-1),
                            (x+1,y+1),(x-1,y+1),(x+1,y-1)]:
                    if (self.light.get_light(*pos) == self.light.MAX_LIGHT_LEVEL 
                            and self.get_block(*pos) == Block(name="dirt").id):
                        self.set_block(pos[0], pos[1], Block(name="grass").id)

    def rect_colliding(self, rect, assume_solid=None):
        """Return true if the given rect will collide with the map.
        
        This works by finding all the map blocks inside the rect, and 
        returning true if any of them are solid blocks.
        
        rect should be a (x, y, w, h) tuple since pygame Rects don't use 
        floats.
        
        If assume_solid is an (x, y) tuple, that block will be assumed solid.
        """
        r_x = rect[0]
        r_y = rect[1]
        r_w = rect[2]
        r_h = rect[3]
        # get range of blocks inside the given rect
        x_range = (int(r_x), int(ceil(r_x + r_w)))
        y_range = (int(r_y), int(ceil(r_y + r_h)))
        for x in xrange(x_range[0], x_range[1]):
            for y in xrange(y_range[0], y_range[1]):
                if self.is_solid_block(x, y) or (x, y) == assume_solid:
                    return True
        return False


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
        self.PLAYER_REACH = 4
        self.HUD_HEIGHT = 50
        
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("tilecollision prototype")
        self.screen_size = (self.WIDTH, self.HEIGHT)
        self.screen = pygame.display.set_mode(self.screen_size)
        
        self.clock = pygame.time.Clock()
        
        self.map = Map(self.MAP_SIZE)
        self.player = MapEntity(*(self.PLAYER_POS + self.PLAYER_SIZE + (0, 0)))
        self.map.entities.append(self.player)
        
        hud_rect = (0, self.screen_size[1] - self.HUD_HEIGHT, 
                    self.screen_size[0], self.HUD_HEIGHT)
        self.hud = HUD(hud_rect)
        
        self.topleft = (0, 0) # reset to center on player
        
        self.mouse_pos = (0, 0)
        
    def do_events(self):
        """Handle events from pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == 119: # w
                    self.player.jump = True
                elif event.key == 100: # d
                    self.player.walk_right = True
                elif event.key == 97: # a
                    self.player.walk_left = True
                else:
                    print event.key
            elif event.type == pygame.KEYUP:
                if event.key == 119: # w
                    self.player.jump = False
                elif event.key == 100: # d
                    self.player.walk_right = False
                elif event.key == 97: # a
                    self.player.walk_left = False
            elif event.type == pygame.MOUSEMOTION:
                # save mouse pos to compute map cursor each frame
                self.mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # if mouse is in valid location to place/destory block
                    if self.map.cursor_pos:
                        (gx, gy) = self.map.px_to_grid(self.topleft,
                                                       self.map.cursor_pos)
                        (gx, gy) = (int(gx), int(gy))
                        block_id = self.map.get_block(gx, gy)
                        if Block(block_id).is_solid:
                            # remove block
                            self.map.set_block(gx, gy, Block(name="air").id)
                            self.hud.add_block(block_id)
                            surf = Block(block_id).surf
                            ps_pos = (particles.ParticleSystem(surf),
                                      (gx+0.5, gy+0.5))
                            self.map._particle_systems.append(ps_pos)
                            angle = atan2(gx - self.player.x, gy -
                                          self.player.y)
                            self.player.punch((180/3.141) * angle)
                        else:
                            # add block
                            new_block = self.hud.get_selected_block()
                            self.map.set_block(gx, gy, new_block)
                elif event.button == 4: # wheel up
                    self.hud.rotate_selection(-1)
                elif event.button == 5: # wheel down
                    self.hud.rotate_selection(1)
                

    def do_update(self, elapsed):
        """Update the game state."""
        self.map.update(elapsed)
        
        # update the cursor
        # find grid distance from center of block under the mouse to
        # player's center
        (gx, gy) = self.map.px_to_grid(self.topleft, self.mouse_pos)
        (gx, gy) = (int(gx), int(gy))
        dist = sqrt(pow(gx + 0.5 - self.player.x - self.player.width/2, 2) +
                    pow(gy + 0.5 - self.player.y - self.player.height/2, 2))
        # only show cursor if close enough and block doesn't collide
        if dist > self.PLAYER_REACH:
            self.map.cursor_pos = None
        elif self.map.rect_colliding(self.player.get_rect(), (gx, gy)):
            self.map.cursor_pos = None
        else:
            self.map.cursor_pos = self.mouse_pos
    
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
