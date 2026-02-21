import pygame
import math

class Player:
    def __init__(self, start_x, start_y, world_map=None, radius=20, color=(255, 255, 0)):
        self.x = start_x
        self.y = start_y
        self.radius = radius
        self.color = color
        
        # Stats Progression
        self.level = 1
        self.xp = 0
        self.speed = 4.5
        self.max_health = 100
        self.health = 100
        self.regen_rate = 0.05
        
        # Attack & Tank State
        self.is_attacking = False
        self.tank_type = "basic" # Level 5 choice: 'twin' or 'flank'

    def gain_xp(self, amount):
        """Adds XP and handles leveling logic."""
        self.xp += amount
        # Requirement: Weighted XP / Leveling
        if self.xp >= 100:
            self.xp -= 100
            self.level += 1
            # Scale health with level as per progression requirements
            self.max_health += 10
            self.health = self.max_health 

    def handle_input(self, events):
        """Processes mouse clicks for attack range stretching."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_attacking = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_attacking = False

    def handle_movement(self, keys, world_map, mouse_follow=False, camera=(0, 0)):
        dx, dy = 0, 0

        if mouse_follow:
            mx, my = pygame.mouse.get_pos()
            target_x = mx + camera[0]
            target_y = my + camera[1]
            
            dist = math.hypot(target_x - self.x, target_y - self.y)
            if dist > 5:
                angle = math.atan2(target_y - self.y, target_x - self.x)
                dx = math.cos(angle) * self.speed
                dy = math.sin(angle) * self.speed
        else:
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            
            if dx != 0 or dy != 0:
                length = math.hypot(dx, dy)
                dx = (dx / length) * self.speed
                dy = (dy / length) * self.speed

        # Sliding Physics (Circular Collision)
        new_x = self.x + dx
        if not world_map.is_colliding(new_x, self.y, self.radius):
            if 0 + self.radius < new_x < world_map.width_px - self.radius:
                self.x = new_x
        
        new_y = self.y + dy
        if not world_map.is_colliding(self.x, new_y, self.radius):
            if 0 + self.radius < new_y < world_map.height_px - self.radius:
                self.y = new_y

    def update(self):
        # Out-of-combat regeneration logic
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + self.regen_rate)

    def draw(self, screen, camera_x, camera_y):
        sx, sy = int(self.x - camera_x), int(self.y - camera_y)
        
        # Player Body + Outline
        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.radius + 3)
        pygame.draw.circle(screen, self.color, (sx, sy), self.radius)
        
        # Dual Health Bar (BG and FG)
        bar_w, bar_h = 50, 8
        bx, by = sx - bar_w // 2, sy + self.radius + 12
        pygame.draw.rect(screen, (50, 50, 50), (bx, by, bar_w, bar_h), border_radius=2)
        if self.health > 0:
            hp_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(screen, (100, 230, 100), (bx, by, hp_w, bar_h), border_radius=2)