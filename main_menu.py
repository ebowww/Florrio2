import pygame
import random
from auth import AccountManager

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height

        # Fonts
        self.title_font = pygame.font.SysFont("arial", 80, bold=True)
        self.button_font = pygame.font.SysFont("arial", 30, bold=True)
        self.input_font = pygame.font.SysFont("arial", 28, bold=False)
        self.msg_font = pygame.font.SysFont("arial", 20, bold=True)

        # Menu States: "home", "login", "register"
        self.menu_state = "home"
        
        # Account Data
        self.username = ""
        self.password = ""
        self.active_field = "username" # Toggle focus
        self.message = ""
        self.message_color = (255, 255, 255)

        # UI Rects
        self.login_btn_rect = pygame.Rect(self.w // 2 - 120, self.h // 2, 240, 60)
        self.reg_btn_rect = pygame.Rect(self.w // 2 - 120, self.h // 2 + 80, 240, 60)
        
        # Shared input/submit rects for login/register screens
        self.u_input_rect = pygame.Rect(self.w // 2 - 150, self.h // 2 - 60, 300, 45)
        self.p_input_rect = pygame.Rect(self.w // 2 - 150, self.h // 2 + 20, 300, 45)
        self.submit_btn_rect = pygame.Rect(self.w // 2 - 100, self.h // 2 + 100, 200, 50)
        self.back_btn_rect = pygame.Rect(20, 80, 100, 40)
        self.quit_rect = pygame.Rect(20, 20, 100, 40)

        # Decorative Petals
        self.petals = []
        self.spawn_petals(40)

    def spawn_petals(self, amount):
        colors = [(255, 210, 210), (255, 240, 190), (210, 230, 255), (220, 255, 220), (240, 220, 255)]
        shapes = ["circle", "diamond", "square"]
        for _ in range(amount):
            self.petals.append({
                "x": random.randint(-100, self.w),
                "y": random.randint(0, self.h),
                "size": random.randint(6, 18),
                "speed": random.uniform(0.3, 1.5),
                "drift": random.uniform(-0.2, 0.2),
                "color": random.choice(colors),
                "shape": random.choice(shapes)
            })

    def handle_auth(self):
        if len(self.username) < 3 or len(self.password) < 3:
            self.message = "Username/Password too short!"
            self.message_color = (200, 50, 50)
            return "menu"

        if self.menu_state == "register":
            if AccountManager.load(self.username):
                self.message = "User already exists!"
                self.message_color = (200, 50, 50)
            else:
                # Create account with starting stats
                initial_data = {
                    "password": self.password,
                    "level": 1,
                    "xp": 0,
                    "inventory": {"Common": 5},
                    "hotbar": ["Common"] * 5,
                    "index_counts": {}
                }
                AccountManager.save(self.username, initial_data)
                self.message = "Registered! Now please Login."
                self.message_color = (50, 200, 50)
                self.menu_state = "login"
                self.password = "" 
        
        elif self.menu_state == "login":
            data = AccountManager.load(self.username)
            if data and data.get("password") == self.password:
                return "game" # Success!
            else:
                self.message = "Invalid Username or Password!"
                self.message_color = (200, 50, 50)
        
        return "menu"

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()

        # Petal movement
        for petal in self.petals:
            petal["x"] += petal["speed"]
            petal["y"] += petal["drift"]
            if petal["x"] > self.w + 50:
                petal["x"] = -50
                petal["y"] = random.randint(0, self.h)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.quit_rect.collidepoint(mouse_pos):
                    pygame.quit(); exit()
                
                if self.menu_state == "home":
                    if self.login_btn_rect.collidepoint(mouse_pos): self.menu_state = "login"
                    elif self.reg_btn_rect.collidepoint(mouse_pos): self.menu_state = "register"
                
                else: # In Login or Register screen
                    if self.back_btn_rect.collidepoint(mouse_pos): 
                        self.menu_state = "home"
                        self.message = ""
                    if self.u_input_rect.collidepoint(mouse_pos): self.active_field = "username"
                    if self.p_input_rect.collidepoint(mouse_pos): self.active_field = "password"
                    if self.submit_btn_rect.collidepoint(mouse_pos):
                        res = self.handle_auth()
                        if res == "game": return "game"

            if event.type == pygame.KEYDOWN and self.menu_state != "home":
                if event.key == pygame.K_BACKSPACE:
                    if self.active_field == "username": self.username = self.username[:-1]
                    else: self.password = self.password[:-1]
                elif event.key == pygame.K_TAB:
                    self.active_field = "password" if self.active_field == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    res = self.handle_auth()
                    if res == "game": return "game"
                else:
                    if len(self.username) < 15 and self.active_field == "username":
                        self.username += event.unicode
                    elif len(self.password) < 15 and self.active_field == "password":
                        self.password += event.unicode

        return "menu"

    def draw(self, screen):
        # Background and title
        self.draw_gradient(screen)
        for petal in self.petals: self.draw_petal(screen, petal)
        
        title_surf = self.title_font.render("florr.io", True, (40, 40, 40))
        screen.blit(title_surf, title_surf.get_rect(center=(self.w // 2, 120)))

        mouse_pos = pygame.mouse.get_pos()

        if self.menu_state == "home":
            self.draw_ui_button(screen, self.login_btn_rect, "LOGIN", (90, 190, 120), mouse_pos)
            self.draw_ui_button(screen, self.reg_btn_rect, "CREATE ACCOUNT", (70, 140, 200), mouse_pos)
        
        else:
            # Drawing Input Fields
            self.draw_input(screen, self.u_input_rect, "Username", self.username, self.active_field == "username")
            self.draw_input(screen, self.p_input_rect, "Password", "*" * len(self.password), self.active_field == "password")
            
            submit_label = "GO!" if self.menu_state == "login" else "REGISTER"
            self.draw_ui_button(screen, self.submit_btn_rect, submit_label, (50, 50, 50), mouse_pos)
            self.draw_ui_button(screen, self.back_btn_rect, "BACK", (120, 120, 120), mouse_pos)

        # Feedback Message
        if self.message:
            msg_surf = self.msg_font.render(self.message, True, self.message_color)
            screen.blit(msg_surf, msg_surf.get_rect(center=(self.w // 2, 190)))

        # Quit Button
        self.draw_ui_button(screen, self.quit_rect, "QUIT", (170, 50, 50), mouse_pos)

    def draw_input(self, screen, rect, label, value, is_active):
        color = (255, 255, 255) if is_active else (220, 220, 220)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        pygame.draw.rect(screen, (80, 80, 80) if is_active else (150, 150, 150), rect, 2, border_radius=10)
        
        label_surf = self.msg_font.render(label, True, (60, 60, 60))
        screen.blit(label_surf, (rect.x, rect.y - 22))
        
        val_surf = self.input_font.render(value, True, (40, 40, 40))
        screen.blit(val_surf, (rect.x + 10, rect.y + 7))

    def draw_ui_button(self, screen, rect, text, color, mouse_pos):
        btn_color = [min(255, c + 30) for c in color] if rect.collidepoint(mouse_pos) else color
        pygame.draw.rect(screen, btn_color, rect, border_radius=12)
        txt_surf = self.button_font.render(text, True, (255, 255, 255))
        screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))

    # Existing visual helper methods
    def draw_petal(self, screen, petal):
        x, y, size, color = int(petal["x"]), int(petal["y"]), petal["size"], petal["color"]
        if petal["shape"] == "circle": pygame.draw.circle(screen, color, (x, y), size)
        elif petal["shape"] == "square": pygame.draw.rect(screen, color, (x-size, y-size, size*2, size*2), border_radius=4)
        elif petal["shape"] == "diamond": pygame.draw.polygon(screen, color, [(x, y-size), (x+size, y), (x, y+size), (x-size, y)])

    def draw_gradient(self, screen):
        t, b = (200, 255, 200), (50, 150, 50)
        for y in range(self.h):
            ratio = y / self.h
            c = [int(t[i]*(1-ratio) + b[i]*ratio) for i in range(3)]
            pygame.draw.line(screen, c, (0, y), (self.w, y))