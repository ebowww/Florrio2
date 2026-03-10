import pygame

class WorldMap:
    def __init__(self, screen_w, screen_h):
        # 3000x3000px Coordinate System (Requirement)
        self.width_px = 3000
        self.height_px = 3000
        self.grid_size = 50
        self.bg_color = (2, 230, 0)
        self.grid_color = (0,0, 0)

    def is_colliding(self, x, y, radius):
        """Simple boundary collision for the world edges."""
        if x - radius < 0 or x + radius > self.width_px:
            return True
        if y - radius < 0 or y + radius > self.height_px:
            return True
        return False

    def get_safe_spawn(self):
        """Returns the center of the world for spawning."""
        return self.width_px // 2, self.height_px // 2

    def draw(self, screen, camera_x, camera_y):
        screen.fill(self.bg_color)
        
        # Calculate grid range based on camera
        start_x = int(camera_x // self.grid_size) * self.grid_size
        start_y = int(camera_y // self.grid_size) * self.grid_size
        end_x = start_x + screen.get_width() + self.grid_size
        end_y = start_y + screen.get_height() + self.grid_size

        # Draw Vertical Lines
        for x in range(start_x, end_x, self.grid_size):
            pygame.draw.line(screen, self.grid_color, (x - camera_x, 0), (x - camera_x, screen.get_height()))
        
        # Draw Horizontal Lines
        for y in range(start_y, end_y, self.grid_size):
            pygame.draw.line(screen, self.grid_color, (0, y - camera_y), (screen.get_width(), y - camera_y))

    def draw_minimap(self, screen, player, mobs):
        """Restores the interactive minimap in the bottom right."""
        map_size = 150
        margin = 20
        # Position Rect
        map_rect = pygame.Rect(screen.get_width() - map_size - margin, 
                               screen.get_height() - map_size - margin, 
                               map_size, map_size)
        
        # Scale factors (Map Size / World Size)
        scale = map_size / self.width_px
        
        # Draw Map Base with Outlines
        pygame.draw.rect(screen, (0, 0, 0), map_rect.inflate(4, 4)) # Black Outline
        pygame.draw.rect(screen, (40, 40, 40), map_rect) # Dark Fill
        
        # Draw Bee dots (Red)
        for bee in mobs:
            bx = map_rect.x + int(bee.x * scale)
            by = map_rect.y + int(bee.y * scale)
            if map_rect.collidepoint(bx, by):
                pygame.draw.circle(screen, (255, 50, 50), (bx, by), 2)
        
        # Draw Player dot (White)
        px = map_rect.x + int(player.x * scale)
        py = map_rect.y + int(player.y * scale)
        pygame.draw.circle(screen, (255, 255, 255), (px, py), 3)