from blocks import Block

class Light:
    """Computes and stores light levels for the map.
    
    The light level for every block in the map is stored at once, so if no 
    blocks are being changed the player can move around without any lighting
    updates.
    
    When a block is changed, every block whose light level could possibly
    change must be set to 0. Then the lighting for this local area must be 
    recomputed. This ensures light can be "cut off" from its source.
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
                if Block(bid).name == "rock":
                    self.set_light(x, y, 15)
                    self.propagate_light(x, y)
                
    def propagate_light(self, x, y):
        """Spread light from one block to its neighbors recursively."""
        level = self.get_light(x, y)
        adjacent = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        for (x, y) in adjacent:
            adj_level = self.get_light(x, y)
            if adj_level != None and adj_level < level - 1:
                self.set_light(x, y, level - 1)
                self.propagate_light(x, y)
    
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
        
