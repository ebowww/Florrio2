import pygame
import math

# ══════════════════════════════════════════════════════════════════
#  XP FORMULA  —  floor(100 * level^1.55)
# ══════════════════════════════════════════════════════════════════

def xp_required(level: int) -> int:
    return int(100 * (level ** 1.55))


# ══════════════════════════════════════════════════════════════════
#  TALENT TREE
#
#  Each entry:
#    label, desc, col, row, max_ranks, costs (list len == max_ranks),
#    requires (id that must be FULLY maxed first), branch_color
#
#  costs[i] = SP needed to buy rank i+1
#  Costs increase per rank so later ranks are always more expensive.
# ══════════════════════════════════════════════════════════════════

TALENT_TREE = {
    # ── col 0  LOADOUT ───────────────────────────────────────────
    "loadout_1": {
        "label": "Extra Petal I",  "desc": "+1 petal slot  (6 total)",
        "col": 0, "row": 0, "max_ranks": 1, "costs": [1],
        "requires": None, "branch_color": (80, 195, 120),
    },
    "loadout_2": {
        "label": "Extra Petal II", "desc": "+1 petal slot  (7 total)",
        "col": 0, "row": 1, "max_ranks": 1, "costs": [3],
        "requires": "loadout_1", "branch_color": (80, 195, 120),
    },
    "loadout_3": {
        "label": "Extra Petal III","desc": "+1 petal slot  (8 total)",
        "col": 0, "row": 2, "max_ranks": 1, "costs": [7],
        "requires": "loadout_2", "branch_color": (80, 195, 120),
    },

    # ── col 1  HEALTH ────────────────────────────────────────────
    "health_1": {
        "label": "Vitality I",   "desc": "+50 max HP per rank",
        "col": 1, "row": 0, "max_ranks": 3, "costs": [1, 2, 3],
        "requires": None, "branch_color": (220, 70, 70),
    },
    "health_2": {
        "label": "Vitality II",  "desc": "+100 max HP per rank",
        "col": 1, "row": 1, "max_ranks": 3, "costs": [2, 4, 6],
        "requires": "health_1", "branch_color": (220, 70, 70),
    },
    "health_3": {
        "label": "Vitality III", "desc": "+200 max HP per rank",
        "col": 1, "row": 2, "max_ranks": 3, "costs": [4, 7, 10],
        "requires": "health_2", "branch_color": (220, 70, 70),
    },

    # ── col 2  RELOAD ────────────────────────────────────────────
    "reload_1": {
        "label": "Quick Bloom I",  "desc": "-12% petal cooldown per rank",
        "col": 2, "row": 0, "max_ranks": 3, "costs": [1, 2, 3],
        "requires": None, "branch_color": (90, 155, 240),
    },
    "reload_2": {
        "label": "Quick Bloom II", "desc": "-15% petal cooldown per rank",
        "col": 2, "row": 1, "max_ranks": 3, "costs": [2, 4, 6],
        "requires": "reload_1", "branch_color": (90, 155, 240),
    },
    "reload_3": {
        "label": "Quick Bloom III","desc": "-18% petal cooldown per rank",
        "col": 2, "row": 2, "max_ranks": 3, "costs": [4, 7, 10],
        "requires": "reload_2", "branch_color": (90, 155, 240),
    },

    # ── col 3  BODY DAMAGE ───────────────────────────────────────
    "body_1": {
        "label": "Thorns I",   "desc": "+8 body dmg per rank",
        "col": 3, "row": 0, "max_ranks": 3, "costs": [1, 2, 3],
        "requires": None, "branch_color": (210, 135, 40),
    },
    "body_2": {
        "label": "Thorns II",  "desc": "+18 body dmg per rank",
        "col": 3, "row": 1, "max_ranks": 3, "costs": [2, 4, 6],
        "requires": "body_1", "branch_color": (210, 135, 40),
    },
    "body_3": {
        "label": "Thorns III", "desc": "+35 body dmg per rank",
        "col": 3, "row": 2, "max_ranks": 3, "costs": [4, 7, 10],
        "requires": "body_2", "branch_color": (210, 135, 40),
    },
}

TALENT_IDS = list(TALENT_TREE.keys())


# ══════════════════════════════════════════════════════════════════
#  PLAYER
# ══════════════════════════════════════════════════════════════════

