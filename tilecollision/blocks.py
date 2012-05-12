import pygame

class Block:
    """Class to provide info about block ID as attributes.
    
    The first time it is imported, this module will load the surfaces.
    """
    l = pygame.image.load
    #       block_id  name     solid  surf             brightness opacity
    info = {0:       ("air",   False, None,            0,          1),
            1:       ("grass", True,  l("grass.png"),  0,          5),
            2:       ("rock",  True,  l("rock.png"),   15,         1),
           }
    # derive name->id dict
    names = {}
    for bid in info:
        names[info[bid][0]] = bid
    print names
    print "loaded block surfaces"
    
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
        self.surf = bi[2]
        self.brightness = bi[3]
        self.opacity = bi[4]

if __name__ == "__main__":
    print Block(0).name
    print Block(bid=0).name
    print Block(name="air").name
    print Block(bid=0, name="air").name # should be ValueError
    
