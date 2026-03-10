import pygame



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
            slot_x = self.x + i * (self.slot_size + self.padding)
            slot_rect = pygame.Rect(slot_x, self.y, self.slot_size, self.slot_size)
            if slot_rect.collidepoint(mouse_pos):
                return i
        return None

    def draw(self, screen, petals):
        for i in range(self.num_slots):
            slot_x = self.x + i * (self.slot_size + self.padding)
            slot_rect = pygame.Rect(slot_x, self.y, self.slot_size, self.slot_size)
            
            # Default empty colors
            bg_color = (45, 45, 50)
            border_color = (100, 100, 100)
            rarity_color = (255, 255, 255)
            
            # --- RARITY BACKGROUND LOGIC ---
            if i < len(petals):
                p = petals[i]
                rarity_color = p.rarity_color
                # Background becomes a darkened version of the rarity color
                bg_color = tuple(max(0, c - 50) for c in rarity_color)
                border_color = rarity_color
                
                if not p.active: # Cooldown state
                    bg_color = tuple(c // 2 for c in bg_color)
                    border_color = (50, 50, 50)

            # Draw Slot
            pygame.draw.rect(screen, (0, 0, 0), slot_rect.inflate(6, 6), border_radius=12)
            pygame.draw.rect(screen, bg_color, slot_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, slot_rect, width=3, border_radius=10)
            
            if i < len(petals):
                center = slot_rect.center
                pygame.draw.circle(screen, (40, 40, 40), center, 18)
                pygame.draw.circle(screen, rarity_color, center, 16)
                pygame.draw.circle(screen, (255, 240, 150), center, 11)
                
                # Label
                name_surf = self.font.render("Glass", True, (255, 255, 255))
                name_rect = name_surf.get_rect(midbottom=(slot_rect.centerx, slot_rect.bottom - 4))
                label_bg = pygame.Surface((self.slot_size - 10, 12), pygame.SRCALPHA)
                label_bg.fill((0, 0, 0, 100))
                screen.blit(label_bg, (slot_x + 5, name_rect.y))
                screen.blit(name_surf, name_rect)

            num_surf = self.font.render(str(i + 1), True, (200, 200, 200))
            screen.blit(num_surf, (slot_rect.x + 5, slot_rect.y + 2))
class InventoryButton:
    def __init__(self, screen_h):
        # Positioned above the hotbar (Hotbar y is screen_h - 70)
        self.rect = pygame.Rect(20, screen_h - 130, 40, 40)
        self.open = False

    def draw(self, screen):
        # Draw a brown "Bag" icon button
        pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(4, 4), border_radius=8)
        pygame.draw.rect(screen, (139, 69, 19), self.rect, border_radius=8)
        # Simple buckle icon
        pygame.draw.rect(screen, (255, 215, 0), (self.rect.x + 15, self.rect.y + 10, 10, 10), 2)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class InventoryMenu:
    def __init__(self, screen_h):
        self.width = 320
        self.height = 400
        # Positioned off-screen to the left for the sliding effect
        self.rect = pygame.Rect(-self.width, screen_h // 2 - 200, self.width, self.height)
        self.target_x = -self.width
        self.visible = False
        
        # Grid settings
        self.slot_size = 60
        self.padding = 10
        self.cols = 4

    def toggle(self):
        self.visible = not self.visible
        self.target_x = 10 if self.visible else -self.width

    def update(self):
        # Smooth sliding animation logic
        self.rect.x += (self.target_x - self.rect.x) * 0.15

    def handle_click(self, mouse_pos, player):
        """Checks if a specific petal slot was clicked and returns its rarity."""
        if not self.visible:
            return None

        hierarchy = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        # Sort items to match the visual draw order
        items = sorted(player.inventory.items(), key=lambda x: hierarchy.index(x[0]) if x[0] in hierarchy else 0)

        for i, (rarity, count) in enumerate(items):
            row = i // self.cols
            col = i % self.cols
            
            slot_x = self.rect.x + 20 + col * (self.slot_size + self.padding)
            slot_y = self.rect.top + 65 + row * (self.slot_size + self.padding)
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)

            if slot_rect.collidepoint(mouse_pos) and count > 0:
                self.toggle() # Close the inventory automatically
                return rarity # Return the rarity name to main.py
        return None

    def draw(self, screen, player):
        # 1. Main Background Panel
        pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(6, 6), border_radius=15)
        pygame.draw.rect(screen, (35, 35, 40), self.rect, border_radius=15)
        
        font_count = pygame.font.SysFont("arial", 12, bold=True)
        item_label_font = pygame.font.SysFont("arial", 10, bold=True)
        from mobs import Bee 

        hierarchy = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        items = sorted(player.inventory.items(), key=lambda x: hierarchy.index(x[0]) if x[0] in hierarchy else 0)
        
        # Header Title
        title = pygame.font.SysFont("arial", 22, bold=True).render("INVENTORY", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 20, self.rect.top + 20))

        if not items:
            msg = pygame.font.SysFont("arial", 16).render("Your bag is empty...", True, (120, 120, 120))
            screen.blit(msg, (self.rect.x + 20, self.rect.top + 70))

        for i, (rarity, count) in enumerate(items):
            row = i // self.cols
            col = i % self.cols
            
            slot_x = self.rect.x + 20 + col * (self.slot_size + self.padding)
            slot_y = self.rect.top + 65 + row * (self.slot_size + self.padding)
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            
            rarity_color = Bee.RARITY_COLORS.get(rarity, (255, 255, 255))
            
            # --- 1. SLOT BACKGROUND (Rarity Color) ---
            pygame.draw.rect(screen, rarity_color, slot_rect, border_radius=10)
            
            # Darker inner shade for depth
            inner_shade = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
            pygame.draw.rect(inner_shade, (0, 0, 0, 40), (0, 0, self.slot_size, self.slot_size), border_radius=10)
            screen.blit(inner_shade, (slot_x, slot_y))
            
            # --- 2. THE PETAL ICON ---
            pygame.draw.circle(screen, (40, 40, 40), slot_rect.center, 16) 
            pygame.draw.circle(screen, rarity_color, slot_rect.center, 14)
            pygame.draw.circle(screen, (255, 240, 150), slot_rect.center, 10) # Glass color
            
            # --- 3. ITEM NAME ("Glass") ---
            name_surf = item_label_font.render("Glass", True, (255, 255, 255))
            name_rect = name_surf.get_rect(midbottom=(slot_rect.centerx, slot_rect.bottom - 4))
            
            label_bg = pygame.Surface((self.slot_size - 12, 12), pygame.SRCALPHA)
            label_bg.fill((0, 0, 0, 100))
            screen.blit(label_bg, (slot_x + 6, name_rect.y))
            screen.blit(name_surf, name_rect)

            # --- 4. QUANTITY COUNTER ---
            if count > 0:
                count_surf = font_count.render(f"x{count}", True, (255, 255, 255))
                count_rect = count_surf.get_rect(bottomright=(slot_rect.right - 5, slot_rect.bottom - 2))
                screen.blit(count_surf, count_rect)
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

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            for i, (_, rect) in enumerate(self.rendered_options):
                if rect.inflate(40,20).collidepoint(event.pos):
                    self.selected = i

    def draw(self, screen):
        if not self.visible: return
        pygame.draw.rect(screen, (0,0,0), self.rect.inflate(6,6), border_radius=12)
        pygame.draw.rect(screen, (240,240,240), self.rect, border_radius=12)
        for i, (surf, rect) in enumerate(self.rendered_options):
            color = (120,240,120) if i==self.selected else (200,200,200)
            btn_rect = rect.inflate(40,15)
            pygame.draw.rect(screen,(0,0,0),btn_rect.inflate(4,4),border_radius=8)
            pygame.draw.rect(screen,color,btn_rect,border_radius=8)
            screen.blit(surf,rect)

