import pygame, sys, random, math
from main_menu import MainMenu
from maps import WorldMap
from auth import AccountManager
from player import Player
from petals import PetalManager, Petal
from mobs import MobManager, Bee
# Added CraftButton and CraftMenu to the UI imports
from ui import (CogButton, SettingsMenu, Hotbar, IndexButton, 
                InventoryButton, InventoryMenu, CraftButton, CraftMenu)

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Florr Clone - Account System")
clock = pygame.time.Clock()

# --- Initialize objects ---
world = WorldMap(WIDTH, HEIGHT)
menu = MainMenu(WIDTH, HEIGHT)
spawn_x, spawn_y = world.get_safe_spawn()
player = Player(spawn_x, spawn_y, world_map=world)
petal_manager = PetalManager(player, num_petals=5)

cog_button = CogButton()
settings_menu = SettingsMenu()
hotbar = Hotbar(HEIGHT)
index_button = IndexButton(cog_button)

# Inventory UI
inv_button = InventoryButton(HEIGHT)
inv_menu = InventoryMenu(HEIGHT)

# Crafting UI (Positioned on top of inventory)
craft_button = CraftButton(HEIGHT)
craft_menu = CraftMenu(HEIGHT)

mob_manager = MobManager(world, num_bees=20, index_button=index_button)

game_state = "menu"
font = pygame.font.SysFont("arial", 20, bold=True)
selected_petal = None 
save_timer = 0 

# --- Background Animation Logic ---
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
        shape_surf = pygame.Surface((s["size"], s["size"]), pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0, 0, 0, 40), (0, 0, s["size"], s["size"]), width=2)
        pygame.draw.rect(shape_surf, (150, 150, 150, 20), (2, 2, s["size"] - 4, s["size"] - 4))
        rotated = pygame.transform.rotate(shape_surf, s["angle"])
        screen.blit(rotated, (s["x"], s["y"]))

# --- Account Logic Functions ---
def save_game_data():
    if not menu.username or menu.username.strip() == "":
        return
    current_record = AccountManager.load(menu.username)
    saved_password = current_record.get("password", "") if current_record else ""
    idx_counts = getattr(index_button, 'counts', {})
    
    data = {
        "password": saved_password,
        "level": player.level,
        "xp": player.xp,
        "inventory": player.inventory,
        "hotbar": [p.rarity for p in petal_manager.petals],
        "index_counts": idx_counts
    }
    AccountManager.save(menu.username, data)
    print(f"Progress saved for: {menu.username}")

def load_game_data(data):
    player.level = data.get("level", 1)
    player.xp = data.get("xp", 0)
    player.inventory = data.get("inventory", {"Common": 5})
    saved_hotbar = data.get("hotbar", ["Common"] * 5)
    petal_manager.petals = [Petal(player, rarity=r) for r in saved_hotbar]
    if hasattr(index_button, 'counts'):
        index_button.counts = data.get("index_counts", {})

# --- Main Game Loop ---
while True:
    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()
    
    for event in events:
        if event.type == pygame.QUIT:
            if game_state == "game": save_game_data()
            pygame.quit(); sys.exit()
        
        if cog_button.is_clicked(event): settings_menu.toggle()
        if index_button.is_clicked(event): index_button.menu_open = not index_button.menu_open
        
        if game_state == "game":
            # Inventory Logic
            if inv_button.is_clicked(event): 
                inv_menu.toggle()
                if inv_menu.visible: craft_menu.visible = False; craft_menu.target_x = -craft_menu.width
                selected_petal = None 
            
            # Crafting Logic
            if craft_button.is_clicked(event):
                craft_menu.toggle()
                if craft_menu.visible: inv_menu.visible = False; inv_menu.target_x = -inv_menu.width
                selected_petal = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                picked = inv_menu.handle_click(event.pos, player)
                if picked:
                    selected_petal = picked
                elif selected_petal:
                    slot_idx = hotbar.get_slot_clicked(event.pos)
                    if slot_idx is not None:
                        old_rarity = petal_manager.petals[slot_idx].rarity
                        player.inventory[old_rarity] = player.inventory.get(old_rarity, 0) + 1
                        petal_manager.petals[slot_idx] = Petal(player, rarity=selected_petal)
                        player.inventory[selected_petal] -= 1
                        if player.inventory[selected_petal] <= 0: del player.inventory[selected_petal]
                        selected_petal = None
        
        settings_menu.handle_event(event)

    if game_state == "menu":
        draw_animated_menu_bg(screen)
        prev_state = game_state
        game_state = menu.update(events)
        menu.draw(screen)
        if prev_state == "menu" and game_state == "game":
            account_data = AccountManager.load(menu.username)
            if account_data: load_game_data(account_data)
            else: save_game_data()

    elif game_state == "game":
        player.handle_input(events)
        inv_menu.update() 
        craft_menu.update()
        
        camera_x = max(0, min(player.x - WIDTH // 2, world.width_px - WIDTH))
        camera_y = max(0, min(player.y - HEIGHT // 2, world.height_px - HEIGHT))

        if not settings_menu.visible:
            player.handle_movement(pygame.key.get_pressed(), world, settings_menu.selected == 1, (camera_x, camera_y))
            player.update()
            petal_manager.update()
            mob_manager.update(player, world, petal_manager)

            save_timer += 1
            if save_timer >= 300:
                save_game_data()
                save_timer = 0

            if player.health <= 0:
                save_game_data(); game_state = "menu"
                player.__init__(spawn_x, spawn_y, world_map=world)
                petal_manager = PetalManager(player, num_petals=5)
                mob_manager = MobManager(world, num_bees=20, index_button=index_button)
                selected_petal = None
                menu.menu_state = "home"

        # --- DRAWING ---
        world.draw(screen, camera_x, camera_y)
        mob_manager.draw(screen, camera_x, camera_y)
        petal_manager.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)

        # UI
        hotbar.draw(screen, petal_manager.petals)
        world.draw_minimap(screen, player, mob_manager.bees)
        cog_button.draw(screen)
        index_button.draw(screen)
        
        inv_button.draw(screen)
        inv_menu.draw(screen, player)
        
        craft_button.draw(screen)
        craft_menu.draw(screen)
        
        # Nametag
        name_txt = f"Lvl {player.level} | {menu.username}"
        name_surf = font.render(name_txt, True, (255, 255, 255))
        screen.blit(name_surf, name_surf.get_rect(center=(player.x - camera_x, player.y - camera_y - 45)))
        
        if selected_petal:
            color = Bee.RARITY_COLORS.get(selected_petal, (255, 255, 255))
            pygame.draw.circle(screen, (40, 40, 40), mouse_pos, 18)
            pygame.draw.circle(screen, color, mouse_pos, 16)
            pygame.draw.circle(screen, (255, 240, 150), mouse_pos, 11)

        index_button.draw_menu(screen)
        settings_menu.draw(screen)

    pygame.display.flip()
    clock.tick(60)