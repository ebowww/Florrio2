import pygame
import math
import random

class Bee:
    # Color mapping for different rarities
    RARITY_COLORS = {
        "Common": (124, 239, 149),
        "Rare": (107, 178, 249),
        "Epic": (191, 131, 255),
        "Legendary": (255, 227, 85),
        "Mythic": (255, 105, 105),
        "Ultra": (255, 113, 229),
        "Super": (48, 48, 48),
        "Unique": (255, 255, 255) # Unique is pure white/glower": (255, 100, 150)     # Pink
    }

    def __init__(self, x, y, rarity="Common"):
        self.x, self.y = x, y
        self.radius = 18
        self.bob_offset = random.uniform(0, 5)
        self.rarity = rarity
        self.state = "idle"
        self.target = None

        # --- NEW: Exponential Power Scaling ---
        # Base stats for a Common Bee
        base_hp = 50
        base_dmg = 0.5  # damage per frame
        
        # Power multiplier per tier (Approx 3x-4x stronger each level)
        power_scales = {
            "Common": 1,
            "Rare": 4,
            "Epic": 15,
            "Legendary": 60,
            "Mythic": 250,
            "Ultra": 1000,
            "Super": 5000
        }
        
        mult = power_scales.get(rarity, 1)
        
        # Health scales heavily (Legendary now has 3,000 HP instead of 125)
        self.max_health = base_hp * mult
        self.health = self.max_health
        
        # Damage scales heavily (Legendary now deals 30 damage/frame!)
        self.damage = base_dmg * mult
        
        # Visual Size scaling (Still linear so they don't fill the whole screen)
        size_mults = {"Common": 1, "Rare": 1.3, "Epic": 1.6, "Legendary": 2.0, "Mythic": 2.5, "Ultra": 3.0, "Super": 3.5}
        self.radius = int(18 * size_mults.get(rarity, 1))
        
        # Speed: Higher rarities are slightly slower but not stationary
        self.speed = 3.2 * (1.0 / (1.0 + (mult * 0.001)))

    def take_damage(self, amount, source_player):
        self.health -= amount
        self.state = "chase"
        self.target = source_player

    def update(self, player, world_map, other_mobs):
        self.bob_offset += 0.1
        dx, dy = 0, 0
        if self.state == "chase" and self.target:
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            dx, dy = math.cos(angle)*self.speed, math.sin(angle)*self.speed

        # 1. World Boundary Collision
        if not world_map.is_colliding(self.x + dx, self.y, self.radius): self.x += dx
        if not world_map.is_colliding(self.x, self.y + dy, self.radius): self.y += dy

        # 2. Mob-to-Mob Collision (New: Prevents overlapping)
        for other in other_mobs:
            if other is self: continue
            dist = math.hypot(other.x - self.x, other.y - self.y)
            min_dist = self.radius + other.radius
            if dist < min_dist:
                # Push away from each other
                push_angle = math.atan2(self.y - other.y, self.x - other.x)
                overlap = min_dist - dist
                # Move slightly away (half the overlap each)
                move_x = math.cos(push_angle) * (overlap / 2)
                move_y = math.sin(push_angle) * (overlap / 2)
                
                if not world_map.is_colliding(self.x + move_x, self.y, self.radius): self.x += move_x
                if not world_map.is_colliding(self.x, self.y + move_y, self.radius): self.y += move_y

        # 3. Player Collision (Knockback logic)
        dist_p = math.hypot(player.x - self.x, player.y - self.y)
        if dist_p < (self.radius + player.radius):
            player.health -= self.damage
            push_angle = math.atan2(player.y - self.y, player.x - self.x)
            overlap = (self.radius + player.radius) - dist_p
            px, py = player.x + math.cos(push_angle)*overlap, player.y + math.sin(push_angle)*overlap
            if not world_map.is_colliding(px, py, player.radius):
                player.x, player.y = px, py

    def draw(self, screen, camera_x, camera_y):
        bob_y = int(math.sin(self.bob_offset) * 5)
        sx, sy = int(self.x - camera_x), int(self.y - camera_y) + bob_y
        
        # Wings
        pygame.draw.circle(screen, (200,230,255), (sx-12, sy-10), 8)
        pygame.draw.circle(screen, (200,230,255), (sx+12, sy-10), 8)
        
        # Body + Outline (Preserved Detail)
        pygame.draw.circle(screen, (40, 40, 40), (sx, sy), self.radius + 2) 
        pygame.draw.circle(screen, (255,220,0), (sx, sy), self.radius)
        
        # Stripes
        pygame.draw.rect(screen, (0,0,0), (sx-self.radius//2, sy-4, self.radius, 4))
        pygame.draw.rect(screen, (0,0,0), (sx-self.radius//2, sy+2, self.radius, 4))
        
        # Scaling Health Bar (Preserved Detail)
        bar_w = int(self.radius * 1.8)
        bar_h = 6
        bx, by = sx - bar_w // 2, sy + self.radius + 8
        pygame.draw.rect(screen, (40, 40, 40), (bx, by, bar_w, bar_h), border_radius=2)
        if self.health > 0:
            hp_w = int(bar_w * (self.health / self.max_health))
            pygame.draw.rect(screen, (100, 230, 100), (bx, by, hp_w, bar_h), border_radius=2)

        # Labels
        main_font = pygame.font.SysFont("arial", 22, bold=True)
        main_text = main_font.render("Bee", True, (0, 0, 0))
        screen.blit(main_text, main_text.get_rect(center=(sx, sy - self.radius - 20)))
        
        rarity_font = pygame.font.SysFont("arial", 16, bold=True)
        rarity_color = self.RARITY_COLORS.get(self.rarity, (255, 255, 255))
        rarity_text = rarity_font.render(self.rarity, True, rarity_color)
        screen.blit(rarity_text, rarity_text.get_rect(center=(sx, sy + self.radius + 28)))

import math
import random
from mobs import Bee

class MobManager:
    def __init__(self, world_map, num_bees=20, index_button=None):
        self.bees = []
        self.index_button = index_button
        self.spawn_mobs(world_map, num_bees)

    def spawn_mobs(self, world_map, b_count):
        rarities = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        for _ in range(b_count):
            rx, ry = random.randint(300, 2700), random.randint(300, 2700)
            # Weighted rarity distribution for spawning mobs
            rarity = random.choices(rarities, weights=[50, 30, 10, 5, 3, 2, 0.5])[0]
            if not world_map.is_colliding(rx, ry, 25):
                self.bees.append(Bee(rx, ry, rarity))

    def update(self, player, world_map, petal_manager):
        for b in self.bees[:]:
            b.update(player, world_map, self.bees)
            
            # Check collisions with player's equipped petals
            for p in petal_manager.petals: 
                # Check if petal is active and physically touching the bee
                if p.active and math.hypot(p.x - b.x, p.y - b.y) < (p.size + b.radius):
                    # --- SCALED DAMAGE LOGIC ---
                    # We use p.damage which is calculated in Petal.__init__ based on rarity
                    b.take_damage(p.damage, player)
                    
                    # Set petal to reload state after a hit
                    p.active = False
                    p.cooldown_timer = p.reload_time
                    
                    # Simple knockback effect: push mob away from the petal hit
                    angle = math.atan2(b.y - p.y, b.x - p.x)
                    b.x += math.cos(angle) * 15
                    b.y += math.sin(angle) * 15
            
            # Check if the mob has died
            if b.health <= 0:
                # Update the Mob Index/Bestiary if available
                if self.index_button:
                    self.index_button.increment(b.rarity, "Bee")
                
                # Spawn loot: Dropped Glass based on the mob's rarity
                petal_manager.spawn_dropped_petal(b.x, b.y, b.rarity)

                # Remove mob and award XP to the player
                self.bees.remove(b)
                # Weighted XP: higher rarity mobs give more XP
                xp_values = {"Common": 25, "Rare": 60, "Epic": 150, "Legendary": 500, 
                             "Mythic": 1200, "Ultra": 4000, "Super": 15000}
                player.gain_xp(xp_values.get(b.rarity, 25))
                
                # Respawn a new mob elsewhere to keep the world populated
                self.spawn_mobs(world_map, 1)

    def draw(self, screen, camera_x, camera_y):
        for b in self.bees: 
            b.draw(screen, camera_x, camera_y)