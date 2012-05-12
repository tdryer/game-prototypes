from blocks import Block


def expand(blocks):
    """Return set of blocks resulting from "expanding" the given set of blocks.
    
    blocks: a list/set of (x, y) tuples.
    
    "Expanding" represents propagating the light by one step for every block
    given.
            X
     X --> XXX
            X
    """
    new_blocks = []
    for (x, y) in blocks:
        new_blocks += [(x, y), (x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return set(new_blocks)


def expand_n(pos, n):
    """Return the set of blocks affected by a light source at pos.
    
    n: the max light value.
    
    This works by calling expand on pos n times.
    """
    return reduce(lambda x, y: expand(x), xrange(n - 1), [pos])


class Light:
    """Computes and stores light levels for the map.
    
    The light level for every block in the map is stored at once, so if no 
    blocks are being changed the player can move around without any lighting
    updates.
    
    When a block is changed, every block whose light level could possibly
    change must be set to 0. Then the lighting for this local area must be 
    recomputed. This ensures light can be "cut off" from its source.
    
    The update is completed by propagating light for every block in the area,
    as well as for all blocks adjacent to the area.
    """
    MAX_LIGHT_LEVEL = 15
    
    def __init__(self, map_blocks):
        """Init light map for the given Map."""
        self.map_blocks = map_blocks
        self.map_size = map_blocks.size
        self.map_light = [0] * (self.map_size[0] * self.map_size[1])
        
        # compute light levels for whole map
        for x in xrange(0, self.map_size[0]):
            for y in xrange(0, self.map_size[1]):
                bid = self.map_blocks.get_block(x, y)
                if Block(bid).brightness > 0:
                    self.set_light(x, y, Block(bid).brightness)
                    self.propagate_light(x, y)
                
    def propagate_light(self, x, y):
        """Spread light from one block to its neighbors recursively."""
        level = self.get_light(x, y)
        adjacent = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        bid = self.map_blocks.get_block(x, y)
        opacity = Block(bid).opacity
        for (x, y) in adjacent:
            adj_level = self.get_light(x, y)
            if adj_level != None and adj_level < level - opacity:
                self.set_light(x, y, level - opacity)
                self.propagate_light(x, y)
    
    def update_light(self, x, y):
        """Update light in area surrounding a changed block at (x, y).
        
        Return a list of blocks whose light levels changed.
        """
        # clear all light in surrounding area
        area = expand_n((x, y), self.MAX_LIGHT_LEVEL)
        for (bx, by) in area:
            if self.get_light(bx, by) != None:
                self.set_light(bx, by, 0)
        
        # update light in area
        blocks = expand_n((x, y), self.MAX_LIGHT_LEVEL + 1)
        for (bx, by) in blocks:
            bid = self.map_blocks.get_block(bx, by)
            if bid != None:
                if Block(bid).brightness > 0:
                    self.set_light(bx, by, Block(bid).brightness)
                self.propagate_light(bx, by)
        
        return area
    
    def get_light(self, x, y):
        """Return light level at coordinates."""
        if (x in xrange(0, self.map_size[0]) and
                    y in xrange(0, self.map_size[1])):
            i = (y * self.map_size[1]) + x
            return self.map_light[i]
        else:
            return None
    
    def set_light(self, x, y, light_level):
        """Set light level at coordinates."""
        assert self.get_light(x, y) != None
        i = (y * self.map_size[1]) + x
        self.map_light[i] = light_level
        
