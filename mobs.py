import pygame
import math
import random

class Bee:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 18
        self.health = 50
        self.max_health = 50
        self.speed = 3.2
        self.state = "idle"
        self.target = None
        self.bob_offset = random.uniform(0, 5)

    def take_damage(self, amount, source_player):
        self.health -= amount
        self.state = "chase"
        self.target = source_player

    def update(self, player, world_map, other_mobs):
        self.bob_offset += 0.1
        dx, dy = 0, 0
        if self.state == "chase" and self.target:
            angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            dx, dy = math.cos(angle) * self.speed, math.sin(angle) * self.speed
        
        # Wall/Mob Collision logic
        if not world_map.is_colliding(self.x + dx, self.y, self.radius): self.x += dx
        if not world_map.is_colliding(self.x, self.y + dy, self.radius): self.y += dy

        # Player Collision (Solid/Anti-Phasing)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < (self.radius + player.radius):
            player.health -= 0.5 
            push_angle = math.atan2(player.y - self.y, player.x - self.x)
            overlap = (self.radius + player.radius) - dist
            px, py = player.x + math.cos(push_angle) * overlap, player.y + math.sin(push_angle) * overlap
            if not world_map.is_colliding(px, py, player.radius):
                player.x, player.y = px, py

    def draw(self, screen, camera_x, camera_y):
        sx, sy = int(self.x - camera_x), int(self.y - camera_y) + int(math.sin(self.bob_offset)*5)
        # Bee visuals (Wing/Body/Outline)
        pygame.draw.circle(screen, (200, 230, 255), (sx-12, sy-10), 8)
        pygame.draw.circle(screen, (200, 230, 255), (sx+12, sy-10), 8)
        pygame.draw.circle(screen, (0, 0, 0), (sx, sy), self.radius + 2)
        pygame.draw.circle(screen, (255, 220, 0), (sx, sy), self.radius)
        if self.health < self.max_health:
            bar_w = 30
            pygame.draw.rect(screen, (0, 0, 0), (sx-16, sy+24, bar_w+2, 7)) # Bar Outline
            pygame.draw.rect(screen, (255, 50, 50), (sx-15, sy+25, bar_w * (self.health/50), 5))

class MobManager:
    def __init__(self, world_map, num_bees=20):
        self.bees = []
        self.spawn_mobs(world_map, num_bees)

    def spawn_mobs(self, world_map, b_count):
        for _ in range(b_count):
            rx, ry = random.randint(300, 2700), random.randint(300, 2700)
            if not world_map.is_colliding(rx, ry, 25): self.bees.append(Bee(rx, ry))

    def update(self, player, world_map, petals):
        for b in self.bees[:]:
            b.update(player, world_map, self.bees)
            for p in petals:
                if p.active and math.hypot(p.x-b.x, p.y-b.y) < (p.size+b.radius):
                    b.take_damage(10, player)
                    p.active, p.cooldown_timer = False, p.reload_time
            if b.health <= 0: self.bees.remove(b); player.gain_xp(25)

    def draw(self, screen, camera_x, camera_y):
        for b in self.bees: b.draw(screen, camera_x, camera_y)