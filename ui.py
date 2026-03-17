import pygame
import random
import math

# --- BASE CLASSES ---

class SideButton:
    """Circular button style used in florr.io"""
    def __init__(self, x, y, icon_text, color):
        self.rect = pygame.Rect(x, y, 52, 52)
        self.icon_text = icon_text
        self.color = color
        self.font = pygame.font.SysFont("arial", 28, bold=True)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.circle(screen, (20, 20, 20), self.rect.center, 26)
        draw_col = [min(255, c + 30) for c in self.color] if hover else self.color
        pygame.draw.circle(screen, draw_col, self.rect.center, 22)
        txt = self.font.render(self.icon_text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

class SlidingMenu:
    """Semi-transparent glass panel logic"""
    def __init__(self, screen_height, title):
        self.width, self.height = 320, 450
        self.x, self.target_x = -320, -320
        self.y = (screen_height - 450) // 2
        self.visible = False
        self.title = title
        self.title_font = pygame.font.SysFont("arial", 30, bold=True)

    def toggle(self):
        self.visible = not self.visible
        self.target_x = 10 if self.visible else -self.width

    def update(self):
        self.x += (self.target_x - self.x) * 0.2

    def draw_panel(self, screen):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30, 30, 35, 195), (0, 0, self.width, self.height), border_top_right_radius=20, border_bottom_right_radius=20)
        pygame.draw.rect(surf, (255, 255, 255, 40), (0, 0, self.width, self.height), 2, border_top_right_radius=20, border_bottom_right_radius=20)
        screen.blit(surf, (self.x, self.y))
        title_surf = self.title_font.render(self.title, True, (255, 255, 255))
        screen.blit(title_surf, (self.x + 25, self.y + 25))

# --- BUTTONS ---

class InventoryButton(SideButton):
    def __init__(self, screen_height):
        super().__init__(15, screen_height - 145, "I", (85, 145, 200))

class CraftButton(SideButton):
    def __init__(self, screen_height):
        super().__init__(15, screen_height - 75, "C", (140, 90, 210))

