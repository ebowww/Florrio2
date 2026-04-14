import pygame
import math
import random

# ══════════════════════════════════════════════════════════════════
#  BASE CLASSES
# ══════════════════════════════════════════════════════════════════

class SideButton:
    def __init__(self, x, y, icon_text, color, tooltip=""):
        self.rect      = pygame.Rect(x, y, 52, 52)
        self.icon_text = icon_text
        self.color     = color
        self.tooltip   = tooltip
        self.font      = pygame.font.SysFont("segoeui", 15, bold=True)
        self.tip_font  = pygame.font.SysFont("segoeui", 14)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

    def draw(self, screen):
        hover    = self.rect.collidepoint(pygame.mouse.get_pos())
        draw_col = tuple(min(255, c + 40) for c in self.color) if hover else self.color
        pygame.draw.circle(screen, (10, 10, 10),
                           (self.rect.centerx + 2, self.rect.centery + 2), 24)
        pygame.draw.circle(screen, (20, 20, 20), self.rect.center, 26)
        pygame.draw.circle(screen, draw_col,     self.rect.center, 23)
        txt = self.font.render(self.icon_text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))
        if hover and self.tooltip:
            tip  = self.tip_font.render(self.tooltip, True, (255, 255, 255))
            trec = tip.get_rect(midleft=(self.rect.right + 8, self.rect.centery))
            pygame.draw.rect(screen, (30, 30, 30), trec.inflate(10, 6), border_radius=5)
            screen.blit(tip, trec)


class SlidingMenu:
    def __init__(self, screen_height, title, icon=""):
        self.width    = 320
        self.height   = 460
        self.x        = -self.width
        self.target_x = -self.width
        self.y        = (screen_height - self.height) // 2
        self.visible  = False
        self.title    = title
        self.icon     = icon
        self.title_font = pygame.font.SysFont("segoeui", 22, bold=True)

    def toggle(self):
        self.visible  = not self.visible
        self.target_x = 10 if self.visible else -self.width

    def update(self):
        self.x += (self.target_x - self.x) * 0.18

    def draw_panel(self, screen):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 22, 28, 215),
                         (0, 0, self.width, self.height),
                         border_top_right_radius=18, border_bottom_right_radius=18)
        pygame.draw.rect(surf, (255, 255, 255, 35),
                         (0, 0, self.width, self.height), 2,
                         border_top_right_radius=18, border_bottom_right_radius=18)
        screen.blit(surf, (self.x, self.y))
        label = f"{self.icon}  {self.title}" if self.icon else self.title
        ts = self.title_font.render(label, True, (220, 225, 255))
        screen.blit(ts, (self.x + 18, self.y + 14))
        pygame.draw.line(screen, (55, 58, 88),
                         (int(self.x) + 14, self.y + 50),
                         (int(self.x) + self.width - 14, self.y + 50), 1)


# ══════════════════════════════════════════════════════════════════
#  HUD BUTTONS
# ══════════════════════════════════════════════════════════════════

class CogButton:
    def __init__(self, x=15, y=15, size=42):
        self.rect     = pygame.Rect(x, y, size, size)
        self.font     = pygame.font.SysFont("segoeui", 13, bold=True)
        self.tip_font = pygame.font.SysFont("segoeui", 14)

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        col   = (190, 190, 190) if hover else (140, 140, 140)
        pygame.draw.circle(screen, (10, 10, 10),
                           (self.rect.centerx + 2, self.rect.centery + 2), 23)
        pygame.draw.circle(screen, (30, 30, 30), self.rect.center, 23)
        pygame.draw.circle(screen, col,          self.rect.center, 20)
        txt = self.font.render("SET", True, (30, 30, 30))
        screen.blit(txt, txt.get_rect(center=self.rect.center))
        if hover:
            tip  = self.tip_font.render("Settings", True, (255, 255, 255))
            trec = tip.get_rect(midleft=(self.rect.right + 8, self.rect.centery))
            pygame.draw.rect(screen, (30, 30, 30), trec.inflate(10, 6), border_radius=5)
            screen.blit(tip, trec)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class InventoryButton(SideButton):
    def __init__(self, sh): super().__init__(15, sh - 150, "INV", (60, 120, 185), "Inventory")

class CraftButton(SideButton):
    def __init__(self, sh): super().__init__(15, sh - 80,  "CFT", (115, 65, 195), "Craft")

class TalentButton(SideButton):
    def __init__(self, sh): super().__init__(15, sh - 220, "TAL", (170, 105, 35), "Talents [T]")


# ══════════════════════════════════════════════════════════════════
#  INDEX BUTTON / BESTIARY
# ══════════════════════════════════════════════════════════════════

