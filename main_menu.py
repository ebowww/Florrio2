import pygame
import random

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height

        # Fonts
        self.title_font = pygame.font.SysFont("arial", 80, bold=True)
        self.button_font = pygame.font.SysFont("arial", 36, bold=True)
        self.input_font = pygame.font.SysFont("arial", 32, bold=False)  # bigger for placeholder

        # Play button
        self.button_rect = pygame.Rect(
            self.w // 2 - 120,
            self.h // 2 + 90,
            240,
            70
        )

        # Username input box
        self.input_rect = pygame.Rect(
            self.w // 2 - 200,   # moved left to stay centered
            self.h // 2 - 20,
            400,                 # increased width
            50
        )

        self.username = ""
        self.active_input = False
        self.placeholder = "Enter your username"

        # Quit button (top-left)
        self.quit_rect = pygame.Rect(20, 20, 100, 40)

        # Petals
        self.petals = []
        self.spawn_petals(40)

    # -----------------------------
    # Petal creation
    # -----------------------------
    def spawn_petals(self, amount):
        colors = [
            (255, 210, 210),
            (255, 240, 190),
            (210, 230, 255),
            (220, 255, 220),
            (240, 220, 255)
        ]
        shapes = ["circle", "diamond", "square"]

        for _ in range(amount):
            size = random.randint(6, 18)
            self.petals.append({
                "x": random.randint(-100, self.w),
                "y": random.randint(0, self.h),
                "size": size,
                "speed": random.uniform(0.3, 1.5),
                "drift": random.uniform(-0.2, 0.2),
                "color": random.choice(colors),
                "shape": random.choice(shapes)
            })

    # -----------------------------
    # Update menu (petals + input + clicks)
    # -----------------------------
    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        # Move petals left → right
        for petal in self.petals:
            petal["x"] += petal["speed"]
            petal["y"] += petal["drift"]
            if petal["x"] > self.w + 50:
                petal["x"] = -50
                petal["y"] = random.randint(0, self.h)

        # Input handling
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_rect.collidepoint(mouse_pos):
                    self.active_input = True
                else:
                    self.active_input = False

                if self.button_rect.collidepoint(mouse_pos):
                    if self.username.strip() == "":
                        self.username = "Player"
                    return "game"

                if self.quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

            if event.type == pygame.KEYDOWN and self.active_input:
                if event.key == pygame.K_BACKSPACE:
                    self.username = self.username[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active_input = False
                else:
                    if len(self.username) < 15:
                        self.username += event.unicode

        return "menu"

    # -----------------------------
    # Draw petals
    # -----------------------------
    def draw_petal(self, screen, petal):
        x = int(petal["x"])
        y = int(petal["y"])
        size = petal["size"]
        color = petal["color"]

        if petal["shape"] == "circle":
            pygame.draw.circle(screen, color, (x, y), size)
        elif petal["shape"] == "square":
            rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
            pygame.draw.rect(screen, color, rect, border_radius=4)
        elif petal["shape"] == "diamond":
            points = [
                (x, y - size),
                (x + size, y),
                (x, y + size),
                (x - size, y)
            ]
            pygame.draw.polygon(screen, color, points)

    # -----------------------------
    # Draw gradient background
    # -----------------------------
    def draw_gradient(self, screen):
        top_color = (200, 255, 200)  # light green
        bottom_color = (50, 150, 50)  # dark green
        for y in range(self.h):
            ratio = y / self.h
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.w, y))

    # -----------------------------
    # Draw menu
    # -----------------------------
    def draw(self, screen):
        # Background gradient
        self.draw_gradient(screen)

        # Draw petals
        for petal in self.petals:
            self.draw_petal(screen, petal)

        # Title
        title_surface = self.title_font.render("florr.io", True, (40, 40, 40))
        title_rect = title_surface.get_rect(center=(self.w // 2, 150))
        screen.blit(title_surface, title_rect)

        # Username input box
        color = (255, 255, 255) if self.active_input else (200, 200, 200)
        pygame.draw.rect(screen, color, self.input_rect, border_radius=15)
        pygame.draw.rect(screen, (150, 150, 150), self.input_rect, 3, border_radius=15)

        if self.username == "" and not self.active_input:
            text_surface = self.input_font.render(self.placeholder, True, (120, 120, 120))
        else:
            text_surface = self.input_font.render(self.username, True, (50, 50, 50))

        text_rect = text_surface.get_rect(midleft=(self.input_rect.x + 15, self.input_rect.centery))
        screen.blit(text_surface, text_rect)

        # Play button hover effect
        mouse_pos = pygame.mouse.get_pos()
        button_color = (90, 190, 120) if self.button_rect.collidepoint(mouse_pos) else (70, 170, 100)
        pygame.draw.rect(screen, button_color, self.button_rect, border_radius=20)

        # Play button text
        text_surface = self.button_font.render("PLAY", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        screen.blit(text_surface, text_rect)

        # Quit button hover effect
        quit_color = (200, 80, 80) if self.quit_rect.collidepoint(mouse_pos) else (170, 50, 50)
        pygame.draw.rect(screen, quit_color, self.quit_rect, border_radius=12)
        quit_text = self.input_font.render("QUIT", True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=self.quit_rect.center)
        screen.blit(quit_text, quit_rect)