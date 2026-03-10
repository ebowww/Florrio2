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
        self.inner_color = (255, 240, 150) # The yellowish-white "Glass" color
        self.font = pygame.font.SysFont("arial", 11, bold=True)

    def update(self):
        # Apply the scatter movement
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def draw(self, screen, camera_x, camera_y):
        float_y = math.sin(pygame.time.get_ticks() * 0.005) * 5
        sx, sy = int(self.x - camera_x), int(self.y - camera_y + float_y)
        
        # 1. VISUAL PETAL
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.rarity_color, 80), (30, 30), 22)
        screen.blit(glow_surf, (sx - 30, sy - 30))
        
        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.radius + 3)
        pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.radius + 1)
        pygame.draw.circle(screen, self.inner_color, (sx, sy), self.radius - 2)

        # 2. THE LABEL ("Glass")
        label_surf = self.font.render("Glass", True, (255, 255, 255))
        label_rect = label_surf.get_rect(center=(sx, sy + self.radius + 15))
        shadow = self.font.render("Glass", True, (0, 0, 0))
        screen.blit(shadow, (label_rect.x + 1, label_rect.y + 1))
        screen.blit(label_surf, label_rect)




class Petal:
    def __init__(self, player, angle=0, rarity="Common"):
        self.player = player
        self.size = 12
        self.angle = angle  # This is now controlled by PetalManager
        self.rarity = rarity
        
        # Pull rarity color from the Bee class definitions
        from mobs import Bee
        self.rarity_color = Bee.RARITY_COLORS.get(self.rarity, (255, 255, 255))
        self.inner_color = (255, 240, 150) # The "Glass" face color

        # --- Damage Scaling ---
        multipliers = {
            "Common": 1.0, 
            "Rare": 1.5, 
            "Epic": 2.5, 
            "Legendary": 5.0, 
            "Mythic": 10.0, 
            "Ultra": 25.0, 
            "Super": 100.0
        }
        self.base_damage = 10
        self.damage = self.base_damage * multipliers.get(self.rarity, 1.0)
        
        # Range & Cooldown Stats
        self.base_radius = 65
        self.attack_radius = 160
        self.current_radius = self.base_radius
        
        self.active = True
        self.cooldown_timer = 0
        self.reload_time = 120 # Frames until petal reactivates
        
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y, attacking, new_angle):
        # Sync angle with the manager's master rotation
        self.angle = new_angle
        
        # Handle Cooldown
        if not self.active:
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                self.active = True

        # Stretching logic (Reach out when attacking)
        target_r = self.attack_radius if attacking else self.base_radius
        self.current_radius += (target_r - self.current_radius) * 0.12
        
        # Calculate world position based on current radius and angle
        self.x = player_x + math.cos(self.angle) * self.current_radius
        self.y = player_y + math.sin(self.angle) * self.current_radius

    def draw(self, screen, camera_x, camera_y):
        # Hide the petal while it is on cooldown
        if not self.active:
            return 
            
        sx, sy = int(self.x - camera_x), int(self.y - camera_y)
        
        # Orbiting Petal Visuals: Outer Outline -> Rarity Ring -> Glass Face
        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.size + 3) # Outline
        pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.size + 1) # Rarity Ring
        pygame.draw.circle(screen, self.inner_color, (sx, sy), self.size - 2) # Glass Center

class PetalManager:
    def __init__(self, player, num_petals=5):
        self.player = player
        self.rotation_offset = 0  # Global timer for the entire petal circle
        # Initialize with Common rarity by default
        self.petals = [Petal(player, angle=0, rarity="Common") for i in range(num_petals)]
        self.dropped_petals = []

    def spawn_dropped_petal(self, x, y, mob_rarity):
        roll = random.random() * 100
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
        # 1. Update the master rotation (controls all orbiting petals)
        self.rotation_offset += 0.06
        
        # 2. Update orbiting petals with synchronized alignment
        num = len(self.petals)
        for i, petal in enumerate(self.petals):
            # Calculate where this specific slot SHOULD be right now
            # Base slot angle + the master rotation offset
            slot_angle = (i * (2 * math.pi / num)) + self.rotation_offset
            petal.update(self.player.x, self.player.y, self.player.is_attacking, slot_angle)
            
        # 3. Update dropped loot and collection logic
        for dp in self.dropped_petals[:]:
            dp.update()
            
            # Distance check for collection
            dist = math.hypot(self.player.x - dp.x, self.player.y - dp.y)
            if dist < 45:
                # Add to player inventory
                self.player.inventory[dp.rarity] = self.player.inventory.get(dp.rarity, 0) + 1
                self.dropped_petals.remove(dp)

    def draw(self, screen, camera_x, camera_y):
        # Draw dropped petals FIRST so they stay behind orbiting petals
        for dp in self.dropped_petals:
            dp.draw(screen, camera_x, camera_y)
            
        # Draw orbiting petals
        for petal in self.petals:
            petal.draw(screen, camera_x, camera_y)