class IndexButton:
    RARITIES  = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
    MOB_TYPES = ["Bee", "Ladybug", "Bubble", "Jellyfish"]

    def __init__(self, cog_button, size=42):
        self.size      = size
        self.rect      = pygame.Rect(cog_button.rect.right + 10,
                                     cog_button.rect.top, size, size)
        self.menu_open = False
        # counts[(mob_type, rarity)] = kill count
        self.counts    = {mob: {r: 0 for r in self.RARITIES} for mob in self.MOB_TYPES}

        self.f_title = pygame.font.SysFont("segoeui", 20, bold=True)
        self.f_sm    = pygame.font.SysFont("segoeui", 12, bold=True)
        self.f_mob   = pygame.font.SysFont("segoeui", 15, bold=True)
        self.f_tip   = pygame.font.SysFont("segoeui", 14)

    def increment(self, rarity, mob_type="Bee"):
        if mob_type in self.counts and rarity in self.counts[mob_type]:
            self.counts[mob_type][rarity] += 1

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        col   = (130, 175, 255) if hover else (85, 125, 215)
        pygame.draw.circle(screen, (10, 10, 10),
                           (self.rect.centerx + 2, self.rect.centery + 2), 23)
        pygame.draw.circle(screen, (20, 20, 20), self.rect.center, 23)
        pygame.draw.circle(screen, col,          self.rect.center, 20)
        cx, cy = self.rect.center
        pygame.draw.rect(screen, (255, 255, 255), (cx - 7, cy - 8, 14, 16), 2, border_radius=2)
        for dy2 in (-3, 1, 5):
            pygame.draw.line(screen, (255, 255, 255), (cx - 4, cy + dy2), (cx + 4, cy + dy2), 1)
        if hover:
            tip  = self.f_tip.render("Bestiary", True, (255, 255, 255))
            trec = tip.get_rect(midleft=(self.rect.right + 8, self.rect.centery))
            pygame.draw.rect(screen, (30, 30, 30), trec.inflate(10, 6), border_radius=5)
            screen.blit(tip, trec)

    def draw_menu(self, screen):
        if not self.menu_open:
            return
        from mobs import RARITY_COLORS
        col_start = 130
        col_step  = 72
        menu_w    = col_start + len(self.RARITIES) * col_step + 16
        menu_h    = 95 + len(self.MOB_TYPES) * 52
        panel     = pygame.Rect(0, 0, menu_w, menu_h)
        panel.center = (screen.get_width() // 2, screen.get_height() // 2)

        pygame.draw.rect(screen, (0, 0, 0), panel.inflate(8, 8), border_radius=16)
        pygame.draw.rect(screen, (18, 20, 28), panel, border_radius=16)
        pygame.draw.rect(screen, (65, 70, 110), panel, 2, border_radius=16)

        title = self.f_title.render("[ Bestiary ]", True, (200, 210, 255))
        screen.blit(title, (panel.left + 16, panel.top + 10))
        pygame.draw.line(screen, (50, 54, 82),
                         (panel.left + 12, panel.top + 44),
                         (panel.right - 12, panel.top + 44), 1)

        for i, r in enumerate(self.RARITIES):
            lbl = self.f_sm.render(r, True, RARITY_COLORS.get(r, (255, 255, 255)))
            screen.blit(lbl, lbl.get_rect(
                center=(panel.left + col_start + i * col_step, panel.top + 60)))

        for ri, mob in enumerate(self.MOB_TYPES):
            ry2   = panel.top + 78 + ri * 52
            icon  = "🐝" if mob == "Bee" else "🐞"
            ml    = self.f_mob.render(f"{mob}", True, (210, 215, 230))
            screen.blit(ml, (panel.left + 14, ry2 + 8))
            for ci, rarity in enumerate(self.RARITIES):
                count = self.counts[mob].get(rarity, 0)
                cell  = pygame.Rect(panel.left + col_start + ci * col_step - 26,
                                    ry2, 52, 34)
                bg = (42, 48, 62) if count > 0 else (26, 28, 36)
                pygame.draw.rect(screen, bg, cell, border_radius=6)
                if count > 0:
                    pygame.draw.rect(screen, RARITY_COLORS.get(rarity, (80, 80, 80)),
                                     cell, 1, border_radius=6)
                val = self.f_sm.render(str(count), True,
                                       (235, 235, 235) if count > 0 else (50, 55, 68))
                screen.blit(val, val.get_rect(center=cell.center))

        hint = self.f_tip.render("click index to close", True, (65, 70, 95))
        screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 14)))


