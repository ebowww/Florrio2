import pygame
import math
import random

# ══════════════════════════════════════════════════════════════════
#  GARDEN WALLS  (axis-aligned rects: x, y, w, h)
#  All four cardinal passages are clear and verified by tests.
# ══════════════════════════════════════════════════════════════════

def generate_garden_map():
    walls = []
    # We will repeat the 3000px pattern at 0, 3000, and 6000
    offsets = [0, 3000, 6000]

    for off_x in offsets:
        for off_y in offsets:
            # Current cell base coordinates: (off_x, off_y)
            cell_walls = [
                # Outer border for this cell
                (off_x + 0,    off_y + 0,    1350, 50),   
                (off_x + 1650, off_y + 0,    1350, 50),   
                (off_x + 0,    off_y + 2950, 1350, 50),   
                (off_x + 1650, off_y + 2950, 1350, 50),   
                (off_x + 0,    off_y + 0,    50, 1350),   
                (off_x + 0,    off_y + 1650, 50, 1350),   
                (off_x + 2950, off_y + 0,    50, 1350),   
                (off_x + 2950, off_y + 1650, 50, 1350),   

                # Inner cross
                (off_x + 400,  off_y + 1475, 1000, 50),   
                (off_x + 1650, off_y + 1475, 1000, 50),   
                (off_x + 1475, off_y + 400,  50, 1040),   
                (off_x + 1475, off_y + 1560, 50, 1040),   

                # Corridor channels
                (off_x + 1350, off_y + 60,   50, 290),
                (off_x + 1600, off_y + 60,   50, 290),
                (off_x + 1350, off_y + 2650, 50, 290),
                (off_x + 1600, off_y + 2650, 50, 290),
                (off_x + 60,   off_y + 1350, 290, 50),
                (off_x + 60,   off_y + 1600, 290, 50),
                (off_x + 2650, off_y + 1350, 290, 50),
                (off_x + 2650, off_y + 1600, 290, 50),

                # Corner obstacles
                (off_x + 550,  off_y + 200,  180, 180),
                (off_x + 200,  off_y + 550,  180, 180),
                (off_x + 2270, off_y + 200,  180, 180),
                (off_x + 2620, off_y + 550,  180, 180),
                (off_x + 550,  off_y + 2620, 180, 180),
                (off_x + 200,  off_y + 2270, 180, 180),
                (off_x + 2270, off_y + 2620, 180, 180),
                (off_x + 2620, off_y + 2270, 180, 180),
            ]
            walls.extend(cell_walls)
            
    # Add final world-border at 10,000 to keep player inside
    walls.append((0, 9950, 10000, 50)) # Bottom world edge
    walls.append((9950, 0, 50, 10000)) # Right world edge
    
    return walls

# Now set your constant
GARDEN_WALLS = generate_garden_map()
# ══════════════════════════════════════════════════════════════════
#  MOB ZONES  (distance from world center 1500,1500)
#  Fixed: Common mobs are CLOSEST to spawn, rarities increase outward.
#
#  Zone  dist range    rarities
#  Safe  0 – 300      no mobs
#  1     300 – 550    Common only
#  2     550 – 850    Common / Rare
#  3     850 – 1150   Rare / Epic
#  4     1150 – 1450  Epic / Legendary
#  5     1450 – 1800  Legendary / Mythic
#  6     1800+        Mythic / Ultra
#  Super: 0.25% anywhere outside the safe zone (very rare)
# ══════════════════════════════════════════════════════════════════

RARITY_LIST = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra"]

GARDEN_ZONES = [
    {"r_min":    0, "r_max":  300, "safe": True},
    {"r_min":  300, "r_max":  550, "min_ri": 0, "max_ri": 0, "safe": False},  # Common
    {"r_min":  550, "r_max":  850, "min_ri": 0, "max_ri": 1, "safe": False},  # Common/Rare
    {"r_min":  850, "r_max": 1150, "min_ri": 1, "max_ri": 2, "safe": False},  # Rare/Epic
    {"r_min": 1150, "r_max": 1450, "min_ri": 2, "max_ri": 3, "safe": False},  # Epic/Legendary
    {"r_min": 1450, "r_max": 1800, "min_ri": 3, "max_ri": 4, "safe": False},  # Legendary/Mythic
    {"r_min": 1000, "r_max": 9999, "min_ri": 4, "max_ri": 5, "safe": False},  # Mythic/Ultra
]


# ══════════════════════════════════════════════════════════════════
#  PORTAL
# ══════════════════════════════════════════════════════════════════