class Player:
    _FLASH_DURATION  = 55
    _BASE_BODY_DMG   = 2.0   # per-frame while touching a mob

    def __init__(self, start_x, start_y, world_map=None, radius=20, color=(255, 230, 50)):
        self.x, self.y   = float(start_x), float(start_y)
        self.radius       = radius
        self.color        = color
        self.world_map    = world_map

        # Progression
        self.level        = 1
        self.xp           = 0
        self.xp_to_next   = xp_required(1)
        self.skill_points = 0
        self._flash_timer = 0

        # Talents  {id: current_rank}
        self.talents = {tid: 0 for tid in TALENT_IDS}

        # Combat stats  (recomputed by _compute_stats)
        self.max_health  = 100.0
        self.health      = 100.0
        self.regen_rate  = 0.04
        self.speed       = 4.5
        self.body_damage = self._BASE_BODY_DMG
        self.is_attacking = False

        # Set externally after PetalManager creation
        self.petal_manager = None

        # Inventory
        self.inventory = {}

        # Eye direction
        self._eye_dx = 0.0
        self._eye_dy = 0.0

        # Pre-baked fonts
        self.font_lvl = pygame.font.SysFont("segoeui", 13, bold=True)

    # ── helpers ──────────────────────────────────────────────────

    def _hp_bonus_from_talents(self) -> float:
        bonus = 0.0
        bonus += self.talents["health_1"] * 50
        bonus += self.talents["health_2"] * 100
        bonus += self.talents["health_3"] * 200
        return bonus

    def _body_bonus_from_talents(self) -> float:
        bonus = 0.0
        bonus += self.talents["body_1"] * 8
        bonus += self.talents["body_2"] * 18
        bonus += self.talents["body_3"] * 35
        return bonus

    def reload_multiplier(self) -> float:
        """Returns fraction of base reload time remaining after talents."""
        red  = self.talents["reload_1"] * 0.12
        red += self.talents["reload_2"] * 0.15
        red += self.talents["reload_3"] * 0.18
        return max(0.10, 1.0 - red)   # floor at 10 % of base

    def num_petal_slots(self) -> int:
        return 5 + self.talents["loadout_1"] + self.talents["loadout_2"] + self.talents["loadout_3"]

    # ── stat recompute ───────────────────────────────────────────

    def _compute_stats(self):
        """Rebuild all derived stats.  Call after any talent change or level-up."""
        # Max health
        old_max = self.max_health
        new_max = 100.0 + (self.level - 1) * 10.0 + self._hp_bonus_from_talents()
        # Scale current health proportionally
        ratio   = (self.health / old_max) if old_max > 0 else 1.0
        self.max_health = new_max
        self.health     = min(new_max, new_max * ratio)

        # Body damage
        self.body_damage = (self._BASE_BODY_DMG
                            + (self.level - 1) * 0.5
                            + self._body_bonus_from_talents())

        # Petal reload
        # Petal reload
        if self.petal_manager:
            talent_mult = self.reload_multiplier()  # Bonus from Quick Bloom
            for p in self.petal_manager.petals:
                # 1. Get the base reload for this specific type (e.g., Bubble=180, Glass=55)
                from petals import petal_reload_base
                base = petal_reload_base(p.petal_type)
                
                # 2. Get the rarity multiplier (e.g., Common=1.0, Unique=0.3)
                rarity_mult = p._RELOAD_MULTIPLIERS.get(p.rarity, 1.0)
                
                # 3. Combine them: Base * Talent * Rarity
                # We use max(10, ...) so it never reloads faster than 10 frames
                p.reload_time = max(10, int(base * talent_mult * rarity_mult))

    # ── talent spending ──────────────────────────────────────────

    def next_rank_cost(self, tid: str) -> int:
        """SP cost for the NEXT rank of talent `tid`. Returns 0 if maxed."""
        t    = TALENT_TREE[tid]
        rank = self.talents[tid]
        if rank >= t["max_ranks"]:
            return 0
        return t["costs"][rank]   # costs[rank] = cost to go from rank → rank+1

    def can_unlock(self, tid: str) -> bool:
        t    = TALENT_TREE[tid]
        rank = self.talents[tid]
        if rank >= t["max_ranks"]:
            return False
        cost = self.next_rank_cost(tid)
        if self.skill_points < cost:
            return False
        req = t["requires"]
        if req:
            req_t = TALENT_TREE[req]
            if self.talents[req] < req_t["max_ranks"]:
                return False
        return True

    def spend_talent(self, tid: str) -> bool:
        if not self.can_unlock(tid):
            return False
        cost = self.next_rank_cost(tid)
        self.skill_points   -= cost
        self.talents[tid]   += 1

        # Loadout change → resize petal ring
        if tid.startswith("loadout") and self.petal_manager:
            self.petal_manager.resize_slots(self.num_petal_slots())

        self._compute_stats()
        return True

    # ── XP / level ───────────────────────────────────────────────

    def gain_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp     -= self.xp_to_next
            self.level  += 1

            # +1 SP every level, +10 bonus every 10th level
            gained = 1 + (10 if self.level % 10 == 0 else 0)
            self.skill_points += gained

            self.speed        = min(7.5, self.speed + 0.04)
            self._flash_timer = self._FLASH_DURATION
            self.xp_to_next   = xp_required(self.level)

            self._compute_stats()
            self.health = self.max_health   # full heal on level-up

    # ── input / movement ─────────────────────────────────────────

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_attacking = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_attacking = False

    def handle_movement(self, keys, world_map, mouse_follow=False, camera=(0, 0)):
        dx, dy = 0.0, 0.0
        if mouse_follow:
            mx, my   = pygame.mouse.get_pos()
            tx, ty   = mx + camera[0], my + camera[1]
            dist     = math.hypot(tx - self.x, ty - self.y)
            if dist > 6:
                a = math.atan2(ty - self.y, tx - self.x)
                dx, dy = math.cos(a) * self.speed, math.sin(a) * self.speed
                self._eye_dx, self._eye_dy = math.cos(a), math.sin(a)
        else:
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if dx != 0 or dy != 0:
                ln = math.hypot(dx, dy)
                dx, dy = (dx / ln) * self.speed, (dy / ln) * self.speed
                self._eye_dx, self._eye_dy = dx / self.speed, dy / self.speed

        nx = self.x + dx
        if not world_map.is_colliding(nx, self.y, self.radius):
            if self.radius < nx < world_map.width_px - self.radius:
                self.x = nx
        ny = self.y + dy
        if not world_map.is_colliding(self.x, ny, self.radius):
            if self.radius < ny < world_map.height_px - self.radius:
                self.y = ny

    # ── per-frame update ─────────────────────────────────────────

    def update(self):
        if self.health < self.max_health:
            self.health = min(self.max_health, self.health + self.regen_rate)
        if self._flash_timer > 0:
            self._flash_timer -= 1

    # ── draw (world space) ───────────────────────────────────────

    def draw(self, screen, camera_x, camera_y):
        sx, sy = int(self.x - camera_x), int(self.y - camera_y)
        r = self.radius

        # Level-up gold flash ring
        if self._flash_timer > 0:
            ratio = self._flash_timer / self._FLASH_DURATION
            frad  = r + 6 + int((1 - ratio) * 14)
            fl    = pygame.Surface((frad * 2 + 4, frad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(fl, (255, 220, 60, int(220 * ratio)),
                               (frad + 2, frad + 2), frad, 3)
            screen.blit(fl, (sx - frad - 2, sy - frad - 2))

        # Drop shadow
        sh = pygame.Surface((r * 2 + 12, r * 2 + 12), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 55), (0, r // 2 + 2, r * 2 + 12, r + 4))
        screen.blit(sh, (sx - r - 6, sy))

        # Thorns spikes (body damage visual)
        if self.body_damage > self._BASE_BODY_DMG:
            slen = min(9, 3 + int((self.body_damage - self._BASE_BODY_DMG) / 12))
            for i in range(8):
                a  = math.radians(i * 45)
                x1 = sx + int(math.cos(a) * (r + 1))
                y1 = sy + int(math.sin(a) * (r + 1))
                x2 = sx + int(math.cos(a) * (r + slen))
                y2 = sy + int(math.sin(a) * (r + slen))
                pygame.draw.line(screen, (210, 135, 40), (x1, y1), (x2, y2), 2)

        # Body
        pygame.draw.circle(screen, (30, 30, 30), (sx, sy), r + 3)
        pygame.draw.circle(screen, self.color,   (sx, sy), r)
        pygame.draw.circle(screen, (255, 255, 255),
                           (sx - r // 4, sy - r // 4), max(2, r // 5))

        # Eyes
        for side in (-1, 1):
            ox = side * 7
            pygame.draw.ellipse(screen, (255, 255, 255), (sx + ox - 3, sy - 9, 7, 10))
            pygame.draw.circle(screen, (20, 20, 20),
                               (int(sx + ox + self._eye_dx * 3),
                                int(sy - 4 + self._eye_dy * 3)), 2)
        pygame.draw.arc(screen, (35, 35, 35),
                        pygame.Rect(sx - 5, sy + 3, 11, 7), math.pi, 0, 2)

        # HP bar
        bw, bh = 54, 7
        bx, by = sx - bw // 2, sy + r + 10
        pygame.draw.rect(screen, (30, 30, 30), (bx - 1, by - 1, bw + 2, bh + 2), border_radius=3)
        rhp = max(0.0, self.health / self.max_health)
        hw  = int(bw * rhp)
        bc  = (65, 205, 75) if rhp > 0.5 else (220, 170, 30) if rhp > 0.25 else (210, 50, 50)
        if hw > 0:
            pygame.draw.rect(screen, bc, (bx, by, hw, bh), border_radius=3)

        # XP bar
        xby = by + bh + 3
        rxp = self.xp / self.xp_to_next if self.xp_to_next else 0.0
        xw  = int(bw * rxp)
        pygame.draw.rect(screen, (22, 22, 28), (bx - 1, xby - 1, bw + 2, 7), border_radius=2)
        if xw > 0:
            pygame.draw.rect(screen, (75, 135, 255), (bx, xby, xw, 5), border_radius=2)

        # Level badge
        bdx, bdy = bx - 18, by + bh // 2
        pygame.draw.circle(screen, (20, 20, 28), (bdx, bdy), 11)
        pygame.draw.circle(screen, (75, 135, 255), (bdx, bdy), 9)
        lv = self.font_lvl.render(str(self.level), True, (255, 255, 255))
        screen.blit(lv, lv.get_rect(center=(bdx, bdy)))

    # ── static HUD ───────────────────────────────────────────────

    @staticmethod
    def draw_level_hud(screen, player, width, height):
        bw, bh = 360, 14
        bx     = (width - bw) // 2
        by     = height - bh - 6

        pygame.draw.rect(screen, (15, 15, 20), (bx - 2, by - 2, bw + 4, bh + 4), border_radius=8)
        pygame.draw.rect(screen, (35, 35, 45), (bx, by, bw, bh), border_radius=7)

        r  = player.xp / player.xp_to_next if player.xp_to_next else 0.0
        xw = int(bw * r)
        if xw > 0:
            pygame.draw.rect(screen, (60, 110, 230), (bx, by, xw, bh), border_radius=7)
            pygame.draw.rect(screen, (100, 160, 255),
                             (bx, by + 2, xw, max(2, bh // 3)), border_radius=4)

        fn  = pygame.font.SysFont("segoeui", 13, bold=True)
        lv  = fn.render(f"Lv {player.level}", True, (180, 190, 255))
        xps = fn.render(f"{player.xp:,} / {player.xp_to_next:,} XP", True, (150, 160, 210))
        screen.blit(lv,  (bx - lv.get_width() - 8,  by + bh // 2 - lv.get_height() // 2))
        screen.blit(xps, (bx + bw + 8,               by + bh // 2 - xps.get_height() // 2))

        # SP badge
        if player.skill_points > 0:
            spf  = pygame.font.SysFont("segoeui", 12, bold=True)
            sps  = spf.render(f"+{player.skill_points} SP", True, (255, 220, 60))
            spx, spy = bx + bw + 8, by - sps.get_height() - 2
            pygame.draw.rect(screen, (30, 28, 12),
                             (spx - 3, spy - 2, sps.get_width() + 6, sps.get_height() + 4),
                             border_radius=4)
            screen.blit(sps, (spx, spy))

        # Level-up float text
        if player._flash_timer > 0:
            ratio  = player._flash_timer / player._FLASH_DURATION
            offset = int((1 - ratio) * 30)
            ff  = pygame.font.SysFont("segoeui", 22, bold=True)
            fls = ff.render(f"Level {player.level}!", True, (255, 220, 60))
            fls.set_alpha(int(255 * ratio))
            screen.blit(fls, fls.get_rect(center=(width // 2, by - 18 - offset)))