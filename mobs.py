import pygame
import math
import random

# ══════════════════════════════════════════════════════════════════
#  SHARED RARITY COLOURS
# ══════════════════════════════════════════════════════════════════

RARITY_COLORS = {
    "Common":    (124, 239, 149),
    "Rare":      (107, 178, 249),
    "Epic":      (191, 131, 255),
    "Legendary": (255, 227,  85),
    "Mythic":    (255, 105, 105),
    "Ultra":     (255, 113, 229),
    "Super":     ( 48,  48,  48),
    "Unique":    (255, 255, 255),
}

_POWER = {
    "Common": 1, "Rare": 4, "Epic": 15, "Legendary": 60,
    "Mythic": 250, "Ultra": 1000, "Super": 5000,
}
_SIZE_MULT = {
    "Common": 1.0, "Rare": 1.3, "Epic": 1.6, "Legendary": 2.0,
    "Mythic": 2.5, "Ultra": 3.0, "Super": 3.5,
}
_XP = {
    "Common": 25, "Rare": 60, "Epic": 150, "Legendary": 500,
    "Mythic": 1200, "Ultra": 4000, "Super": 15000,
}

# ══════════════════════════════════════════════════════════════════
#  SHARED MOB BASE
# ══════════════════════════════════════════════════════════════════

class _MobBase:
    def _move(self, world_map, dx, dy):
        if not world_map.is_colliding(self.x + dx, self.y, self.radius):
            self.x += dx
        if not world_map.is_colliding(self.x, self.y + dy, self.radius):
            self.y += dy

    def _separate(self, all_mobs, world_map):
        for other in all_mobs:
            if other is self:
                continue
            dist = math.hypot(other.x - self.x, other.y - self.y)
            md   = self.radius + other.radius
            if 0 < dist < md:
                push = math.atan2(self.y - other.y, self.x - other.x)
                half = (md - dist) * 0.5
                mx2  = math.cos(push) * half
                my2  = math.sin(push) * half
                if not world_map.is_colliding(self.x + mx2, self.y, self.radius):
                    self.x += mx2
                if not world_map.is_colliding(self.x, self.y + my2, self.radius):
                    self.y += my2

    def _contact_player(self, player, world_map):
        dp = math.hypot(player.x - self.x, player.y - self.y)
        if dp < self.radius + player.radius:
            if self.damage > 0:
                player.health -= self.damage
            self.health -= getattr(player, "body_damage", 0)
            push = math.atan2(player.y - self.y, player.x - self.x)
            ovlp = (self.radius + player.radius) - dp
            nx   = player.x + math.cos(push) * ovlp
            ny   = player.y + math.sin(push) * ovlp
            if not world_map.is_colliding(nx, ny, player.radius):
                player.x, player.y = nx, ny

    def _draw_hp_bar(self, screen, sx, sy):
        r  = self.radius
        bw = int(r * 1.8);  bh = 5
        bx = sx - bw // 2;  by = sy + r + 7
        pygame.draw.rect(screen, (35, 35, 35), (bx, by, bw, bh), border_radius=2)
        if self.health > 0:
            ratio = max(0.0, self.health / self.max_health)
            hp_w  = int(bw * ratio)
            bc    = (80, 220, 90) if ratio > 0.5 \
                    else (230, 180, 40) if ratio > 0.25 else (220, 60, 60)
            pygame.draw.rect(screen, bc, (bx, by, hp_w, bh), border_radius=2)


# ══════════════════════════════════════════════════════════════════
#  BEE  (Garden)
# ══════════════════════════════════════════════════════════════════

