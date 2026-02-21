import pygame

class Hotbar:
    def __init__(self, screen_height, num_slots=5):
        self.num_slots = num_slots
        self.slot_size = 50
        self.padding = 10
        self.y = screen_height - self.slot_size - 20
        self.x = 20
        self.font = pygame.font.SysFont("arial", 12, bold=True)

    def draw(self, screen, petals):
        for i in range(self.num_slots):
            slot_x = self.x + i * (self.slot_size + self.padding)
            slot_rect = pygame.Rect(slot_x, self.y, self.slot_size, self.slot_size)
            
            is_reloading = not petals[i].active if i < len(petals) else False
            
            # Colors
            bg_color = (60, 100, 20) if is_reloading else (126, 211, 33)
            border_color = (40, 70, 10) if is_reloading else (90, 160, 20)
            
            # Draw Slot with Outline
            pygame.draw.rect(screen, (0, 0, 0), slot_rect.inflate(4, 4), border_radius=8) # Outer Outline
            pygame.draw.rect(screen, bg_color, slot_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, slot_rect, width=3, border_radius=8)
            
            # Petal Icon
            petal_color = (130, 130, 130) if is_reloading else (255, 255, 255)
            petal_center = (slot_x + self.slot_size // 2, self.y + self.slot_size // 2 - 5)
            pygame.draw.circle(screen, petal_color, petal_center, 10)
            pygame.draw.circle(screen, (0, 0, 0), petal_center, 10, width=2) # Icon Outline

class SettingsMenu:
    def __init__(self, width=300, height=250):
        self.width, self.height = width, height
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (400, 300)
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.options = ["WASD Movement", "Mouse Follow"]
        self.selected = 1
        self.visible = False
        self._generate_option_rects()

    def _generate_option_rects(self):
        self.rendered_options = []
        for i, text_str in enumerate(self.options):
            text_surf = self.font.render(text_str, True, (0, 0, 0))
            text_rect = text_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top + 70 + i * 60)
            self.rendered_options.append((text_surf, text_rect))

    def toggle(self): self.visible = not self.visible
    
    def handle_event(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            for i, (_, rect) in enumerate(self.rendered_options):
                if rect.inflate(40, 20).collidepoint(event.pos): self.selected = i

    def draw(self, screen):
        if not self.visible: return
        # Sliding UI feel (simplified for now as a centered box)
        pygame.draw.rect(screen, (0, 0, 0), self.rect.inflate(6, 6), border_radius=12) # Thick Outline
        pygame.draw.rect(screen, (240, 240, 240), self.rect, border_radius=12)
        
        for i, (surf, rect) in enumerate(self.rendered_options):
            color = (120, 240, 120) if i == self.selected else (200, 200, 200)
            btn_rect = rect.inflate(40, 15)
            pygame.draw.rect(screen, (0, 0, 0), btn_rect.inflate(4, 4), border_radius=8) # Button Outline
            pygame.draw.rect(screen, color, btn_rect, border_radius=8)
            screen.blit(surf, rect)

class CogButton:
    def __init__(self, x=15, y=15, size=40):
        self.rect = pygame.Rect(x, y, size, size)
    def draw(self, screen):
        pygame.draw.circle(screen, (0, 0, 0), self.rect.center, (self.rect.width // 2) + 2) # Outline
        pygame.draw.circle(screen, (150, 150, 150), self.rect.center, self.rect.width // 2)
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)