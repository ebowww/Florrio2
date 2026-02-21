import pygame
import math

class Petal:
    def __init__(self, angle=0):
        self.size = 8
        self.color = (255, 255, 255)
        self.angle = angle
        self.rotation_speed = 0.06 
        
        # Range & Cooldown Stats
        self.base_radius = 65
        self.attack_radius = 160
        self.current_radius = self.base_radius
        
        self.active = True
        self.cooldown_timer = 0
        self.reload_time = 120 # 2 seconds at 60 FPS
        
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y, attacking):
        self.angle += self.rotation_speed
        
        # Handle Cooldown
        if not self.active:
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                self.active = True

        # Stretching logic
        target_r = self.attack_radius if attacking else self.base_radius
        self.current_radius += (target_r - self.current_radius) * 0.12
        
        self.x = player_x + math.cos(self.angle) * self.current_radius
        self.y = player_y + math.sin(self.angle) * self.current_radius

    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return # Don't draw in world if reloading
            
        sx, sy = int(self.x - camera_x), int(self.y - camera_y)
        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.size + 2)
        pygame.draw.circle(screen, self.color, (sx, sy), self.size)

class PetalManager:
    def __init__(self, player, num_petals=5):
        self.player = player
        self.petals = [Petal(angle=(i * (2 * math.pi / num_petals))) for i in range(num_petals)]

    def update(self):
        for petal in self.petals:
            petal.update(self.player.x, self.player.y, self.player.is_attacking)

    def draw(self, screen, camera_x, camera_y):
        for petal in self.petals:
            petal.draw(screen, camera_x, camera_y)