class CogButton:
    def __init__(self, x=15, y=15, size=40):
        self.rect = pygame.Rect(x,y,size,size)
    def draw(self, screen):
        pygame.draw.circle(screen,(0,0,0),self.rect.center,(self.rect.width//2)+2)
        pygame.draw.circle(screen,(150,150,150),self.rect.center,self.rect.width//2)
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- MENUS ---

class InventoryMenu(SlidingMenu):
    def __init__(self, screen_height):
        super().__init__(screen_height, "Inventory")
        self.slot_size = 58
        self.padding = 10

    def handle_click(self, mouse_pos, player):
        if not self.visible: return None
        items = list(player.inventory.items())
        for i, (rarity, count) in enumerate(items):
            col, row = i % 4, i // 4
            slot_rect = pygame.Rect(self.x + 25 + col * (self.slot_size + self.padding), 
                                    self.y + 85 + row * (self.slot_size + self.padding), 
                                    self.slot_size, self.slot_size)
            if slot_rect.collidepoint(mouse_pos) and count > 0:
                return rarity
        return None

    def draw(self, screen, player):
        self.draw_panel(screen)
        if self.x < -self.width + 10: return
        from mobs import Bee 
        for i, (rarity, count) in enumerate(player.inventory.items()):
            col, row = i % 4, i // 4
            sx = self.x + 25 + col * (self.slot_size + self.padding)
            sy = self.y + 85 + row * (self.slot_size + self.padding)
            color = Bee.RARITY_COLORS.get(rarity, (255, 255, 255))
            
            pygame.draw.rect(screen, color, (sx, sy, self.slot_size, self.slot_size), border_radius=10)
            pygame.draw.circle(screen, (40, 40, 40), (sx + 29, sy + 29), 18)
            pygame.draw.circle(screen, color, (sx + 29, sy + 29), 15)
            
            cnt = pygame.font.SysFont("arial", 13, bold=True).render(f"x{count}", True, (255, 255, 255))
            screen.blit(cnt, (sx + 36, sy + 40))

class IndexButton:
    def __init__(self, cog_button, size=40):
        self.size = size
        self.rect = pygame.Rect(cog_button.rect.right + 10, cog_button.rect.top, size, size)
        self.menu_open = False
        self.mobs_list = ["Bee"] 
        self.rarities = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        self.kill_counts = {mob: {r: 0 for r in self.rarities} for mob in self.mobs_list}

    def increment(self, rarity, mob_type="Bee"):
        if mob_type in self.kill_counts and rarity in self.kill_counts[mob_type]:
            self.kill_counts[mob_type][rarity] += 1

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, (self.size // 2) + 2)
        pygame.draw.circle(screen, (100, 150, 255), self.rect.center, self.size // 2)
        cx, cy = self.rect.center
        pygame.draw.rect(screen, (255,255,255), (cx-8, cy-8, 16, 16), 2)

    def draw_menu(self, screen):
        if not self.menu_open: return
        from mobs import Bee
        menu_w, menu_h = 700, 450
        panel = pygame.Rect(0, 0, menu_w, menu_h)
        panel.center = (screen.get_width()//2, screen.get_height()//2)
        pygame.draw.rect(screen, (0,0,0), panel.inflate(8,8), border_radius=15)
        pygame.draw.rect(screen, (30,30,35), panel, border_radius=15)
        
        font_sm = pygame.font.SysFont("arial", 14, bold=True)
        for i, rarity in enumerate(self.rarities):
            color = Bee.RARITY_COLORS.get(rarity, (255, 255, 255))
            lbl = font_sm.render(rarity, True, color)
            screen.blit(lbl, lbl.get_rect(center=(panel.left + 160 + i*80, panel.top + 40)))

        for r_idx, mob in enumerate(self.mobs_list):
            mob_lbl = pygame.font.SysFont("arial", 20, bold=True).render(mob, True, (255,255,255))
            screen.blit(mob_lbl, (panel.left + 30, panel.top + 80 + r_idx*60))
            for c_idx, rarity in enumerate(self.rarities):
                count = self.kill_counts[mob][rarity]
                cell = pygame.Rect(panel.left + 130 + c_idx*80, panel.top + 75 + r_idx*60, 60, 35)
                pygame.draw.rect(screen, (50, 50, 60) if count > 0 else (40, 40, 45), cell, border_radius=5)
                val = font_sm.render(str(count), True, (255,255,255) if count > 0 else (80,80,80))
                screen.blit(val, val.get_rect(center=cell.center))

# --- HUD ELEMENTS ---

class Hotbar:
    def __init__(self, screen_height, num_slots=5):
        self.num_slots = num_slots
        self.slot_size = 60
        self.padding = 10
        self.x = (800 // 2) - ((self.num_slots * (self.slot_size + self.padding)) // 2)
        self.y = screen_height - self.slot_size - 30
        self.font = pygame.font.SysFont("arial", 12, bold=True)

    def get_slot_clicked(self, mouse_pos):
        for i in range(self.num_slots):
            rect = pygame.Rect(self.x + i * (self.slot_size + self.padding), self.y, self.slot_size, self.slot_size)
            if rect.collidepoint(mouse_pos): return i
        return None

    def draw(self, screen, petals):
        for i in range(self.num_slots):
            slot_x = self.x + i * (self.slot_size + self.padding)
            rect = pygame.Rect(slot_x, self.y, self.slot_size, self.slot_size)
            
            p_exists = i < len(petals)
            rarity_color = petals[i].rarity_color if p_exists else (255, 255, 255)
            bg_color = tuple(max(0, c - 60) for c in rarity_color) if p_exists else (45, 45, 50)
            border_col = rarity_color if p_exists else (80, 80, 80)
            
            pygame.draw.rect(screen, (0, 0, 0), rect.inflate(6, 6), border_radius=12)
            pygame.draw.rect(screen, bg_color, rect, border_radius=10)
            pygame.draw.rect(screen, border_col, rect, width=3, border_radius=10)
            
            if p_exists:
                pygame.draw.circle(screen, (40, 40, 40), rect.center, 18)
                pygame.draw.circle(screen, rarity_color, rect.center, 16)
                name_surf = self.font.render("Glass", True, (255, 255, 255))
                screen.blit(name_surf, name_surf.get_rect(midbottom=(rect.centerx, rect.bottom - 4)))

            num_surf = self.font.render(str(i + 1), True, (200, 200, 200))
            screen.blit(num_surf, (rect.x + 5, rect.y + 2))

# --- CraftMenu & SettingsMenu remain as in previous message ---

import pygame
import random
import math

import pygame
import math
import random

# Assuming SlidingMenu is defined above or imported
class CraftMenu: # Use your existing inheritance: class CraftMenu(SlidingMenu):
    def __init__(self, screen_height):
        # ... your super().__init__ code ...
        self.width = 300
        self.x = -self.width
        self.target_x = -self.width
        self.visible = False
        
        self.slot_size = 58
        self.padding = 10
        self.selected_rarity = None
        self.is_spinning = False
        self.spin_angle = 0
        self.spin_timer = 0
        
        # Updated Tiers and Rates (8 tiers total)
        self.tiers = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super", "Unique"]
        # Rates for: C>R, R>E, E>L, L>M, M>U, U>S, S>Unique
        self.rates = [ 32, 16, 8, 4, 2, 1, 100] 

    def toggle(self):
        self.visible = not self.visible
        self.target_x = 0 if self.visible else -self.width

    def update(self):
        # Sliding logic
        self.x += (self.target_x - self.x) * 0.2
        if self.is_spinning:
            self.spin_angle += 15
            self.spin_timer -= 1
            if self.spin_timer <= 0:
                self.is_spinning = False

    def handle_click(self, mouse_pos, player):
        if not self.visible or self.is_spinning: return
        
        available_items = [(r, c) for r, c in player.inventory.items() if c > 0]
        for i, (rarity, count) in enumerate(available_items):
            col, row = i % 4, i // 4
            slot_rect = pygame.Rect(self.x + 25 + col * (self.slot_size + self.padding), 
                                    85 + row * (self.slot_size + self.padding), 
                                    self.slot_size, self.slot_size)
            if slot_rect.collidepoint(mouse_pos):
                self.selected_rarity = rarity
                return

        btn_rect = pygame.Rect(self.x + 60, 375, 200, 40)
        if btn_rect.collidepoint(mouse_pos) and self.selected_rarity:
            # Check if it's even possible to craft the next tier
            if player.inventory.get(self.selected_rarity, 0) >= 5:
                self.is_spinning = True
                self.spin_timer = 120

    def draw(self, screen, player):
        # Panel Background
        pygame.draw.rect(screen, (40, 40, 40), (self.x, 0, self.width, 600))
        from mobs import Bee

        # 1. Inventory Grid
        available_items = [(r, c) for r, c in player.inventory.items() if c > 0]
        for i, (rarity, count) in enumerate(available_items):
            col, row = i % 4, i // 4
            sx, sy = self.x + 25 + col * (self.slot_size + self.padding), 85 + row * (self.slot_size + self.padding)
            color = Bee.RARITY_COLORS.get(rarity, (255, 255, 255))
            if self.selected_rarity == rarity:
                pygame.draw.rect(screen, (255, 255, 255), (sx-2, sy-2, self.slot_size+4, self.slot_size+4), border_radius=12)
            pygame.draw.rect(screen, color, (sx, sy, self.slot_size, self.slot_size), border_radius=10)
            txt = pygame.font.SysFont("arial", 12, bold=True).render(f"x{count}", True, (255, 255, 255))
            screen.blit(txt, (sx+35, sy+40))

        # 2. 5-Petal Display (Glass Look)
        center_x, center_y = self.x + 150, 300
        has_five = self.selected_rarity and player.inventory.get(self.selected_rarity, 0) >= 5
        if has_five:
            for i in range(5):
                angle = math.radians(i * (360 / 5) + self.spin_angle)
                px, py = center_x + math.cos(angle) * 50, center_y + math.sin(angle) * 50
                pygame.draw.circle(screen, (0, 0, 0), (int(px), int(py)), 18) # Outline
                pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), 16) # White Body

        # 3. Craft Button & Percentage
        can_craft = has_five and not self.is_spinning
        btn_col = (140, 90, 210) if can_craft else (60, 60, 65)
        btn_rect = pygame.Rect(self.x + 50, 375, 200, 40)
        pygame.draw.rect(screen, btn_col, btn_rect, border_radius=10)
        
        btn_txt = pygame.font.SysFont("arial", 18, bold=True).render("CRAFT", True, (255, 255, 255))
        screen.blit(btn_txt, btn_txt.get_rect(center=btn_rect.center))

        # SUCCESS PERCENTAGE LOGIC
        if self.selected_rarity in self.tiers:
            idx = self.tiers.index(self.selected_rarity)
            if idx < len(self.tiers) - 1: # If there is a next tier
                chance = self.rates[idx]
                p_txt = f"Success Chance: {chance}%"
                color = (200, 200, 200)
            else:
                p_txt = "MAX TIER REACHED"
                color = (255, 100, 100)
            
            p_surf = pygame.font.SysFont("arial", 16).render(p_txt, True, color)
            screen.blit(p_surf, p_surf.get_rect(center=(self.x + 150, 430)))
class SettingsMenu:
    def __init__(self, width=300, height=250):
        self.width, self.height = width, height
        self.rect = pygame.Rect(0,0,width,height)
        self.rect.center = (400,300)
        self.font = pygame.font.SysFont("arial",22,bold=True)
        self.options = ["WASD Movement", "Mouse Follow"]
        self.selected = 1
        self.visible = False
        self._generate_option_rects()
    def _generate_option_rects(self):
        self.rendered_options = []
        for i, text_str in enumerate(self.options):
            text_surf = self.font.render(text_str, True, (0,0,0))
            text_rect = text_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top+70+i*60)
            self.rendered_options.append((text_surf,text_rect))
    def toggle(self): self.visible = not self.visible
    def handle_event(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            for i, (_, rect) in enumerate(self.rendered_options):
                if rect.inflate(40,20).collidepoint(event.pos): self.selected = i
    def draw(self, screen):
        if not self.visible: return
        pygame.draw.rect(screen, (0,0,0), self.rect.inflate(6,6), border_radius=12)
        pygame.draw.rect(screen, (240,240,240), self.rect, border_radius=12)
        for i, (surf, rect) in enumerate(self.rendered_options):
            color = (120,240,120) if i==self.selected else (200,200,200)
            pygame.draw.rect(screen,color,rect.inflate(40,15),border_radius=8)
            screen.blit(surf,rect)