# ══════════════════════════════════════════════════════════════════
#  INVENTORY MENU
#  inventory key = (petal_type, rarity)  e.g. ("Glass", "Common")
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
#  PETAL TOOLTIP  (shown on hover in hotbar and inventory)
# ══════════════════════════════════════════════════════════════════

_TIP_FONT_TITLE = None
_TIP_FONT_BODY  = None

def _draw_petal_tooltip(screen, mouse_pos, petal_type, rarity, damage, reload_frames):
    """Draw a florr.io-style hover tooltip for a petal."""
    global _TIP_FONT_TITLE, _TIP_FONT_BODY
    if _TIP_FONT_TITLE is None:
        _TIP_FONT_TITLE = pygame.font.SysFont("segoeui", 14, bold=True)
        _TIP_FONT_BODY  = pygame.font.SysFont("segoeui", 12)

    from petals import petal_special, petal_description, PETAL_TYPES
    from mobs import RARITY_COLORS

    rc      = RARITY_COLORS.get(rarity, (200, 200, 200))
    special = petal_special(petal_type)
    desc    = petal_description(petal_type)

    reload_s = f"{reload_frames / 60:.2f}s"
    if damage > 0:
        dmg_str = f"{damage:.1f}"
    else:
        dmg_str = "0  (utility)"

    lines = [
        (f"{petal_type}  [{rarity}]", rc, True),
        (f"Damage:  {dmg_str}", (200, 210, 220), False),
        (f"Reload:  {reload_s}", (180, 195, 215), False),
    ]
    if special:
        lines.append((f"Special: {special}", (255, 220, 80), False))
    if desc:
        lines.append((desc, (155, 165, 185), False))

    pad   = 8
    w     = 185
    lh    = 17
    h     = pad * 2 + len(lines) * lh

    mx, my = mouse_pos
    tx     = mx + 14
    ty     = my - h - 4
    sw, sh = screen.get_width(), screen.get_height()
    tx     = max(4, min(tx, sw - w - 4))
    ty     = max(4, min(ty, sh - h - 4))

    pygame.draw.rect(screen, (8, 10, 16),  (tx - 2, ty - 2, w + 4, h + 4), border_radius=8)
    pygame.draw.rect(screen, (20, 22, 32), (tx, ty, w, h), border_radius=8)
    pygame.draw.rect(screen, rc,           (tx, ty, w, h), 1, border_radius=8)

    for i, (text, col, bold) in enumerate(lines):
        fn   = _TIP_FONT_TITLE if bold else _TIP_FONT_BODY
        surf = fn.render(text, True, col)
        screen.blit(surf, (tx + pad, ty + pad + i * lh))

def _draw_petal_icon(screen, cx, cy, petal_type, rarity_color, size=14):
    """Draw a small petal icon centred at (cx, cy)."""
    if petal_type == "Bubble":
        bsurf = pygame.Surface((size * 2 + 6, size * 2 + 6), pygame.SRCALPHA)
        bx, by = size + 3, size + 3
        pygame.draw.circle(bsurf, (55, 62, 68, 180),    (bx, by), size + 2)
        pygame.draw.circle(bsurf, (148, 158, 165, 110), (bx, by), size)
        pygame.draw.circle(bsurf, (*rarity_color, 150), (bx, by), size, 2)
        screen.blit(bsurf, (cx - size - 3, cy - size - 3))
    elif petal_type == "Lightning":
        pygame.draw.circle(screen, (20, 25, 55),     (cx, cy), size + 2)
        pygame.draw.circle(screen, (70, 115, 210),   (cx, cy), size)
        pygame.draw.circle(screen, (200, 220, 255),  (cx, cy), size - 4)
    elif petal_type == "Light":
        pygame.draw.circle(screen, (30, 30, 30),     (cx, cy), size + 2)
        pygame.draw.circle(screen, rarity_color,     (cx, cy), size + 1)
        pygame.draw.circle(screen, (240, 245, 255),  (cx, cy), size - 1)
    else:  # Glass
        pygame.draw.circle(screen, (30, 30, 30),     (cx, cy), size + 2)
        pygame.draw.circle(screen, rarity_color,     (cx, cy), size)
        pygame.draw.circle(screen, (255, 245, 160),  (cx, cy), size - 4)


