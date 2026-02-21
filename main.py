import pygame
import sys
import random
from main_menu import MainMenu
from maps import WorldMap
from player import Player
from ui import CogButton, SettingsMenu, Hotbar
from petals import PetalManager
from mobs import MobManager

# Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Florr Clone - Minimap & UI Restore")
clock = pygame.time.Clock()

# --- Decorative Background Logic ---
bg_shapes = []
for _ in range(15):
    bg_shapes.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "size": random.randint(20, 50),
        "angle": random.random() * 360,
        "rot_speed": random.uniform(0.5, 1.5),
        "speed": random.uniform(0.3, 0.7)
    })

def draw_animated_menu_bg(screen):
    screen.fill((245, 245, 245))
    for s in bg_shapes:
        s["angle"] += s["rot_speed"]
        s["y"] += s["speed"]
        if s["y"] > HEIGHT: s["y"] = -50
        
        # Draw Square with Outline and reduced opacity
        shape_surf = pygame.Surface((s["size"], s["size"]), pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0, 0, 0, 40), (0, 0, s["size"], s["size"]), width=2) # Outline
        pygame.draw.rect(shape_surf, (150, 150, 150, 20), (2, 2, s["size"]-4, s["size"]-4))
        rotated = pygame.transform.rotate(shape_surf, s["angle"])
        screen.blit(rotated, (s["x"], s["y"]))

# --- Core Initialization ---
world = WorldMap(WIDTH, HEIGHT) 
menu = MainMenu(WIDTH, HEIGHT)
spawn_x, spawn_y = world.get_safe_spawn()
player = Player(spawn_x, spawn_y, world_map=world)
petal_manager = PetalManager(player, num_petals=5)
mob_manager = MobManager(world, num_bees=20)

cog_button = CogButton()
settings_menu = SettingsMenu()
hotbar = Hotbar(HEIGHT)

game_state = "menu"
font = pygame.font.SysFont("arial", 20, bold=True)

# --- Main Loop ---
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        if cog_button.is_clicked(event):
            settings_menu.toggle()
        settings_menu.handle_event(event)

    if game_state == "menu":
        draw_animated_menu_bg(screen)
        game_state = menu.update(events)
        menu.draw(screen)
    
    elif game_state == "game":
        player.handle_input(events)
        
        # Camera Logic
        camera_x = max(0, min(player.x - WIDTH // 2, world.width_px - WIDTH))
        camera_y = max(0, min(player.y - HEIGHT // 2, world.height_px - HEIGHT))

        if not settings_menu.visible:
            # Movement & Logic
            player.handle_movement(pygame.key.get_pressed(), world, settings_menu.selected == 1, (camera_x, camera_y))
            player.update()
            petal_manager.update()
            mob_manager.update(player, world, petal_manager.petals)
            
            # Game Reset (Requirement)
            if player.health <= 0:
                game_state = "menu"
                player.__init__(spawn_x, spawn_y, world) # Reset stats/position
                mob_manager = MobManager(world) # Refresh mobs

        # World Rendering
        world.draw(screen, camera_x, camera_y)
        mob_manager.draw(screen, camera_x, camera_y)
        petal_manager.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        
        # UI: Floating Nametag
        name_txt = f"Lvl {player.level} | {menu.username}"
        name_surf = font.render(name_txt, True, (255, 255, 255))
        screen.blit(name_surf, name_surf.get_rect(center=(player.x - camera_x, player.y - camera_y - 45)))
        
        # UI: Overlays
        hotbar.draw(screen, petal_manager.petals)
        world.draw_minimap(screen, player, mob_manager.bees) # Restored Minimap
        cog_button.draw(screen)
        settings_menu.draw(screen)

    pygame.display.flip()
    clock.tick(60)