class Bee(_MobBase):
    RARITY_COLORS = RARITY_COLORS

    def __init__(self, x, y, rarity="Common"):
        self.x, self.y  = float(x), float(y)
        self.bob_offset  = random.uniform(0, math.pi * 2)
        self.rarity      = rarity
        self.state       = "idle"
        self.target      = None
        self.mob_type    = "Bee"

        mult            = _POWER.get(rarity, 1)
        self.max_health = 50 * mult
        self.health     = float(self.max_health)
        self.damage     = 0.5 * mult
        self.radius     = int(18 * _SIZE_MULT.get(rarity, 1.0))
        self.speed      = 3.2 / (1.0 + mult * 0.001)

        self.f_name   = pygame.font.SysFont("segoeui", 18, bold=True)
        self.f_rarity = pygame.font.SysFont("segoeui", 14, bold=True)

    def take_damage(self, amount, source_player):
        self.health -= amount
        self.state   = "chase"
        self.target  = source_player

    def update(self, player, world_map, all_mobs):
        self.bob_offset += 0.1
        dx, dy = 0.0, 0.0
        if self.state == "chase" and self.target:
            a  = math.atan2(self.target.y - self.y, self.target.x - self.x)
            dx = math.cos(a) * self.speed
            dy = math.sin(a) * self.speed
        self._move(world_map, dx, dy)
        self._separate(all_mobs, world_map)
        self._contact_player(player, world_map)

    def draw(self, screen, cam_x, cam_y):
        bob_y = int(math.sin(self.bob_offset) * 4)
        sx    = int(self.x - cam_x)
        sy    = int(self.y - cam_y) + bob_y
        r     = self.radius

        pygame.draw.ellipse(screen, (210, 235, 255),
                            (sx - r - 4, sy - r + 2, r + 2, (r + 2) // 2))
        pygame.draw.ellipse(screen, (210, 235, 255),
                            (sx + 2,    sy - r + 2, r + 2, (r + 2) // 2))
        pygame.draw.circle(screen, (30, 30, 30),  (sx, sy), r + 2)
        pygame.draw.circle(screen, (255, 215, 0), (sx, sy), r)
        sw2 = max(4, r // 2);  sh2 = max(3, r // 5)
        for off in (-sh2 - 2, sh2):
            pygame.draw.rect(screen, (20, 20, 20), (sx - sw2, sy + off, sw2 * 2, sh2))
        rc = RARITY_COLORS.get(self.rarity, (255, 255, 255))
        pygame.draw.circle(screen, rc, (sx, sy), r, 2)
        self._draw_hp_bar(screen, sx, sy)
        ns = self.f_name.render("Bee", True, (20, 20, 20))
        screen.blit(ns, ns.get_rect(center=(sx, sy - r - 16)))
        rs = self.f_rarity.render(self.rarity, True, rc)
        screen.blit(rs, rs.get_rect(center=(sx, sy + r + 22)))


# ══════════════════════════════════════════════════════════════════
#  LADYBUG  (Garden)
# ══════════════════════════════════════════════════════════════════

class Ladybug(_MobBase):
    _POWER = {"Common":1,"Rare":3,"Epic":12,"Legendary":48,"Mythic":200,"Ultra":800,"Super":4000}
    _SIZE  = {"Common":1.0,"Rare":1.25,"Epic":1.5,"Legendary":1.85,"Mythic":2.3,"Ultra":2.8,"Super":3.2}

    def __init__(self, x, y, rarity="Common"):
        self.x, self.y  = float(x), float(y)
        self.bob_offset  = random.uniform(0, math.pi * 2)
        self.rarity      = rarity
        self.state       = "idle"
        self.target      = None
        self.mob_type    = "Ladybug"

        mult            = self._POWER.get(rarity, 1)
        self.max_health = 40 * mult
        self.health     = float(self.max_health)
        self.damage     = 0.4 * mult
        self.radius     = int(16 * self._SIZE.get(rarity, 1.0))
        self.speed      = 3.8 / (1.0 + mult * 0.0008)

        self.f_name   = pygame.font.SysFont("segoeui", 18, bold=True)
        self.f_rarity = pygame.font.SysFont("segoeui", 14, bold=True)

    def take_damage(self, amount, source_player):
        self.health -= amount
        self.state   = "chase"
        self.target  = source_player

    def update(self, player, world_map, all_mobs):
        self.bob_offset += 0.12
        dx, dy = 0.0, 0.0
        if self.state == "chase" and self.target:
            a  = math.atan2(self.target.y - self.y, self.target.x - self.x)
            dx = math.cos(a) * self.speed
            dy = math.sin(a) * self.speed
        self._move(world_map, dx, dy)
        self._separate(all_mobs, world_map)
        self._contact_player(player, world_map)

    def draw(self, screen, cam_x, cam_y):
        bob_y = int(math.sin(self.bob_offset) * 3)
        sx    = int(self.x - cam_x)
        sy    = int(self.y - cam_y) + bob_y
        r     = self.radius
        rc    = RARITY_COLORS.get(self.rarity, (255, 255, 255))
        pygame.draw.circle(screen, (30, 30, 30),  (sx, sy), r + 2)
        pygame.draw.circle(screen, (210, 30, 30), (sx, sy), r)
        dot_r = max(2, r // 6)
        for ddx, ddy in [(-r//3, -r//4), (r//3, -r//4), (0, r//4)]:
            pygame.draw.circle(screen, (20, 20, 20), (sx + ddx, sy + ddy), dot_r)
        pygame.draw.line(screen, (20, 20, 20), (sx, sy - r), (sx, sy + r), max(1, r // 8))
        hr    = max(5, int(r * 0.52))
        hsurf = pygame.Surface((hr * 2 + 4, hr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(hsurf, (20, 20, 20), (hr + 2, hr + 2), hr)
        pygame.draw.rect(hsurf, (0, 0, 0, 0), (0, hr + 2, hr * 2 + 4, hr + 2))
        screen.blit(hsurf, (sx - hr - 2, sy - r - hr - 1))
        ey  = sy - r - hr // 2 - 1
        er2 = max(2, hr // 4)
        for ex2 in (sx - hr // 2, sx + hr // 2):
            pygame.draw.circle(screen, (255, 255, 255), (ex2, ey), er2)
            pygame.draw.circle(screen, (10,  10,  10),  (ex2, ey), max(1, er2 - 1))
        pygame.draw.circle(screen, rc, (sx, sy), r, 2)
        self._draw_hp_bar(screen, sx, sy)
        ns = self.f_name.render("Ladybug", True, (255, 255, 255))
        screen.blit(ns, ns.get_rect(center=(sx, sy - r - hr - 20)))
        rs = self.f_rarity.render(self.rarity, True, rc)
        screen.blit(rs, rs.get_rect(center=(sx, sy + r + 22)))


# ══════════════════════════════════════════════════════════════════
#  BUBBLE  (Ocean — passive, low HP, drops Bubble petal)
# ══════════════════════════════════════════════════════════════════

class Bubble(_MobBase):
    _HP   = {"Common":8,"Rare":20,"Epic":45,"Legendary":100,"Mythic":200,"Ultra":400,"Super":800}
    _SIZE = {"Common":1.0,"Rare":1.2,"Epic":1.4,"Legendary":1.7,"Mythic":2.0,"Ultra":2.4,"Super":2.8}

    def __init__(self, x, y, rarity="Common"):
        self.x, self.y  = float(x), float(y)
        self.bob_offset  = random.uniform(0, math.pi * 2)
        self.rarity      = rarity
        self.mob_type    = "Bubble"
        self.state       = "wander"
        self.target      = None
        self.max_health  = float(self._HP.get(rarity, 8))
        self.health      = self.max_health
        self.damage      = 0.0
        self.radius      = int(16 * self._SIZE.get(rarity, 1.0))
        self.speed       = 1.2
        self._wander_angle = random.uniform(0, math.pi * 2)
        self._wander_timer = random.randint(60, 180)
        self.f_name   = pygame.font.SysFont("segoeui", 16, bold=True)
        self.f_rarity = pygame.font.SysFont("segoeui", 13, bold=True)

    def take_damage(self, amount, source_player):
        self.health -= amount

    def update(self, player, world_map, all_mobs):
        self.bob_offset += 0.08
        self._wander_timer -= 1
        if self._wander_timer <= 0:
            self._wander_angle = random.uniform(0, math.pi * 2)
            self._wander_timer = random.randint(60, 180)
        dx = math.cos(self._wander_angle) * self.speed
        dy = math.sin(self._wander_angle) * self.speed
        self._move(world_map, dx, dy)
        self._separate(all_mobs, world_map)
        dp = math.hypot(player.x - self.x, player.y - self.y)
        if dp < self.radius + player.radius and dp > 0:
            push = math.atan2(player.y - self.y, player.x - self.x)
            ovlp = (self.radius + player.radius) - dp
            nx   = player.x + math.cos(push) * ovlp
            ny   = player.y + math.sin(push) * ovlp
            if not world_map.is_colliding(nx, ny, player.radius):
                player.x, player.y = nx, ny

    def draw(self, screen, cam_x, cam_y):
        bob_y = int(math.sin(self.bob_offset) * 3)
        sx    = int(self.x - cam_x)
        sy    = int(self.y - cam_y) + bob_y
        r     = self.radius
        rc    = RARITY_COLORS.get(self.rarity, (200, 200, 200))
        bsurf = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
        cx2, cy2 = r + 3, r + 3
        pygame.draw.circle(bsurf, (60, 65, 70, 180),    (cx2, cy2), r + 2)
        pygame.draw.circle(bsurf, (150, 158, 165, 110), (cx2, cy2), r)
        pygame.draw.circle(bsurf, (*rc, 40),             (cx2, cy2), r - 3)
        pygame.draw.circle(bsurf, (220, 230, 240, 80),
                           (cx2 - r // 4, cy2 - r // 4), max(2, r // 4))
        pygame.draw.circle(bsurf, (*rc, 160), (cx2, cy2), r, 2)
        screen.blit(bsurf, (sx - r - 3, sy - r - 3))
        self._draw_hp_bar(screen, sx, sy)
        ns = self.f_name.render("Bubble", True, (200, 215, 230))
        screen.blit(ns, ns.get_rect(center=(sx, sy - r - 14)))
        rs = self.f_rarity.render(self.rarity, True, rc)
        screen.blit(rs, rs.get_rect(center=(sx, sy + r + 20)))


# ══════════════════════════════════════════════════════════════════
#  JELLYFISH  (Ocean — follows player after hit, ranged lightning)
# ══════════════════════════════════════════════════════════════════

class Jellyfish(_MobBase):
    # Jellyfish are mid-tier compared to bubbles – more HP, does damage
    _HP   = {"Common":35,"Rare":90,"Epic":220,"Legendary":600,"Mythic":1500,"Ultra":4000,"Super":12000}
    _SIZE = {"Common":1.0,"Rare":1.2,"Epic":1.5,"Legendary":1.8,"Mythic":2.2,"Ultra":2.7,"Super":3.2}
    _DMG  = {"Common":3.0,"Rare":8.0,"Epic":20.0,"Legendary":50.0,"Mythic":120.0,"Ultra":300.0,"Super":700.0}

    # Lightning range: how far the jellyfish can shock from (tentacle range)
    LIGHTNING_RANGE    = 120   # pixels
    LIGHTNING_COOLDOWN = 90    # frames = 1.5 s at 60fps

    def __init__(self, x, y, rarity="Common"):
        self.x, self.y   = float(x), float(y)
        self.bob_offset   = random.uniform(0, math.pi * 10)
        self.rarity       = rarity
        self.mob_type     = "Jellyfish"
        self.state        = "wander"   # wander → chase (after taking damage)
        self.target       = None

        self.max_health   = float(self._HP.get(rarity, 35))
        self.health       = self.max_health
        self.damage       = 0.0   # melee does nothing; lightning deals damage
        self.lightning_dmg = self._DMG.get(rarity, 3.0)
        self.radius       = int(18 * self._SIZE.get(rarity, 1.0))
        self.speed        = 1.8

        # Lightning state
        self._lightning_cd     = 0     # frames until next shock
        self._lightning_flash  = 0     # visual flash timer (frames)
        self._lightning_target = None  # player ref when shocking
        self._lightning_bounce_pos = None  # second mob hit position for bounce visual

        # Wander
        self._wander_angle = random.uniform(0, math.pi * 2)
        self._wander_timer = random.randint(80, 200)

        self.f_name   = pygame.font.SysFont("segoeui", 16, bold=True)
        self.f_rarity = pygame.font.SysFont("segoeui", 13, bold=True)

    def take_damage(self, amount, source_player):
        self.health -= amount
        # Becomes aggressive when hit
        self.state   = "chase"
        self.target  = source_player

    def _try_lightning(self, player, all_mobs):
        """Fire lightning at player if in range, then bounce to a nearby mob."""
        if self._lightning_cd > 0:
            return
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)
        if dist_to_player > self.LIGHTNING_RANGE:
            return

        # Strike player
        player.health -= self.lightning_dmg
        self._lightning_cd    = self.LIGHTNING_COOLDOWN
        self._lightning_flash = 12
        self._lightning_target = player
        self._lightning_bounce_pos = None

        # Bounce to nearest OTHER mob within 180px
        best_mob  = None
        best_dist = 180.0
        for mob in all_mobs:
            if mob is self:
                continue
            d = math.hypot(mob.x - self.x, mob.y - self.y)
            if d < best_dist:
                best_dist = d
                best_mob  = mob
        if best_mob is not None:
            best_mob.health -= self.lightning_dmg * 0.6
            self._lightning_bounce_pos = (best_mob.x, best_mob.y)

    def update(self, player, world_map, all_mobs):
        self.bob_offset += 0.09
        if self._lightning_cd > 0:
            self._lightning_cd -= 1
        if self._lightning_flash > 0:
            self._lightning_flash -= 1

        if self.state == "chase" and self.target:
            a  = math.atan2(self.target.y - self.y, self.target.x - self.x)
            dx = math.cos(a) * self.speed
            dy = math.sin(a) * self.speed
            self._move(world_map, dx, dy)
            self._try_lightning(player, all_mobs)
        else:
            # Wander slowly
            self._wander_timer -= 1
            if self._wander_timer <= 0:
                self._wander_angle = random.uniform(0, math.pi * 2)
                self._wander_timer = random.randint(80, 200)
            dx = math.cos(self._wander_angle) * self.speed * 0.5
            dy = math.sin(self._wander_angle) * self.speed * 0.5
            self._move(world_map, dx, dy)

        self._separate(all_mobs, world_map)
        # No melee contact damage (lightning only)
        dp = math.hypot(player.x - self.x, player.y - self.y)
        if dp < self.radius + player.radius and dp > 0:
            push = math.atan2(player.y - self.y, player.x - self.x)
            ovlp = (self.radius + player.radius) - dp
            nx   = player.x + math.cos(push) * ovlp
            ny   = player.y + math.sin(push) * ovlp
            if not world_map.is_colliding(nx, ny, player.radius):
                player.x, player.y = nx, ny

    def draw(self, screen, cam_x, cam_y):
        bob_y = int(math.sin(self.bob_offset) * 4)
        sx    = int(self.x - cam_x)
        sy    = int(self.y - cam_y) + bob_y
        r     = self.radius
        rc    = RARITY_COLORS.get(self.rarity, (160, 200, 255))

        # Lightning bolt visual when flashing
        if self._lightning_flash > 0 and self._lightning_target:
            tx = int(self._lightning_target.x - cam_x)
            ty = int(self._lightning_target.y - cam_y)
            alpha = min(255, self._lightning_flash * 20)
            lsurf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            # Main bolt
            pygame.draw.line(lsurf, (200, 220, 255, alpha), (sx, sy), (tx, ty), 3)
            # Jagged segments
            steps  = 5
            pts    = [(sx, sy)]
            for i in range(1, steps):
                frac  = i / steps
                mx2   = sx + (tx - sx) * frac + random.randint(-12, 12)
                my2   = sy + (ty - sy) * frac + random.randint(-12, 12)
                pts.append((mx2, my2))
            pts.append((tx, ty))
            if len(pts) >= 2:
                pygame.draw.lines(lsurf, (255, 255, 180, alpha), False, pts, 2)
            screen.blit(lsurf, (0, 0))

            # Bounce bolt
            if self._lightning_bounce_pos:
                bx2 = int(self._lightning_bounce_pos[0] - cam_x)
                by2 = int(self._lightning_bounce_pos[1] - cam_y)
                lsurf2 = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                pygame.draw.line(lsurf2, (160, 200, 255, alpha // 2),
                                 (tx, ty), (bx2, by2), 2)
                screen.blit(lsurf2, (0, 0))

        # Body – translucent blue-purple circle (like a bubble but blueish)
        bsurf = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        cx2, cy2 = r + 4, r + 4
        # Outer rim
        pygame.draw.circle(bsurf, (30, 40, 80, 200),     (cx2, cy2), r + 3)
        # Main fill – semi-transparent blue
        pygame.draw.circle(bsurf, (80, 120, 200, 130),   (cx2, cy2), r)
        # Inner shimmer
        pygame.draw.circle(bsurf, (140, 180, 255, 60),   (cx2, cy2), r - 4)
        # Highlight
        pygame.draw.circle(bsurf, (200, 220, 255, 90),
                           (cx2 - r // 4, cy2 - r // 3), max(2, r // 3))
        # Rarity ring
        pygame.draw.circle(bsurf, (*rc, 200), (cx2, cy2), r + 1, 2)
        # Flash glow when shocking
        if self._lightning_flash > 0:
            pulse_a = min(160, self._lightning_flash * 12)
            pygame.draw.circle(bsurf, (255, 255, 180, pulse_a), (cx2, cy2), r + 3, 3)
        screen.blit(bsurf, (sx - r - 4, sy - r - 4))

        # Tentacles (4 wavy lines hanging below)
        t_anim = pygame.time.get_ticks() * 0.004
        num_t  = 4
        t_col  = (*rc, 160)
        t_surf = pygame.Surface((r * 6, r * 4), pygame.SRCALPHA)
        for i in range(num_t):
            base_x    = r * 3 + int((i - num_t / 2 + 0.5) * (r * 1.2))
            seg_count = 5
            prev      = (base_x, 0)
            for j in range(1, seg_count + 1):
                frac    = j / seg_count
                wave_x  = base_x + int(math.sin(t_anim + i * 1.2 + frac * 3) * (r * 0.4))
                wave_y  = int(frac * r * 2.5)
                nxt     = (wave_x, wave_y)
                pygame.draw.line(t_surf, t_col, prev, nxt, max(1, r // 8))
                prev    = nxt
        screen.blit(t_surf, (sx - r * 3, sy + r - 4))

        self._draw_hp_bar(screen, sx, sy)
        ns = self.f_name.render("Jellyfish", True, (200, 215, 255))
        screen.blit(ns, ns.get_rect(center=(sx, sy - r - 14)))
        rs = self.f_rarity.render(self.rarity, True, rc)
        screen.blit(rs, rs.get_rect(center=(sx, sy + r + 22)))


# ══════════════════════════════════════════════════════════════════
#  GARDEN MOB MANAGER
# ══════════════════════════════════════════════════════════════════

class MobManager:
    """Manages Bees and Ladybugs in the Garden world.
    
    Spawning uses distance-based rarity so high rarities ONLY appear far
    from center. Max dist for _get_pos_and_rarity is 1800 (Mythic/Ultra zone
    boundary), and Super is only spawned separately with a tiny chance.
    """

    def __init__(self, world_map, num_bees=70, num_ladybugs=60, index_button=None):
        self.bees         = []
        self.ladybugs     = []
        self.index_button = index_button
        self.world_map    = world_map
        self._spawn_bees(num_bees)
        self._spawn_ladybugs(num_ladybugs)

    def _get_pos_and_rarity(self, allow_super=False):
        wm = self.world_map
        # Calculate the actual maximum possible distance from center to corner
        # For a 9000x9000 map, this is roughly 6360
        map_radius = math.hypot(wm.width_px/2, wm.height_px/2)

        for _ in range(200):
            if hasattr(wm, "safe_spawn_pos"):
                # Use the full map radius so mobs spawn in all 9 rooms
                # We cap it slightly before the edge to avoid spawning inside outer walls
                max_d = map_radius * 0.95 if allow_super else map_radius * 0.8
                x, y = wm.safe_spawn_pos(min_dist=320, max_dist=max_d)
            else:
                # Standard random spawn if safe_spawn isn't working
                x = random.uniform(100, wm.width_px - 100)
                y = random.uniform(100, wm.height_px - 100)

            # Check if we spawned inside a wall
            if wm.is_colliding(x, y, 28):
                continue

            if hasattr(wm, "rarity_for_position"):
                rarity = wm.rarity_for_position(x, y)
            else:
                rarity = "Common"

            if rarity is None:
                continue

            # In the bigger map, we want Supers to be possible in the far corners
            if rarity == "Super" and not allow_super:
                # 10% chance to allow it anyway if we're in the deep zones
                if random.random() > 0.10: 
                    continue
            
            return x, y, rarity

        # Ultimate fallback (Center of the world)
        return wm.width_px // 2, wm.height_px // 2, "Common"
    def _spawn_bees(self, count):
        for _ in range(count):
            x, y, r = self._get_pos_and_rarity()
            self.bees.append(Bee(x, y, r))

    def _spawn_ladybugs(self, count):
        for _ in range(count):
            x, y, r = self._get_pos_and_rarity()
            self.ladybugs.append(Ladybug(x, y, r))

    def _respawn_mob(self, mob_type):
        """Respawn one mob. Very occasionally allows a Super (1 in 80)."""
        allow_super = (random.randint(1, 80) == 1)
        x, y, r    = self._get_pos_and_rarity(allow_super=allow_super)
        if mob_type == "Bee":
            self.bees.append(Bee(x, y, r))
        else:
            self.ladybugs.append(Ladybug(x, y, r))

    def update(self, player, world_map, petal_manager):
        all_mobs = self.bees + self.ladybugs

        for mob_list, drop_type, mob_key in [
            (self.bees,     "Glass", "Bee"),
            (self.ladybugs, "Light", "Ladybug"),
        ]:
            for mob in mob_list[:]:
                mob.update(player, world_map, all_mobs)

                for p in petal_manager.petals:
                    if not p.active:
                        continue
                    hit = p.collides_with(mob.x, mob.y, mob.radius)
                    # Lightning petal bounces
                    if hit and p.petal_type == "Lightning":
                        mob.take_damage(p.damage, player)
                        p.active         = False
                        p.cooldown_timer = p.reload_time
                        ka = math.atan2(mob.y - p.y, mob.x - p.x)
                        mob.x += math.cos(ka) * 12
                        mob.y += math.sin(ka) * 12
                        # Bounce: hit nearest other mob within 200px
                        bounce_range = 200
                        best = None;  bd = bounce_range
                        for other in all_mobs:
                            if other is mob: continue
                            d = math.hypot(other.x - mob.x, other.y - mob.y)
                            if d < bd:
                                bd = d; best = other
                        if best:
                            best.take_damage(p.damage * 0.6, player)
                            # Visual flash
                            p._bounce_flash = (int(mob.x), int(mob.y),
                                               int(best.x), int(best.y), 12)
                    elif hit:
                        mob.take_damage(p.damage, player)
                        p.active         = False
                        p.cooldown_timer = p.reload_time
                        ka = math.atan2(mob.y - p.y, mob.x - p.x)
                        mob.x += math.cos(ka) * 14
                        mob.y += math.sin(ka) * 14

                if mob.health <= 0:
                    if self.index_button:
                        self.index_button.increment(mob.rarity, mob_key)
                    xp_mult = 1.0 if mob_key == "Bee" else 0.85
                    petal_manager.spawn_dropped_petal(mob.x, mob.y, mob.rarity, drop_type)
                    mob_list.remove(mob)
                    player.gain_xp(int(_XP.get(mob.rarity, 25) * xp_mult))
                    self._respawn_mob(mob_key)

    def draw(self, screen, cam_x, cam_y):
        for b  in self.bees:      b.draw(screen, cam_x, cam_y)
        for lb in self.ladybugs:  lb.draw(screen, cam_x, cam_y)

    @property
    def all_mobs(self):
        return self.bees + self.ladybugs


# ══════════════════════════════════════════════════════════════════
#  OCEAN MOB MANAGER  (Bubbles + Jellyfish)
# ══════════════════════════════════════════════════════════════════

class OceanMobManager:
    _OCEAN_ZONES = [
        {"r_min":   0, "r_max":  250, "safe": True},
        {"r_min": 250, "r_max":  600, "min_ri": 0, "max_ri": 0},
        {"r_min": 600, "r_max":  950, "min_ri": 1, "max_ri": 2},
        {"r_min": 950, "r_max": 1300, "min_ri": 2, "max_ri": 3},
        {"r_min":1300, "r_max": 9999, "min_ri": 4, "max_ri": 5},
    ]
    _RARITY_LIST = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra"]

    def __init__(self, world_map, num_bubbles=50, num_jellyfish=50, index_button=None):
        self.bubbles      = []
        self.jellyfish    = []
        self.world_map    = world_map
        self.index_button = index_button
        self._spawn_bubbles(num_bubbles)
        self._spawn_jellyfish(num_jellyfish)

    def _rarity_for_pos(self, x, y):
        wm     = self.world_map
        cx, cy = wm.width_px // 2, wm.height_px // 2
        dist   = math.hypot(x - cx, y - cy)
        for zone in self._OCEAN_ZONES:
            if zone["r_min"] <= dist < zone["r_max"]:
                if zone.get("safe"):
                    return None
                lo, hi  = zone["min_ri"], zone["max_ri"]
                choices = self._RARITY_LIST[lo: hi + 1]
                n       = len(choices)
                weights = [max(1, 10 - i * 3) for i in range(n)]
                return random.choices(choices, weights=weights)[0]
        return "Rare"

    def _rand_pos(self, min_dist=280, max_dist=3400):
        wm     = self.world_map
        cx, cy = wm.width_px // 2, wm.height_px // 2
        for _ in range(200):
            a = random.uniform(0, math.pi * 2)
            d = random.uniform(min_dist, max_dist)
            x = cx + math.cos(a) * d
            y = cy + math.sin(a) * d
            x = max(60, min(wm.width_px - 60, x))
            y = max(60, min(wm.height_px - 60, y))
            if not wm.is_colliding(x, y, 25):
                return x, y
        return cx + 300, cy + 300

    def _spawn_bubbles(self, count):
        for _ in range(count):
            x, y   = self._rand_pos()
            rarity = self._rarity_for_pos(x, y) or "Common"
            self.bubbles.append(Bubble(x, y, rarity))

    def _spawn_jellyfish(self, count):
        for _ in range(count):
            # Jellyfish start a bit farther from center than bubbles
            x, y   = self._rand_pos(min_dist=350, max_dist=1400)
            rarity = self._rarity_for_pos(x, y) or "Common"
            self.jellyfish.append(Jellyfish(x, y, rarity))

    def update(self, player, world_map, petal_manager):
        all_mobs = list(self.bubbles) + list(self.jellyfish)

        # ── Bubbles ──────────────────────────────────────────────
        for b in self.bubbles[:]:
            b.update(player, world_map, all_mobs)
            for p in petal_manager.petals:
                if p.petal_type == "Bubble":
                    continue   # Bubble petal never damages mobs
                if p.active and p.collides_with(b.x, b.y, b.radius):
                    b.take_damage(p.damage, player)
                    p.active         = False
                    p.cooldown_timer = p.reload_time
                    ka = math.atan2(b.y - p.y, b.x - p.x)
                    b.x += math.cos(ka) * 10
                    b.y += math.sin(ka) * 10
            if b.health <= 0:
                if self.index_button:
                    self.index_button.increment(b.rarity, "Bubble")
                petal_manager.spawn_dropped_petal(b.x, b.y, b.rarity, "Bubble")
                self.bubbles.remove(b)
                player.gain_xp(int(_XP.get(b.rarity, 25) * 0.4))
                self._spawn_bubbles(1)

        # ── Jellyfish ─────────────────────────────────────────────
        for jf in self.jellyfish[:]:
            jf.update(player, world_map, all_mobs)

            for p in petal_manager.petals:
                if not p.active:
                    continue
                hit = p.collides_with(jf.x, jf.y, jf.radius)
                if hit and p.petal_type == "Lightning":
                    jf.take_damage(p.damage, player)
                    p.active         = False
                    p.cooldown_timer = p.reload_time
                    # Lightning bounces to nearest other mob
                    best = None;  bd = 200.0
                    for other in all_mobs:
                        if other is jf: continue
                        d = math.hypot(other.x - jf.x, other.y - jf.y)
                        if d < bd:
                            bd = d; best = other
                    if best:
                        best.take_damage(p.damage * 0.6, player)
                elif hit:
                    jf.take_damage(p.damage, player)
                    p.active         = False
                    p.cooldown_timer = p.reload_time
                    ka = math.atan2(jf.y - p.y, jf.x - p.x)
                    jf.x += math.cos(ka) * 12
                    jf.y += math.sin(ka) * 12

            if jf.health <= 0:
                if self.index_button:
                    self.index_button.increment(jf.rarity, "Jellyfish")
                petal_manager.spawn_dropped_petal(jf.x, jf.y, jf.rarity, "Lightning")
                self.jellyfish.remove(jf)
                player.gain_xp(int(_XP.get(jf.rarity, 25) * 0.7))
                self._spawn_jellyfish(1)

    def draw(self, screen, cam_x, cam_y):
        for b  in self.bubbles:   b.draw(screen, cam_x, cam_y)
        for jf in self.jellyfish: jf.draw(screen, cam_x, cam_y)

    @property
    def all_mobs(self):
        return list(self.bubbles) + list(self.jellyfish)