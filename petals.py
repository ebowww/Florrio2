import pygame
import math
import random

# ══════════════════════════════════════════════════════════════════
#  PETAL TYPE REGISTRY
# ══════════════════════════════════════════════════════════════════

RARITY_ORDER = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super", "Unique"]

PETAL_TYPES = {
    "Glass": {
        "display_name":    "Glass",
        "base_damage":     10.0,
        "counts":          [1, 1, 1, 1, 1, 1, 1, 1],
        "reload_base":     55,     # half of Light – fast reload
        "special":         None,
        "description":     "Standard petal. Fast reload.",
    },
    "Light": {
        "display_name":    "Light",
        "base_damage":     8.0,
        "counts":          [1, 1, 1, 2, 2, 2, 3, 3],
        "reload_base":     110,
        "special":         "Multi-petal",
        "description":     "Gains extra petals at higher rarities.",
    },
    "Bubble": {
        "display_name":    "Bubble",
        "base_damage":     0.0,
        "counts":          [1, 1, 1, 1, 1, 1, 1, 1],
        "reload_base":     180,
        "special":         "Dash",
        "description":     "Deals no damage. Right-click to dash forward.",
    },
    "Lightning": {
        "display_name":    "Lightning",
        "base_damage":     12.0,
        "counts":          [1, 1, 1, 1, 1, 1, 1, 1],
        "reload_base":     130,
        "special":         "Chain",
        "description":     "On hit, bounces to a nearby mob for 60% damage.",
    },
}

def petal_count(petal_type: str, rarity: str) -> int:
    pt  = PETAL_TYPES.get(petal_type, PETAL_TYPES["Glass"])
    idx = RARITY_ORDER.index(rarity) if rarity in RARITY_ORDER else 0
    return pt["counts"][idx]

def petal_base_damage(petal_type: str) -> float:
    return PETAL_TYPES.get(petal_type, PETAL_TYPES["Glass"])["base_damage"]

def petal_reload_base(petal_type: str) -> int:
    return PETAL_TYPES.get(petal_type, PETAL_TYPES["Glass"]).get("reload_base", 110)

def petal_special(petal_type: str):
    return PETAL_TYPES.get(petal_type, PETAL_TYPES["Glass"]).get("special")

def petal_description(petal_type: str) -> str:
    return PETAL_TYPES.get(petal_type, PETAL_TYPES["Glass"]).get("description", "")


# ══════════════════════════════════════════════════════════════════
#  DROPPED PETAL
# ══════════════════════════════════════════════════════════════════

class DroppedPetal:
    def __init__(self, x, y, rarity, petal_type="Glass"):
        self.x, self.y  = float(x), float(y)
        self.rarity     = rarity
        self.petal_type = petal_type
        self.radius     = 11

        angle      = random.uniform(0, math.pi * 2)
        speed      = random.uniform(2.5, 5.5)
        self.vx    = math.cos(angle) * speed
        self.vy    = math.sin(angle) * speed
        self.friction = 0.90

        from mobs import RARITY_COLORS
        self.rarity_color = RARITY_COLORS.get(rarity, (200, 200, 200))
        self.font         = pygame.font.SysFont("segoeui", 11, bold=True)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

    def draw(self, screen, cam_x, cam_y):
        t   = pygame.time.get_ticks() * 0.004
        bob = math.sin(t + self.x * 0.01) * 5
        sx  = int(self.x - cam_x)
        sy  = int(self.y - cam_y + bob)

        glow  = pygame.Surface((50, 50), pygame.SRCALPHA)
        alpha = 130 if self.rarity == "Unique" else 80
        gr    = 24 if self.rarity == "Unique" else 18
        pygame.draw.circle(glow, (*self.rarity_color, alpha), (25, 25), gr)
        screen.blit(glow, (sx - 25, sy - 25))

        if self.petal_type == "Bubble":
            bsurf = pygame.Surface((self.radius * 2 + 6, self.radius * 2 + 6), pygame.SRCALPHA)
            cx2, cy2 = self.radius + 3, self.radius + 3
            pygame.draw.circle(bsurf, (60, 65, 70, 160),     (cx2, cy2), self.radius + 2)
            pygame.draw.circle(bsurf, (150, 158, 165, 100),  (cx2, cy2), self.radius)
            pygame.draw.circle(bsurf, (*self.rarity_color, 140), (cx2, cy2), self.radius, 2)
            screen.blit(bsurf, (sx - self.radius - 3, sy - self.radius - 3))
        elif self.petal_type == "Lightning":
            # Blue electric circle
            pygame.draw.circle(screen, (30, 30, 60),       (sx, sy), self.radius + 2)
            pygame.draw.circle(screen, (80, 120, 220),     (sx, sy), self.radius)
            pygame.draw.circle(screen, (200, 220, 255),    (sx, sy), self.radius - 4)
            # Small zigzag spark
            t2 = pygame.time.get_ticks() * 0.01
            for i in range(3):
                a1 = t2 + i * (math.pi * 2 / 3)
                a2 = a1 + math.pi / 4
                x1 = sx + int(math.cos(a1) * (self.radius - 2))
                y1 = sy + int(math.sin(a1) * (self.radius - 2))
                x2 = sx + int(math.cos(a2) * (self.radius + 4))
                y2 = sy + int(math.sin(a2) * (self.radius + 4))
                pygame.draw.line(screen, (255, 255, 180), (x1, y1), (x2, y2), 1)
        elif self.petal_type == "Light":
            pygame.draw.circle(screen, (30, 30, 30),      (sx, sy), self.radius + 2)
            pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.radius + 1)
            pygame.draw.circle(screen, (240, 245, 255),   (sx, sy), self.radius - 1)
        else:  # Glass
            pygame.draw.circle(screen, (30, 30, 30),      (sx, sy), self.radius + 2)
            pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.radius)
            pygame.draw.circle(screen, (255, 245, 160),   (sx, sy), self.radius - 4)

        lbl  = self.font.render(self.petal_type, True, (255, 255, 255))
        shad = self.font.render(self.petal_type, True, (0, 0, 0))
        lr   = lbl.get_rect(center=(sx, sy + self.radius + 13))
        screen.blit(shad, (lr.x + 1, lr.y + 1))
        screen.blit(lbl,  lr)