class InventoryMenu(SlidingMenu):
    SLOT_W = 70
    SLOT_H = 72
    PAD    = 6

    def __init__(self, screen_height):
        super().__init__(screen_height, "Inventory", "[I]")
        self.font_cnt  = pygame.font.SysFont("segoeui", 12, bold=True)
        self.font_rar  = pygame.font.SysFont("segoeui", 10)
        self.font_type = pygame.font.SysFont("segoeui", 10, bold=True)

    def _slot_rect(self, i):
        cols = max(1, (self.width - 16) // (self.SLOT_W + self.PAD))
        col  = i % cols
        row  = i // cols
        return pygame.Rect(
            self.x + 8 + col * (self.SLOT_W + self.PAD),
            self.y + 58 + row * (self.SLOT_H + self.PAD),
            self.SLOT_W, self.SLOT_H)

    def handle_click(self, mouse_pos, player):
        if not self.visible:
            return None
        for i, key in enumerate(player.inventory):
            if player.inventory[key] > 0 and self._slot_rect(i).collidepoint(mouse_pos):
                return key   # returns (petal_type, rarity) tuple
        return None

    def draw(self, screen, player):
        self.draw_panel(screen)
        if self.x < -self.width + 10:
            return
        from mobs import RARITY_COLORS
        for i, (key, count) in enumerate(player.inventory.items()):
            if count <= 0:
                continue
            ptype, rarity = key
            rect  = self._slot_rect(i)
            color = RARITY_COLORS.get(rarity, (200, 200, 200))
            dark  = tuple(max(0, c - 80) for c in color)

            pygame.draw.rect(screen, dark,  rect, border_radius=10)
            pygame.draw.rect(screen, color, rect, 2, border_radius=10)

            cx, cy = rect.centerx, rect.centery - 6
            _draw_petal_icon(screen, cx, cy, ptype, color, 14)

            # Petal type label
            ts = self.font_type.render(ptype, True, (200, 205, 220))
            screen.blit(ts, ts.get_rect(centerx=rect.centerx, top=cy + 18))

            # Rarity label
            rs = self.font_rar.render(rarity, True, color)
            screen.blit(rs, rs.get_rect(centerx=rect.centerx, top=cy + 29))

            # Count badge
            cs = self.font_cnt.render(f"x{count}", True, (255, 255, 255))
            screen.blit(cs, (rect.right - cs.get_width() - 3, rect.top + 2))

        # ── Petal tooltip on hover ────────────────────────────────────
        if self.visible:
            mouse_pos = pygame.mouse.get_pos()
            for i, (key, count) in enumerate(player.inventory.items()):
                rect = self._slot_rect(i)
                if rect.collidepoint(mouse_pos):
                    ptype, rarity = key
                    from petals import Petal
                    dmg = Petal._MULTIPLIERS.get(rarity, 1.0) * __import__("petals").petal_base_damage(ptype)
                    from petals import petal_reload_base, Petal as _P
                    rt  = max(4, int(petal_reload_base(ptype) * _P._RELOAD_MULTIPLIERS.get(rarity, 1.0)))
                    _draw_petal_tooltip(screen, mouse_pos, ptype, rarity, dmg, rt)
                    break


# ══════════════════════════════════════════════════════════════════
#  CRAFT MENU
# ══════════════════════════════════════════════════════════════════

class CraftMenu(SlidingMenu):
    TIERS = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super", "Unique"]
    RATES = [32, 16, 8, 4, 2, 1, 100]

    SLOT_W = 70
    SLOT_H = 72
    PAD    = 6

    def __init__(self, screen_height):
        super().__init__(screen_height, "Craft", "[C]")
        self.selected_key    = None   # (petal_type, rarity) or None
        self.is_spinning     = False
        self.spin_angle      = 0.0
        self.spin_timer      = 0

        self.font_btn  = pygame.font.SysFont("segoeui", 16, bold=True)
        self.font_item = pygame.font.SysFont("segoeui", 10, bold=True)
        self.font_pct  = pygame.font.SysFont("segoeui", 14)
        self.font_rar  = pygame.font.SysFont("segoeui", 10)
        self.font_type = pygame.font.SysFont("segoeui", 10, bold=True)

    def update(self):
        super().update()
        if self.is_spinning:
            self.spin_angle += 14
            self.spin_timer -= 1
            if self.spin_timer <= 0:
                self.is_spinning = False

    def _slot_rect(self, i):
        cols = max(1, (self.width - 16) // (self.SLOT_W + self.PAD))
        col  = i % cols
        row  = i // cols
        return pygame.Rect(
            self.x + 8 + col * (self.SLOT_W + self.PAD),
            self.y + 58 + row * (self.SLOT_H + self.PAD),
            self.SLOT_W, self.SLOT_H)

    def _btn_rect(self):
        return pygame.Rect(int(self.x) + 50, self.y + 315, 210, 40)

    def handle_click(self, mouse_pos, player):
        if not self.visible or self.is_spinning:
            return
        available = [(k, v) for k, v in player.inventory.items() if v > 0]
        for i, (key, _) in enumerate(available):
            if self._slot_rect(i).collidepoint(mouse_pos):
                self.selected_key = key
                return
        if self._btn_rect().collidepoint(mouse_pos) and self.selected_key:
            if player.inventory.get(self.selected_key, 0) >= 5:
                # Check if rarity can be upgraded
                _, rarity = self.selected_key
                if rarity in self.TIERS and self.TIERS.index(rarity) < len(self.TIERS) - 1:
                    self.is_spinning = True
                    self.spin_timer  = 120

    def draw(self, screen, player):
        self.draw_panel(screen)
        if self.x < -self.width + 10:
            return
        from mobs import RARITY_COLORS

        available = [(k, v) for k, v in player.inventory.items() if v > 0]
        for i, (key, count) in enumerate(available):
            ptype, rarity = key
            rect  = self._slot_rect(i)
            color = RARITY_COLORS.get(rarity, (200, 200, 200))
            dark  = tuple(max(0, c - 80) for c in color)

            pygame.draw.rect(screen, dark, rect, border_radius=9)
            sel   = (key == self.selected_key)
            bcol2 = (255, 255, 255) if sel else color
            bw2   = 3 if sel else 2
            pygame.draw.rect(screen, bcol2, rect, bw2, border_radius=9)

            cx2, cy2 = rect.centerx, rect.centery - 6
            _draw_petal_icon(screen, cx2, cy2, ptype, color, 13)

            ts = self.font_type.render(ptype, True, (200, 205, 220))
            screen.blit(ts, ts.get_rect(centerx=rect.centerx, top=cy2 + 17))
            rs2 = self.font_rar.render(rarity, True, color)
            screen.blit(rs2, rs2.get_rect(centerx=rect.centerx, top=cy2 + 28))
            cs2 = self.font_item.render(f"x{count}", True, (255, 255, 255))
            screen.blit(cs2, (rect.right - cs2.get_width() - 2, rect.top + 2))

        # Spinning preview
        cx3  = int(self.x + self.width // 2)
        cy3  = self.y + 240
        has5 = (self.selected_key is not None
                and player.inventory.get(self.selected_key, 0) >= 5)
        if self.selected_key:
            ptype3, rarity3 = self.selected_key
            sc3 = RARITY_COLORS.get(rarity3, (150, 150, 150))
        else:
            ptype3, sc3 = "Glass", (80, 80, 90)

        pygame.draw.circle(screen, (35, 38, 50), (cx3, cy3), 52, 1)
        for i in range(5):
            a  = math.radians(i * 72 + self.spin_angle)
            px3 = int(cx3 + math.cos(a) * 40)
            py3 = int(cy3 + math.sin(a) * 40)
            if has5:
                _draw_petal_icon(screen, px3, py3, ptype3, sc3, 13)
            else:
                pygame.draw.circle(screen, (20, 20, 20), (px3, py3), 15)
                pygame.draw.circle(screen, (45, 48, 60),  (px3, py3), 13)

        # Craft button
        can   = has5 and not self.is_spinning
        brect = self._btn_rect()
        bcol4 = (118, 72, 200) if can else (45, 45, 55)
        pygame.draw.rect(screen, (12, 12, 12), brect.move(2, 2), border_radius=10)
        pygame.draw.rect(screen, bcol4, brect, border_radius=10)
        if can:
            pygame.draw.rect(screen, (175, 135, 255), brect, 2, border_radius=10)
        bt = self.font_btn.render("[ CRAFT ]", True, (255, 255, 255))
        screen.blit(bt, bt.get_rect(center=brect.center))

        # Success label
        if self.selected_key:
            _, rarity4 = self.selected_key
            if rarity4 in self.TIERS:
                idx4 = self.TIERS.index(rarity4)
                if idx4 < len(self.TIERS) - 1:
                    pt  = f"{self.RATES[idx4]}%  →  {self.TIERS[idx4 + 1]}"
                    pc  = ((150, 255, 160) if self.RATES[idx4] >= 16
                           else (255, 230, 100) if self.RATES[idx4] >= 4
                           else (255, 110, 110))
                else:
                    pt, pc = "MAX TIER", (255, 100, 100)
                ps = self.font_pct.render(pt, True, pc)
                screen.blit(ps, ps.get_rect(center=(int(self.x + self.width // 2),
                                                     self.y + 368)))


# ══════════════════════════════════════════════════════════════════
#  HOTBAR
# ══════════════════════════════════════════════════════════════════

class Hotbar:
    def __init__(self, screen_height, screen_width=800, num_slots=5):
        self.num_slots = num_slots
        self.slot_size = 62
        self.padding   = 10
        self.screen_w  = screen_width
        self.screen_h  = screen_height
        self.font_num  = pygame.font.SysFont("segoeui", 12, bold=True)
        self.font_name = pygame.font.SysFont("segoeui", 10, bold=True)

    def _origin(self):
        total_w = self.num_slots * (self.slot_size + self.padding) - self.padding
        return (self.screen_w - total_w) // 2, self.screen_h - self.slot_size - 24

    def _slot_rect(self, i):
        x, y = self._origin()
        return pygame.Rect(x + i * (self.slot_size + self.padding), y,
                           self.slot_size, self.slot_size)

    def get_slot_clicked(self, mouse_pos):
        for i in range(self.num_slots):
            if self._slot_rect(i).collidepoint(mouse_pos):
                return i
        return None

    def draw(self, screen, petals):
        from mobs import RARITY_COLORS
        for i in range(self.num_slots):
            rect     = self._slot_rect(i)
            p_exists = i < len(petals)
            rcol     = petals[i].rarity_color if p_exists else (70, 72, 85)
            dark     = tuple(max(0, c - 70) for c in rcol)
            bcol     = rcol if p_exists else (55, 58, 72)

            pygame.draw.rect(screen, (0, 0, 0), rect.move(3, 3), border_radius=12)
            pygame.draw.rect(screen, dark, rect, border_radius=12)
            pygame.draw.rect(screen, bcol, rect, 3, border_radius=12)

            if p_exists:
                p   = petals[i]
                cnt = p.count
                cx2, cy2 = rect.centerx, rect.centery - 6

                if cnt == 1:
                    _draw_petal_icon(screen, cx2, cy2, p.petal_type, rcol, 18)
                elif cnt == 2:
                    _draw_petal_icon(screen, cx2 - 9, cy2, p.petal_type, rcol, 13)
                    _draw_petal_icon(screen, cx2 + 9, cy2, p.petal_type, rcol, 13)
                else:  # 3
                    _draw_petal_icon(screen, cx2,      cy2 - 8,  p.petal_type, rcol, 11)
                    _draw_petal_icon(screen, cx2 - 10, cy2 + 6,  p.petal_type, rcol, 11)
                    _draw_petal_icon(screen, cx2 + 10, cy2 + 6,  p.petal_type, rcol, 11)

                # Petal type + rarity
                ts = self.font_name.render(f"{p.petal_type}", True, (220, 222, 235))
                screen.blit(ts, ts.get_rect(centerx=rect.centerx, bottom=rect.bottom - 4))

            ns2 = self.font_num.render(str(i + 1), True, (140, 145, 170))
            screen.blit(ns2, (rect.x + 4, rect.y + 3))


# ══════════════════════════════════════════════════════════════════
#  SETTINGS MENU
# ══════════════════════════════════════════════════════════════════

class SettingsMenu:
    OPTIONS = ["[W] WASD Movement", "[M] Mouse Follow"]

    def __init__(self, width=320, height=260):
        self.width, self.height = width, height
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (400, 300)
        self.selected = 0
        self.visible  = False
        self.f_title  = pygame.font.SysFont("segoeui", 20, bold=True)
        self.f_opt    = pygame.font.SysFont("segoeui", 16, bold=True)

    def toggle(self): self.visible = not self.visible

    def _option_rect(self, i):
        return pygame.Rect(self.rect.left + 20,
                           self.rect.top + 70 + i * 60,
                           self.width - 40, 44)

    def handle_event(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(self.OPTIONS)):
                if self._option_rect(i).collidepoint(event.pos):
                    self.selected = i

    def draw(self, screen):
        if not self.visible: return
        pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(8, 8), border_radius=14)
        pygame.draw.rect(screen, (22, 24, 34), self.rect, border_radius=14)
        pygame.draw.rect(screen, (68, 72, 112), self.rect, 2, border_radius=14)
        title = self.f_title.render("[ Settings ]", True, (205, 210, 255))
        screen.blit(title, title.get_rect(centerx=self.rect.centerx, top=self.rect.top + 14))
        pygame.draw.line(screen, (50, 55, 85),
                         (self.rect.left + 14, self.rect.top + 52),
                         (self.rect.right - 14, self.rect.top + 52), 1)
        for i, text in enumerate(self.OPTIONS):
            r   = self._option_rect(i)
            sel = (i == self.selected)
            bg  = (52, 165, 90) if sel else (38, 40, 54)
            pygame.draw.rect(screen, (10, 10, 10), r.move(2, 2), border_radius=10)
            pygame.draw.rect(screen, bg, r, border_radius=10)
            if sel: pygame.draw.rect(screen, (100, 240, 140), r, 2, border_radius=10)
            surf = self.f_opt.render(text, True,
                                     (255, 255, 255) if sel else (145, 150, 172))
            screen.blit(surf, surf.get_rect(midleft=(r.left + 12, r.centery)))


# ══════════════════════════════════════════════════════════════════
#  TALENT MENU
# ══════════════════════════════════════════════════════════════════

class TalentMenu:
    BRANCHES = [
        {"label": "Loadout",  "color": (80,  195, 120)},
        {"label": "Health",   "color": (220,  70,  70)},
        {"label": "Reload",   "color": (90,  155, 240)},
        {"label": "Body Dmg", "color": (210, 135,  40)},
    ]
    NODE_W  = 136;  NODE_H  =  60
    COL_GAP = 160;  ROW_GAP =  90
    COLS    =   4;  ROWS    =   3

    def __init__(self, sw, sh):
        self.sw, self.sh = sw, sh
        self.visible     = False
        self._hovered    = None
        self.panel_w     = self.COL_GAP * self.COLS + 60
        self.panel_h     = self.ROW_GAP * (self.ROWS + 1) + 110
        self.px          = (sw - self.panel_w) // 2
        self.py          = (sh - self.panel_h) // 2

        self.f_title  = pygame.font.SysFont("segoeui", 21, bold=True)
        self.f_branch = pygame.font.SysFont("segoeui", 14, bold=True)
        self.f_node   = pygame.font.SysFont("segoeui", 11, bold=True)
        self.f_sub    = pygame.font.SysFont("segoeui", 10)
        self.f_tip    = pygame.font.SysFont("segoeui", 12)
        self.f_sp     = pygame.font.SysFont("segoeui", 13, bold=True)

    def toggle(self):
        self.visible  = not self.visible
        if not self.visible: self._hovered = None

    def _node_rect(self, col, row):
        cx = self.px + 30 + col * self.COL_GAP + (self.COL_GAP - self.NODE_W) // 2
        cy = self.py + 88 + row * self.ROW_GAP
        return pygame.Rect(cx, cy, self.NODE_W, self.NODE_H)

    def _close_rect(self):
        return pygame.Rect(self.px + self.panel_w - 32, self.py + 8, 24, 24)

    def handle_event(self, event, player):
        if not self.visible: return
        from player import TALENT_TREE
        if event.type == pygame.MOUSEMOTION:
            self._hovered = None
            for tid, t in TALENT_TREE.items():
                if self._node_rect(t["col"], t["row"]).collidepoint(event.pos):
                    self._hovered = tid; break
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._close_rect().collidepoint(event.pos):
                self.visible = False; self._hovered = None; return
            for tid, t in TALENT_TREE.items():
                if self._node_rect(t["col"], t["row"]).collidepoint(event.pos):
                    player.spend_talent(tid); return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            self.visible = False; self._hovered = None

    def draw(self, screen, player):
        if not self.visible: return
        from player import TALENT_TREE

        # Dark overlay
        ov = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        screen.blit(ov, (0, 0))

        # Panel
        pygame.draw.rect(screen, (0, 0, 0),
                         (self.px - 4, self.py - 4, self.panel_w + 8, self.panel_h + 8),
                         border_radius=18)
        pygame.draw.rect(screen, (15, 17, 24),
                         (self.px, self.py, self.panel_w, self.panel_h),
                         border_radius=16)
        pygame.draw.rect(screen, (52, 57, 92),
                         (self.px, self.py, self.panel_w, self.panel_h),
                         2, border_radius=16)

        # Title + SP
        title = self.f_title.render("Talents", True, (208, 214, 255))
        screen.blit(title, (self.px + 18, self.py + 12))
        sp = self.f_sp.render(f"Skill Points: {player.skill_points}", True, (255, 218, 55))
        screen.blit(sp, sp.get_rect(right=self.px + self.panel_w - 42, centery=self.py + 24))
        pygame.draw.line(screen, (42, 47, 76),
                         (self.px + 12, self.py + 48),
                         (self.px + self.panel_w - 12, self.py + 48), 1)

        # Close button
        cr = self._close_rect()
        hc = cr.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (85, 28, 28) if hc else (55, 20, 20), cr, border_radius=6)
        cl = self.f_branch.render("X", True, (235, 95, 95))
        screen.blit(cl, cl.get_rect(center=cr.center))

        # Branch headers
        for col, branch in enumerate(self.BRANCHES):
            cx2 = self.px + 30 + col * self.COL_GAP + self.COL_GAP // 2
            lbl = self.f_branch.render(branch["label"], True, branch["color"])
            screen.blit(lbl, lbl.get_rect(centerx=cx2, top=self.py + 54))

        # Connector lines
        for tid, t in TALENT_TREE.items():
            req = t["requires"]
            if req is None: continue
            rt    = TALENT_TREE[req]
            topr  = self._node_rect(rt["col"], rt["row"])
            botr  = self._node_rect(t["col"],  t["row"])
            maxed = player.talents[req] >= rt["max_ranks"]
            lc    = t["branch_color"] if maxed else (40, 44, 58)
            pygame.draw.line(screen, lc, topr.midbottom, botr.midtop, 2)

        # Nodes
        for tid, t in TALENT_TREE.items():
            rect    = self._node_rect(t["col"], t["row"])
            rank    = player.talents[tid]
            maxr    = t["max_ranks"]
            can     = player.can_unlock(tid)
            maxed   = rank >= maxr
            hov     = (self._hovered == tid)
            color   = t["branch_color"]
            cost_n  = player.next_rank_cost(tid)

            if maxed:
                bg  = tuple(max(0, c - 55) for c in color); bdr = color; bw = 3
            elif can:
                bg  = (44, 48, 64) if hov else (32, 35, 48); bdr = color; bw = 2
            else:
                bg  = (18, 20, 27); bdr = (38, 42, 55); bw = 1

            pygame.draw.rect(screen, (0, 0, 0), rect.move(2, 2), border_radius=10)
            pygame.draw.rect(screen, bg,  rect, border_radius=10)
            pygame.draw.rect(screen, bdr, rect, bw, border_radius=10)

            lbl_col = (210, 215, 235) if (can or maxed) else (78, 82, 98)
            lbl = self.f_node.render(t["label"], True, lbl_col)
            screen.blit(lbl, lbl.get_rect(centerx=rect.centerx, top=rect.top + 6))

            # Pips
            pw, pg  = 11, 3
            ptot    = maxr
            psx     = rect.centerx - (ptot * (pw + pg) - pg) // 2
            for ii in range(ptot):
                px2 = psx + ii * (pw + pg)
                py2 = rect.bottom - 13
                pc  = color if ii < rank else (32, 35, 50)
                pygame.draw.rect(screen, pc, (px2, py2, pw, 6), border_radius=3)
                if ii < rank:
                    pygame.draw.rect(screen, tuple(min(255, c + 52) for c in pc),
                                     (px2, py2, pw, 3), border_radius=2)

            # Cost / MAX
            if maxed:
                ms = self.f_sub.render("MAX", True, color)
                screen.blit(ms, (rect.right - ms.get_width() - 3, rect.top + 3))
            elif cost_n > 0:
                cc2 = (252, 216, 55) if can else (75, 78, 92)
                cs3 = self.f_sub.render(f"{cost_n} SP", True, cc2)
                screen.blit(cs3, (rect.right - cs3.get_width() - 3, rect.top + 3))

        # Tooltip
        if self._hovered and self._hovered in TALENT_TREE:
            t    = TALENT_TREE[self._hovered]
            rect = self._node_rect(t["col"], t["row"])
            rank = player.talents[self._hovered]
            cost = player.next_rank_cost(self._hovered)
            lines = [t["label"], t["desc"],
                     f"Rank {rank} / {t['max_ranks']}",
                     f"Next: {cost} SP" if cost else "MAXED"]
            req2 = t["requires"]
            if req2 and player.talents[req2] < TALENT_TREE[req2]["max_ranks"]:
                lines.append(f"Req: {TALENT_TREE[req2]['label']} maxed")
            tw  = 205;  th = 10 + len(lines) * 18
            tx  = min(rect.right + 10, self.sw - tw - 10)
            ty  = max(self.py + 8, rect.top)
            if ty + th > self.py + self.panel_h - 8: ty = self.py + self.panel_h - th - 8
            pygame.draw.rect(screen, (7, 9, 14),  (tx - 2, ty - 2, tw + 4, th + 4), border_radius=8)
            pygame.draw.rect(screen, (22, 24, 34),(tx, ty, tw, th), border_radius=8)
            pygame.draw.rect(screen, t["branch_color"], (tx, ty, tw, th), 1, border_radius=8)
            for ii, line in enumerate(lines):
                lc2 = (212, 218, 255) if ii == 0 \
                      else t["branch_color"] if ii == 1 \
                      else (148, 154, 182)
                ls = self.f_tip.render(line, True, lc2)
                screen.blit(ls, (tx + 7, ty + 5 + ii * 18))

        # Footer
        hint = self.f_sub.render("Click node to spend SP  |  [T] or X to close",
                                 True, (50, 55, 82))
        screen.blit(hint, hint.get_rect(
            centerx=self.px + self.panel_w // 2, bottom=self.py + self.panel_h - 7))