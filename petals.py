import pygame
import math
import random

class DroppedPetal:
    def __init__(self, x, y, rarity, petal_type="Glass"):
        self.x, self.y = x, y
        self.rarity = rarity
        self.petal_type = petal_type
        self.radius = 12
        
        # Physics (Scatter/Explosion effect)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 5)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.friction = 0.92
        
        from mobs import Bee
        self.rarity_color = Bee.RARITY_COLORS.get(rarity, (255, 255, 255))
        self.inner_color = (255, 240, 150)
        self.font = pygame.font.SysFont("arial", 11, bold=True)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def draw(self, screen, camera_x, camera_y):
        float_y = math.sin(pygame.time.get_ticks() * 0.005) * 5
        sx, sy = int(self.x - camera_x), int(self.y - camera_y + float_y)
        
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        # Unique glow is usually more intense
        glow_alpha = 120 if self.rarity == "Unique" else 80
        pygame.draw.circle(glow_surf, (*self.rarity_color, glow_alpha), (30, 30), 25 if self.rarity == "Unique" else 22)
        screen.blit(glow_surf, (sx - 30, sy - 30))
        
        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.radius + 3)
        pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.radius + 1)
        pygame.draw.circle(screen, self.inner_color, (sx, sy), self.radius - 2)

        label_surf = self.font.render(self.petal_type, True, (255, 255, 255))
        label_rect = label_surf.get_rect(center=(sx, sy + self.radius + 15))
        shadow = self.font.render(self.petal_type, True, (0, 0, 0))
        screen.blit(shadow, (label_rect.x + 1, label_rect.y + 1))
        screen.blit(label_surf, label_rect)

class Petal:
    def __init__(self, player, angle=0, rarity="Common"):
        self.player = player
        self.size = 12
        self.angle = angle
        self.rarity = rarity
        
        from mobs import Bee
        self.rarity_color = Bee.RARITY_COLORS.get(self.rarity, (255, 255, 255))
        self.inner_color = (255, 240, 150)

        # --- Updated Damage Scaling including Unique ---
        multipliers = {
            "Common": 1.0, 
            "Rare": 1.5, 
            "Epic": 2.5, 
            "Legendary": 5.0, 
            "Mythic": 10.0, 
            "Ultra": 25.0, 
            "Super": 100.0,
            "Unique": 250.0  # Massive damage for the one-and-only
        }
        self.base_damage = 10
        self.damage = self.base_damage * multipliers.get(self.rarity, 1.0)
        
        self.base_radius = 65
        self.attack_radius = 160
        # Unique petals often have slightly more reach or speed
        if self.rarity == "Unique":
            self.attack_radius = 180 
            
        self.current_radius = self.base_radius
        self.active = True
        self.cooldown_timer = 0
        self.reload_time = 120 
        
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y, attacking, new_angle):
        self.angle = new_angle
        if not self.active:
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                self.active = True

        target_r = self.attack_radius if attacking else self.base_radius
        self.current_radius += (target_r - self.current_radius) * 0.12
        
        self.x = player_x + math.cos(self.angle) * self.current_radius
        self.y = player_y + math.sin(self.angle) * self.current_radius

    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return 
            
        sx, sy = int(self.x - camera_x), int(self.y - camera_y)
        
        # Draw Unique pulse effect
        if self.rarity == "Unique":
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 2
            pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.size + 3 + pulse, width=1)

        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.size + 3)
        pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.size + 1)
        pygame.draw.circle(screen, self.inner_color, (sx, sy), self.size - 2)

class PetalManager:
    def __init__(self, player, num_petals=5):
        self.player = player
        self.rotation_offset = 0
        self.petals = [Petal(player, angle=0, rarity="Common") for i in range(num_petals)]
        self.dropped_petals = []

    def spawn_dropped_petal(self, x, y, mob_rarity):
        roll = random.random() * 100
        # Unique is NOT in the drop table (it must be crafted)
        hierarchy = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        
        try:
            current_index = hierarchy.index(mob_rarity)
        except ValueError:
            current_index = 0

        if current_index > 0:
            petal_rarity = hierarchy[current_index] if roll < 30 else hierarchy[current_index - 1]
        else:
            petal_rarity = "Common"

        self.dropped_petals.append(DroppedPetal(x, y, petal_rarity))

    def update(self):
        self.rotation_offset += 0.06
        num = len(self.petals)
        for i, petal in enumerate(self.petals):
            slot_angle = (i * (2 * math.pi / num)) + self.rotation_offset
            petal.update(self.player.x, self.player.y, self.player.is_attacking, slot_angle)
            
        for dp in self.dropped_petals[:]:
            dp.update()
            dist = math.hypot(self.player.x - dp.x, self.player.y - dp.y)
            if dist < 45:
                # Inventory logic
                self.player.inventory[dp.rarity] = self.player.inventory.get(dp.rarity, 0) + 1
                self.dropped_petals.remove(dp)

    def draw(self, screen, camera_x, camera_y):
        for dp in self.dropped_petals:
            dp.draw(screen, camera_x, camera_y)
        for petal in self.petals:
            petal.draw(screen, camera_x, camera_y)