class Portal:
    def __init__(self, x, y, target_world, color=(200, 220, 255), label="Ocean"):
        self.x            = float(x)
        self.y            = float(y)
        self.radius       = 40
        self.target_world = target_world
        self.color        = color
        self.label        = label
        self._t           = 0.0
        self.font         = pygame.font.SysFont("segoeui", 14, bold=True)

    def update(self):
        self._t += 0.04

    def contains(self, px, py):
        return math.hypot(px - self.x, py - self.y) < self.radius

    def draw(self, screen, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        r  = self.radius

        # Skip if off-screen
        sw, sh = screen.get_width(), screen.get_height()
        if sx < -r - 30 or sx > sw + r + 30 or sy < -r - 30 or sy > sh + r + 30:
            return

        pulse = int(math.sin(self._t) * 6)
        gr    = r + 18 + pulse
        glow  = pygame.Surface((gr * 2 + 4, gr * 2 + 4), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            pygame.draw.circle(glow, (*self.color, 28 * i),
                               (gr + 2, gr + 2), r + 4 + pulse + i * 3)
        screen.blit(glow, (sx - gr - 2, sy - gr - 2))

        pygame.draw.circle(screen, (8, 10, 18),  (sx, sy), r + 3)
        pygame.draw.circle(screen, self.color,    (sx, sy), r)

        # Rotating swirl lines
        for i in range(6):
            a  = self._t * 1.4 + i * (math.pi / 3)
            x1 = sx + int(math.cos(a) * 7)
            y1 = sy + int(math.sin(a) * 7)
            x2 = sx + int(math.cos(a) * (r - 7))
            y2 = sy + int(math.sin(a) * (r - 7))
            col_a = tuple(min(255, c + 80) for c in self.color)
            pygame.draw.line(screen, col_a, (x1, y1), (x2, y2), 1)

        pygame.draw.circle(screen, (230, 240, 255), (sx, sy), r // 3)

        lbl  = self.font.render(self.label, True, (255, 255, 255))
        shad = self.font.render(self.label, True, (0, 0, 0))
        lr   = lbl.get_rect(center=(sx, sy - r - 14))
        screen.blit(shad, (lr.x + 1, lr.y + 1))
        screen.blit(lbl, lr)


# ══════════════════════════════════════════════════════════════════
#  GARDEN WORLD
# ══════════════════════════════════════════════════════════════════

class GardenWorld:
    WIDTH  = 9000
    HEIGHT = 9000
    BG_LIGHT  = (38, 180, 55)
    BG_DARK   = (30, 158, 44)
    GRID_COL  = (26, 140, 38)
    WALL_COL  = (48, 32, 16)
    WALL_EDGE = (76, 52, 24)
    TILE      = 60

    def __init__(self):
        self.width_px  = self.WIDTH
        self.height_px = self.HEIGHT
        self._wall_rects = [pygame.Rect(x, y, w, h) for (x, y, w, h) in GARDEN_WALLS]
        # Portal in north corridor gap (y=220, well clear of walls)
        self.portal      = Portal(1500, 220, target_world=1,
                                  color=(160, 210, 255), label="Ocean →")
        self._tile_surf  = self._make_tile()

    def _make_tile(self):
        t   = self.TILE
        sur = pygame.Surface((t * 2, t * 2))
        sur.fill(self.BG_LIGHT)
        pygame.draw.rect(sur, self.BG_DARK, (0, 0, t, t))
        pygame.draw.rect(sur, self.BG_DARK, (t, t, t, t))
        return sur

    # ── collision ────────────────────────────────────────────────

    def is_colliding(self, x, y, radius):
        if x - radius < 0 or x + radius > self.width_px: return True
        if y - radius < 0 or y + radius > self.height_px: return True
        test = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        for wr in self._wall_rects:
            if wr.colliderect(test):
                cx = max(wr.left, min(x, wr.right))
                cy = max(wr.top,  min(y, wr.bottom))
                if math.hypot(x - cx, y - cy) < radius:
                    return True
        return False

    def get_safe_spawn(self):
        return self.WIDTH // 2, self.HEIGHT // 2

    def rarity_for_position(self, x, y):
        """Return rarity string matching the zone at (x, y), or None for safe zone."""
        cx, cy = self.WIDTH // 2, self.HEIGHT // 2
        dist   = math.hypot(x - cx, y - cy)

        # Super is extremely rare, available anywhere outside safe zone
        if dist > 300 and random.random() < 0.25:
            return "Super"

        for zone in GARDEN_ZONES:
            if zone["r_min"] <= dist < zone["r_max"]:
                if zone.get("safe"):
                    return None
                lo, hi   = zone["min_ri"], zone["max_ri"]
                choices  = RARITY_LIST[lo: hi + 1]
                n        = len(choices)
                # Weighted: first (lower) rarity is most common
                weights  = [max(1, 10 - i * 3) for i in range(n)]
                return random.choices(choices, weights=weights)[0]

        # Beyond all zones (shouldn't happen but fallback)
        return random.choice(["Mythic", "Ultra"])

    def safe_spawn_pos(self, min_dist=400, max_dist=1400):
        """Return a non-wall position between min_dist and max_dist from center."""
        cx, cy = self.WIDTH // 2, self.HEIGHT // 2
        for _ in range(300):
            angle = random.uniform(0, math.pi * 2)
            dist  = random.uniform(min_dist, max_dist)
            x     = cx + math.cos(angle) * dist
            y     = cy + math.sin(angle) * dist
            x     = max(60, min(self.WIDTH  - 60, x))
            y     = max(60, min(self.HEIGHT - 60, y))
            if not self.is_colliding(x, y, 28):
                return x, y
        return cx + 500, cy + 200   # last-resort fallback

    def update(self):
        self.portal.update()

    # ── draw ─────────────────────────────────────────────────────

    def draw(self, screen, cam_x, cam_y):
        sw, sh = screen.get_width(), screen.get_height()
        t2     = self.TILE * 2
        sx0    = (int(cam_x) // t2) * t2
        sy0    = (int(cam_y) // t2) * t2
        for ty in range(sy0, int(cam_y) + sh + t2, t2):
            for tx in range(sx0, int(cam_x) + sw + t2, t2):
                screen.blit(self._tile_surf, (tx - int(cam_x), ty - int(cam_y)))

        gs  = self.TILE
        gx0 = (int(cam_x) // gs) * gs
        gy0 = (int(cam_y) // gs) * gs
        for gx in range(gx0, int(cam_x) + sw + gs, gs):
            pygame.draw.line(screen, self.GRID_COL,
                             (gx - int(cam_x), 0), (gx - int(cam_x), sh), 1)
        for gy in range(gy0, int(cam_y) + sh + gs, gs):
            pygame.draw.line(screen, self.GRID_COL,
                             (0, gy - int(cam_y)), (sw, gy - int(cam_y)), 1)

        for wr in self._wall_rects:
            sr = pygame.Rect(wr.x - int(cam_x), wr.y - int(cam_y), wr.w, wr.h)
            if sr.right < 0 or sr.left > sw or sr.bottom < 0 or sr.top > sh:
                continue
            pygame.draw.rect(screen, self.WALL_COL,  sr, border_radius=4)
            pygame.draw.rect(screen, self.WALL_EDGE, sr, 2, border_radius=4)

        self.portal.draw(screen, cam_x, cam_y)

    def draw_minimap(self, screen, player, mobs):
        ms, mg = 150, 20
        mr     = pygame.Rect(screen.get_width() - ms - mg,
                             screen.get_height() - ms - mg, ms, ms)
        scale  = ms / self.WIDTH

        pygame.draw.rect(screen, (0, 0, 0),     mr.inflate(4, 4))
        pygame.draw.rect(screen, (22, 95, 28),  mr)

        for wr in self._wall_rects:
            wrm = pygame.Rect(mr.x + int(wr.x * scale), mr.y + int(wr.y * scale),
                              max(1, int(wr.w * scale)), max(1, int(wr.h * scale)))
            if mr.colliderect(wrm):
                pygame.draw.rect(screen, (38, 24, 8), wrm)

        pdx = mr.x + int(self.portal.x * scale)
        pdy = mr.y + int(self.portal.y * scale)
        if mr.collidepoint(pdx, pdy):
            pygame.draw.circle(screen, (160, 210, 255), (pdx, pdy), 3)

        for mob in mobs:
            mx2 = mr.x + int(mob.x * scale)
            my2 = mr.y + int(mob.y * scale)
            if mr.collidepoint(mx2, my2):
                pygame.draw.circle(screen, (215, 55, 55), (mx2, my2), 2)

        px2 = mr.x + int(player.x * scale)
        py2 = mr.y + int(player.y * scale)
        pygame.draw.circle(screen, (255, 255, 100), (px2, py2), 3)
        pygame.draw.rect(screen, (55, 62, 55), mr, 1)


# ══════════════════════════════════════════════════════════════════
#  OCEAN WORLD
# ══════════════════════════════════════════════════════════════════

class OceanWorld:
    WIDTH  = 9000
    HEIGHT = 9000
    BG_A   = (24,  88, 168)
    BG_B   = (18,  74, 148)
    TILE   = 80

    def __init__(self):
        self.width_px  = self.WIDTH
        self.height_px = self.HEIGHT
        self.portal    = Portal(1500, 1200, target_world=0,
                                color=(110, 195, 90), label="← Garden")
        self._tile_surf  = self._make_tile()
        self._wave_t     = 0.0
        self._bubbles    = [self._rand_bubble() for _ in range(70)]

    def _make_tile(self):
        t   = self.TILE
        sur = pygame.Surface((t * 2, t * 2))
        sur.fill(self.BG_A)
        pygame.draw.rect(sur, self.BG_B, (0, 0, t, t))
        pygame.draw.rect(sur, self.BG_B, (t, t, t, t))
        return sur

    def _rand_bubble(self):
        return {
            "x": random.uniform(0, self.WIDTH),
            "y": random.uniform(0, self.HEIGHT),
            "r": random.randint(3, 12),
            "speed": random.uniform(0.3, 1.4),
            "alpha": random.randint(25, 75),
        }

    def is_colliding(self, x, y, radius):
        return (x - radius < 0 or x + radius > self.width_px
                or y - radius < 0 or y + radius > self.height_px)

    def get_safe_spawn(self):
        return self.WIDTH // 2, self.HEIGHT // 2

    # No rarity_for_position – Ocean has its own mob manager

    def update(self):
        self.portal.update()
        self._wave_t += 0.022
        for b in self._bubbles:
            b["y"] -= b["speed"]
            if b["y"] < -20:
                b["y"]     = self.HEIGHT + 20
                b["x"]     = random.uniform(0, self.WIDTH)
                b["speed"] = random.uniform(0.3, 1.4)

    def draw(self, screen, cam_x, cam_y):
        sw, sh = screen.get_width(), screen.get_height()
        t2     = self.TILE * 2
        sx0    = (int(cam_x) // t2) * t2
        sy0    = (int(cam_y) // t2) * t2
        for ty in range(sy0, int(cam_y) + sh + t2, t2):
            for tx in range(sx0, int(cam_x) + sw + t2, t2):
                screen.blit(self._tile_surf, (tx - int(cam_x), ty - int(cam_y)))

        # Wave shimmer
        wave = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for i in range(0, sh + 70, 70):
            wy = i + int(math.sin(self._wave_t + i * 0.035) * 14)
            if 0 <= wy < sh:
                pygame.draw.line(wave, (80, 155, 255, 20), (0, wy), (sw, wy), 3)
        screen.blit(wave, (0, 0))

        # Bubbles
        bsurf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        for b in self._bubbles:
            bsx = int(b["x"] - cam_x)
            bsy = int(b["y"] - cam_y)
            if -20 < bsx < sw + 20 and -20 < bsy < sh + 20:
                pygame.draw.circle(bsurf, (195, 225, 255, b["alpha"]),
                                   (bsx, bsy), b["r"], 1)
                # Tiny highlight
                if b["r"] >= 5:
                    pygame.draw.circle(bsurf, (230, 245, 255, b["alpha"] // 2),
                                       (bsx - b["r"] // 3, bsy - b["r"] // 3),
                                       max(1, b["r"] // 3))
        screen.blit(bsurf, (0, 0))

        self.portal.draw(screen, cam_x, cam_y)

    def draw_minimap(self, screen, player, mobs):
        ms, mg = 150, 20
        mr     = pygame.Rect(screen.get_width() - ms - mg,
                             screen.get_height() - ms - mg, ms, ms)
        scale  = ms / self.WIDTH

        pygame.draw.rect(screen, (0, 0, 0),      mr.inflate(4, 4))
        pygame.draw.rect(screen, (20, 65, 135),  mr)

        pdx = mr.x + int(self.portal.x * scale)
        pdy = mr.y + int(self.portal.y * scale)
        if mr.collidepoint(pdx, pdy):
            pygame.draw.circle(screen, (110, 195, 90), (pdx, pdy), 3)

        for mob in mobs:
            mx2 = mr.x + int(mob.x * scale)
            my2 = mr.y + int(mob.y * scale)
            if mr.collidepoint(mx2, my2):
                pygame.draw.circle(screen, (160, 200, 255), (mx2, my2), 2)

        px2 = mr.x + int(player.x * scale)
        py2 = mr.y + int(player.y * scale)
        pygame.draw.circle(screen, (255, 255, 100), (px2, py2), 3)
        pygame.draw.rect(screen, (38, 65, 125), mr, 1)


# Backward-compat alias
WorldMap = GardenWorld