# ══════════════════════════════════════════════════════════════════
#  PETAL  (one hotbar slot)
# ══════════════════════════════════════════════════════════════════

class Petal:
    _MULTIPLIERS = {
        "Common": 1.0, "Rare": 3.0, "Epic": 9.0, "Legendary": 18.0,
        "Mythic": 30.0, "Ultra": 90.0, "Super": 180.0, "Unique": 320.0,
    }
    _RELOAD_MULTIPLIERS = {
        "Common": 1.0, "Rare": 0.9, "Epic": 0.5, "Legendary": 0.3,
        "Mythic": 0.1, "Ultra": 0.03, "Super": 0.009, "Unique": 0.004,
    }

    def __init__(self, player, angle=0, rarity="Common", petal_type="Glass"):
        self.player     = player
        self.rarity     = rarity
        self.petal_type = petal_type
        self.angle      = float(angle)

        from mobs import RARITY_COLORS
        self.rarity_color = RARITY_COLORS.get(rarity, (200, 200, 200))

        self.base_damage = petal_base_damage(petal_type)
        self.damage      = self.base_damage * self._MULTIPLIERS.get(rarity, 1.0)
        self.count       = petal_count(petal_type, rarity)

        # Bubble and Light are slightly smaller
        self.size        = 9 if petal_type in ("Light", "Bubble") else \
                           10 if petal_type == "Lightning" else 12

        self.base_radius    = 65
        self.attack_radius  = 175 if rarity == "Unique" else 155
        self.current_radius = float(self.base_radius)

        self.active         = True
        self.cooldown_timer = 0
        base_frames         = petal_reload_base(petal_type)
        rarity_mult         = self._RELOAD_MULTIPLIERS.get(rarity, 1.0)
        self.reload_time    = max(4, int(base_frames * rarity_mult))

        self.sub_positions  = [(0.0, 0.0)] * self.count
        self.x              = 0.0
        self.y              = 0.0

        # Lightning bounce visual state
        self._bounce_flash  = None   # (sx,sy, tx,ty, timer) or None

    def update(self, player_x, player_y, attacking, slot_angle):
        self.angle = slot_angle

        if not self.active:
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                self.active = True

        target_r = self.attack_radius if attacking else self.base_radius
        self.current_radius += (target_r - self.current_radius) * 0.14

        spread = math.radians(22)
        offset = -(spread * (self.count - 1) / 2)
        self.sub_positions = []
        for i in range(self.count):
            a  = slot_angle + offset + i * spread
            x  = player_x + math.cos(a) * self.current_radius
            y  = player_y + math.sin(a) * self.current_radius
            self.sub_positions.append((x, y))

        self.x, self.y = self.sub_positions[0]

        # Tick bounce flash
        if self._bounce_flash is not None:
            lst = list(self._bounce_flash)
            lst[4] -= 1
            self._bounce_flash = tuple(lst) if lst[4] > 0 else None

    def draw(self, screen, cam_x, cam_y):
        # Lightning bounce arc
        if self._bounce_flash is not None:
            sx2, sy2, tx2, ty2, timer = self._bounce_flash
            alpha = min(255, timer * 20)
            lsurf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.line(lsurf, (180, 210, 255, alpha),
                             (sx2 - int(cam_x), sy2 - int(cam_y)),
                             (tx2 - int(cam_x), ty2 - int(cam_y)), 2)
            screen.blit(lsurf, (0, 0))

        if not self.active:
            return

        is_bubble    = (self.petal_type == "Bubble")
        is_light     = (self.petal_type == "Light")
        is_lightning = (self.petal_type == "Lightning")
        t = pygame.time.get_ticks()

        for (px, py) in self.sub_positions:
            sx, sy = int(px - cam_x), int(py - cam_y)

            if is_bubble:
                bsurf = pygame.Surface((self.size * 2 + 8, self.size * 2 + 8), pygame.SRCALPHA)
                cx2, cy2 = self.size + 4, self.size + 4
                pygame.draw.circle(bsurf, (55, 62, 68, 190),    (cx2, cy2), self.size + 2)
                pygame.draw.circle(bsurf, (145, 155, 162, 115), (cx2, cy2), self.size)
                pygame.draw.circle(bsurf, (*self.rarity_color, 150), (cx2, cy2), self.size, 2)
                pygame.draw.circle(bsurf, (215, 228, 238, 85),
                                   (cx2 - self.size // 3, cy2 - self.size // 3),
                                   max(2, self.size // 3))
                if self.rarity == "Unique":
                    pulse = int((math.sin(t * 0.008) + 1) * 3)
                    pygame.draw.circle(bsurf, (*self.rarity_color, 100),
                                       (cx2, cy2), self.size + 3 + pulse, 1)
                screen.blit(bsurf, (sx - self.size - 4, sy - self.size - 4))

            elif is_lightning:
                if self.rarity in ("Legendary", "Mythic", "Ultra", "Super", "Unique"):
                    gl = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(gl, (100, 150, 255, 65), (20, 20), 18)
                    screen.blit(gl, (sx - 20, sy - 20))
                if self.rarity == "Unique":
                    pulse = int((math.sin(t * 0.008) + 1) * 3)
                    pygame.draw.circle(screen, (160, 200, 255),
                                       (sx, sy), self.size + 4 + pulse, 1)
                # Blue body
                pygame.draw.circle(screen, (20, 25, 55),    (sx, sy), self.size + 3)
                pygame.draw.circle(screen, (70, 115, 210),  (sx, sy), self.size + 1)
                pygame.draw.circle(screen, (200, 220, 255), (sx, sy), self.size - 3)
                # Rotating spark lines
                t2 = t * 0.008
                for i in range(3):
                    a1 = t2 + i * (math.pi * 2 / 3)
                    a2 = a1 + math.pi / 5
                    x1 = sx + int(math.cos(a1) * (self.size - 1))
                    y1 = sy + int(math.sin(a1) * (self.size - 1))
                    x2 = sx + int(math.cos(a2) * (self.size + 4))
                    y2 = sy + int(math.sin(a2) * (self.size + 4))
                    pygame.draw.line(screen, (255, 255, 180), (x1, y1), (x2, y2), 1)

            elif is_light:
                if self.rarity == "Unique":
                    pulse = int((math.sin(t * 0.008) + 1) * 3)
                    pygame.draw.circle(screen, self.rarity_color,
                                       (sx, sy), self.size + 3 + pulse, 1)
                if self.rarity in ("Legendary", "Mythic", "Ultra", "Super", "Unique"):
                    gl = pygame.Surface((34, 34), pygame.SRCALPHA)
                    pygame.draw.circle(gl, (*self.rarity_color, 58), (17, 17), 15)
                    screen.blit(gl, (sx - 17, sy - 17))
                pygame.draw.circle(screen, (30, 30, 30),      (sx, sy), self.size + 2)
                pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.size + 1)
                pygame.draw.circle(screen, (240, 245, 255),   (sx, sy), self.size - 1)

            else:  # Glass
                if self.rarity == "Unique":
                    pulse = int((math.sin(t * 0.008) + 1) * 3)
                    pygame.draw.circle(screen, self.rarity_color,
                                       (sx, sy), self.size + 4 + pulse, 1)
                if self.rarity in ("Legendary", "Mythic", "Ultra", "Super", "Unique"):
                    gl = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(gl, (*self.rarity_color, 68), (20, 20), 18)
                    screen.blit(gl, (sx - 20, sy - 20))
                pygame.draw.circle(screen, (30, 30, 30),      (sx, sy), self.size + 3)
                pygame.draw.circle(screen, self.rarity_color, (sx, sy), self.size + 1)
                pygame.draw.circle(screen, (255, 245, 160),   (sx, sy), self.size - 3)

    def collides_with(self, mx, my, mob_radius) -> bool:
        for (px, py) in self.sub_positions:
            if math.hypot(px - mx, py - my) < self.size + mob_radius:
                return True
        return False

    def get_facing_angle(self) -> float:
        return self.angle


# ══════════════════════════════════════════════════════════════════
#  PETAL MANAGER
# ══════════════════════════════════════════════════════════════════

class PetalManager:
    DASH_SPEED    = 10.0
    DASH_DURATION = 10
    DASH_COOLDOWN = 1

    def __init__(self, player, num_petals=5):
        self.player          = player
        self.rotation_offset = 0.0
        self.petals          = [Petal(player, rarity="Common", petal_type="Glass")
                                 for _ in range(num_petals)]
        self.dropped_petals  = []
        self._dash_timer     = 0
        self._dash_cd        = 0
        self._dash_dx        = 0.0
        self._dash_dy        = 0.0

    def resize_slots(self, new_count: int):
        cur = len(self.petals)
        if new_count > cur:
            for _ in range(new_count - cur):
                self.petals.append(Petal(self.player, rarity="Common", petal_type="Glass"))
        elif new_count < cur:
            for p in self.petals[new_count:]:
                key = (p.petal_type, p.rarity)
                inv = self.player.inventory
                inv[key] = inv.get(key, 0) + 1
            self.petals = self.petals[:new_count]

    def try_bubble_dash(self):
        if self._dash_cd > 0:
            return
        total_dx = 0.0
        total_dy = 0.0
        found    = 0
        for p in self.petals:
            if p.petal_type == "Bubble" and p.active:
                angle     = p.get_facing_angle() + math.pi
                total_dx += math.cos(angle) * self.DASH_SPEED
                total_dy += math.sin(angle) * self.DASH_SPEED
                p.active         = False
                p.cooldown_timer = p.reload_time
                found += 1
        if found > 0:
            self._dash_dx    = total_dx
            self._dash_dy    = total_dy
            self._dash_timer = self.DASH_DURATION
            self._dash_cd    = self.DASH_COOLDOWN

    def spawn_dropped_petal(self, x, y, mob_rarity, petal_type="Glass"):
        hierarchy = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        try:
            idx = hierarchy.index(mob_rarity)
        except ValueError:
            idx = 0
        rarity = hierarchy[idx] if (idx > 0 and random.random() < 0.30) \
                 else hierarchy[max(0, idx - 1)] if idx > 0 \
                 else "Common"
        self.dropped_petals.append(DroppedPetal(x, y, rarity, petal_type))

    def update(self):
        self.rotation_offset += 0.055
        num = len(self.petals)
        for i, petal in enumerate(self.petals):
            slot_angle = (i * (2 * math.pi / num)) + self.rotation_offset
            petal.update(self.player.x, self.player.y,
                         self.player.is_attacking, slot_angle)

        if self._dash_timer > 0:
            self._dash_timer -= 1
            wm = self.player.world_map
            nx = self.player.x + self._dash_dx
            ny = self.player.y + self._dash_dy
            if wm and not wm.is_colliding(nx, self.player.y, self.player.radius):
                self.player.x = nx
            if wm and not wm.is_colliding(self.player.x, ny, self.player.radius):
                self.player.y = ny

        if self._dash_cd > 0:
            self._dash_cd -= 1

        for dp in self.dropped_petals[:]:
            dp.update()
            if math.hypot(self.player.x - dp.x, self.player.y - dp.y) < 48:
                key = (dp.petal_type, dp.rarity)
                self.player.inventory[key] = self.player.inventory.get(key, 0) + 1
                self.dropped_petals.remove(dp)

    def draw(self, screen, cam_x, cam_y):
        for dp in self.dropped_petals:
            dp.draw(screen, cam_x, cam_y)
        for petal in self.petals:
            petal.draw(screen, cam_x, cam_y)