import pygame

from blocks import Block

class HUD:
    """The onscreen area for showing info. 
    
    This shows a horizontal list of blocks with the number of each block that
    the player has broken.
    """
    def __init__(self, rect):
        """ Init the HUD.
        
        rect gives the area of the screen which will be drawn to.
        """
        self.rect = rect
        self.font = pygame.font.Font(None, self.rect[3]/2)
        
        self.inv_items = [1, 2, 3] # order of items in bar
        self.inv_count = {1: 0, 2: 0, 3: 0} # block id -> count
        self.selected_cell = 0 # index of selected cell
        
    def draw(self, surf):
        """Draw to the surface given."""
        cell_size = self.rect[3]
        curr_x = 0
        for (i, block) in enumerate(self.inv_items):
            # draw cell background
            cell_rect = (curr_x, self.rect[1], cell_size, cell_size)
            pygame.draw.rect(surf, (0, 0, 0), cell_rect)
            curr_x += cell_size
            
            # draw highlight for selected cell
            if self.selected_cell == i:
                pygame.draw.rect(surf, (255, 0, 0), cell_rect, 2)
            
            # draw block in center of cell_rect
            block_surf = Block(block).surf
            surf.blit(block_surf, 
                       (cell_rect[0] + cell_size/2 - 
                        block_surf.get_size()[0]/2,
                        cell_rect[1] + cell_size/2 - 
                        block_surf.get_size()[1]/2))
            # draw count
            count = self.inv_count[block]
            font_surf = self.font.render(str(count), True, (255, 255, 255))
            surf.blit(font_surf, cell_rect)

    def add_block(self, block_id):
        """Add a block to the inventory."""
        self.inv_count[block_id] += 1
    
    def rotate_selection(self, direction):
        """Change the current selection by direction."""
        self.selected_cell = (self.selected_cell + 
                              direction) % len(self.inv_items)

    def get_selected_block(self):
        """Return currently selected block ID."""
        return self.inv_items[self.selected_cell]

