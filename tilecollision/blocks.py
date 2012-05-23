import pygame

# TODO: this also exists in light.py
MAX_LIGHT_LEVEL = 15

def adjust_surf_brightness(surf, light_level, max_level):
    """Return copy of surf dimmed to given light level."""
    alpha = int(255 * (1 - light_level / float(max_level)))
    surf = surf.copy()
    shade_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    (width, height) = shade_surf.get_size()
    pygame.draw.rect(shade_surf, (0, 0, 0, alpha), (0, 0, width, height))
    surf.blit(shade_surf, (0, 0))
    return surf


class Block:
    """Class to provide info about block ID as attributes.
    
    The first time it is imported, this module will load the surfaces.
    """
    # shortcut to load light-level-index array of block surfaces
    def l(surf_filename):
        surf = pygame.image.load(surf_filename)
        lit_surfs = []
        for light_level in xrange(MAX_LIGHT_LEVEL + 1):
            lit_surfs.append(adjust_surf_brightness(surf, light_level,
                             MAX_LIGHT_LEVEL))
        return lit_surfs
    
    print "loading block surfaces..."
    #       block_id  name     solid  surf             brightness opacity
    info = {0:       ("air",   False, l("air.png"),    0,          1),
            1:       ("grass", True,  l("grass.png"),  0,          5),
            2:       ("rock",  True,  l("rock.png"),   0,          5),
            3:       ("lamp",  True,  l("lamp.png"),   15,         1),
            4:       ("dirt",  True,  l("dirt.png"),   0,          5),
           }
    # derive name->id dict
    names = {}
    for bid in info:
        names[info[bid][0]] = bid
    
    def __init__(self, bid=-1, name=""):
        """Init properties of the given block type."""
        if bid != -1 and name == "":
            self.id = bid
        elif bid == -1 and name != "":
            self.id = self.names[name]
        else:
            raise ValueError, "Only one of bid and name may be set."
            
        
        bi = self.info[self.id]
        
        self.name = bi[0]
        self.is_solid = bi[1]
        self.surf = bi[2][MAX_LIGHT_LEVEL]
        self.lit_surfs = bi[2]
        self.brightness = bi[3]
        self.opacity = bi[4]


if __name__ == "__main__":
    print Block(0).name
    print Block(bid=0).name
    print Block(name="air").name
    print Block(bid=0, name="air").name # should be ValueError
    