class CogButton:
    def __init__(self, x=15, y=15, size=40):
        self.rect = pygame.Rect(x,y,size,size)
    def draw(self, screen):
        pygame.draw.circle(screen,(0,0,0),self.rect.center,(self.rect.width//2)+2)
        pygame.draw.circle(screen,(150,150,150),self.rect.center,self.rect.width//2)
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class IndexButton:
    def __init__(self, cog_button, size=40):
        self.size = size
        self.rect = pygame.Rect(cog_button.rect.right + 10, cog_button.rect.top, size, size)
        self.menu_open = False
        self.mobs_list = ["Bee"] 
        self.rarities = ["Common", "Rare", "Epic", "Legendary", "Mythic", "Ultra", "Super"]
        self.kill_counts = {mob: {r: 0 for r in self.rarities} for mob in self.mobs_list}
        self.counts = {}

    def increment(self, rarity, mob_type="Bee"):
        if mob_type in self.kill_counts and rarity in self.kill_counts[mob_type]:
            self.kill_counts[mob_type][rarity] += 1

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, (self.size // 2) + 2)
        pygame.draw.circle(screen, (100, 150, 255), self.rect.center, self.size // 2)
        cx, cy = self.rect.center
        icon_rect = pygame.Rect(cx - 8, cy - 8, 16, 16)
        pygame.draw.rect(screen, (255, 255, 255), icon_rect, 2)
        pygame.draw.line(screen, (255, 255, 255), (cx - 4, cy - 3), (cx + 4, cy - 3), 2)
        pygame.draw.line(screen, (255, 255, 255), (cx - 4, cy + 3), (cx + 4, cy + 3), 2)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def draw_menu(self, screen):
        if not self.menu_open: return
        menu_w, menu_h = 700, 450
        panel_rect = pygame.Rect(0, 0, menu_w, menu_h)
        panel_rect.center = (screen.get_width() // 2, screen.get_height() // 2)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect.inflate(8, 8), border_radius=15)
        pygame.draw.rect(screen, (30, 30, 35), panel_rect, border_radius=15)
        font_sm = pygame.font.SysFont("arial", 14, bold=True)
        font_title = pygame.font.SysFont("arial", 22, bold=True)
        
        # Borrow rarity colors for X-axis labels
        from mobs import Bee
        start_x = panel_rect.left + 120
        col_width = 80
        for i, rarity in enumerate(self.rarities):
            color = Bee.RARITY_COLORS.get(rarity, (255, 255, 255))
            label = font_sm.render(rarity, True, color)
            screen.blit(label, label.get_rect(center=(start_x + i * col_width, panel_rect.top + 40)))

        start_y = panel_rect.top + 80
        row_height = 60
        for r_idx, mob_name in enumerate(self.mobs_list):
            mob_label = font_title.render(mob_name, True, (255, 255, 255))
            screen.blit(mob_label, (panel_rect.left + 20, start_y + r_idx * row_height))
            for c_idx, rarity in enumerate(self.rarities):
                cell_rect = pygame.Rect(0, 0, 60, 40)
                cell_rect.center = (start_x + c_idx * col_width, start_y + r_idx * row_height + 15)
                count = self.kill_counts[mob_name][rarity]
                bg_color = (50, 50, 60) if count > 0 else (40, 40, 45)
                pygame.draw.rect(screen, bg_color, cell_rect, border_radius=5)
                count_color = (255, 255, 255) if count > 0 else (80, 80, 80)
                count_surf = font_sm.render(str(count), True, count_color)
                screen.blit(count_surf, count_surf.get_rect(center=cell_rect.center))

class CraftButton:
    def __init__(self, screen_height):
        # Positioned exactly 60 pixels above the inventory button
        self.rect = pygame.Rect(10, screen_height - 120, 50, 50)
        self.font = pygame.font.SysFont("arial", 30, bold=True)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        # Dark circular background
        pygame.draw.circle(screen, (40, 40, 40), self.rect.center, 25)
        pygame.draw.circle(screen, (100, 100, 100), self.rect.center, 22)
        # Hammer or Anvil icon placeholder (C for Craft)
        txt = self.font.render("C", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

class CraftMenu:
    def __init__(self, screen_height):
        self.width = 250
        self.height = 400
        self.x = -self.width # Start off-screen
        self.target_x = -self.width
        self.y = (screen_height - self.height) // 2
        self.visible = False

    def toggle(self):
        self.visible = not self.visible
        self.target_x = 0 if self.visible else -self.width

    def update(self):
        # Sliding animation logic
        self.x += (self.target_x - self.x) * 0.2

    def draw(self, screen):
        # Background panel
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, (30, 30, 30), rect, border_top_right_radius=15, border_bottom_right_radius=15)
        pygame.draw.rect(screen, (200, 200, 200), rect, 3, border_top_right_radius=15, border_bottom_right_radius=15)
        
        # Header text
        header_font = pygame.font.SysFont("arial", 24, bold=True)
        header = header_font.render("CRAFTING", True, (255, 255, 255))
        screen.blit(header, (self.x + 20, self.y + 20))
        
        # Subtitle
        sub_font = pygame.font.SysFont("arial", 16)
        sub = sub_font.render("Coming Soon...", True, (150, 150, 150))
        screen.blit(sub, (self.x + 20, self.y + 60))