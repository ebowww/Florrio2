import pygame, sys, random, math
from main_menu import MainMenu
from maps import GardenWorld, OceanWorld
from auth import AccountManager
from player import Player, TALENT_IDS
from petals import PetalManager, Petal, PETAL_TYPES, RARITY_ORDER
from mobs import MobManager, OceanMobManager, RARITY_COLORS
from ui import (CogButton, SettingsMenu, Hotbar, IndexButton,
                InventoryButton, InventoryMenu, CraftButton, CraftMenu,
                TalentButton, TalentMenu, _draw_petal_icon)

pygame.init()
WIDTH, HEIGHT = 800, 600
screen        = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("florr.io  –  Remake")
clock         = pygame.time.Clock()

# ══════════════════════════════════════════════════════════════════
#  WORLDS
# ══════════════════════════════════════════════════════════════════

garden = GardenWorld()
ocean  = OceanWorld()
WORLDS = {0: garden, 1: ocean}

current_world_id = 0
world            = garden

menu             = MainMenu(WIDTH, HEIGHT)
spawn_x, spawn_y = garden.get_safe_spawn()
player           = Player(spawn_x, spawn_y, world_map=world)

petal_manager        = PetalManager(player, num_petals=player.num_petal_slots())
player.petal_manager = petal_manager

# HUD
cog_button    = CogButton()
settings_menu = SettingsMenu()
index_button  = IndexButton(cog_button)
inv_button    = InventoryButton(HEIGHT)
inv_menu      = InventoryMenu(HEIGHT)
craft_button  = CraftButton(HEIGHT)
craft_menu    = CraftMenu(HEIGHT)
talent_button = TalentButton(HEIGHT)
talent_menu   = TalentMenu(WIDTH, HEIGHT)
hotbar        = Hotbar(HEIGHT, WIDTH, num_slots=player.num_petal_slots())

# Mob managers (one per world)
garden_mobs = MobManager(garden, num_bees=15, num_ladybugs=8, index_button=index_button)
ocean_mobs  = OceanMobManager(ocean, num_bubbles=18, num_jellyfish=10, index_button=index_button)

# ══════════════════════════════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════════════════════════════

game_state     = "menu"
selected_petal = None
save_timer     = 0
font_hud       = pygame.font.SysFont("segoeui", 18, bold=True)
font_world     = pygame.font.SysFont("segoeui", 15, bold=True)
font_dash      = pygame.font.SysFont("segoeui", 13, bold=True)

_portal_cooldown = 0
_PORTAL_CD       = 90

# ══════════════════════════════════════════════════════════════════
#  MENU BACKGROUND
# ══════════════════════════════════════════════════════════════════

bg_shapes = [
    {"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT),
     "size": random.randint(18, 48), "angle": random.random() * 360,
     "rot_speed": random.uniform(0.4, 1.2), "speed": random.uniform(0.25, 0.65)}
    for _ in range(15)
]

def draw_animated_menu_bg(surface):
    surface.fill((240, 245, 240))
    for s in bg_shapes:
        s["angle"] += s["rot_speed"];  s["y"] += s["speed"]
        if s["y"] > HEIGHT + 60: s["y"] = -60
        surf = pygame.Surface((s["size"], s["size"]), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0,0,0,35), (0,0,s["size"],s["size"]), width=2, border_radius=4)
        pygame.draw.rect(surf, (140,200,140,18), (2,2,s["size"]-4,s["size"]-4), border_radius=3)
        surface.blit(pygame.transform.rotate(surf, s["angle"]), (s["x"], s["y"]))

# ══════════════════════════════════════════════════════════════════
#  INVENTORY HELPERS
# ══════════════════════════════════════════════════════════════════

_DEFAULT_INV = {("Glass", "Common"): 5}

def _inv_add(inv, key, n=1):
    inv[key] = inv.get(key, 0) + n
    if inv[key] <= 0:
        inv.pop(key, None)

def _inv_to_json(inv):
    return [[pt, r, c] for (pt, r), c in inv.items()]

def _inv_from_json(lst):
    return {(row[0], row[1]): int(row[2]) for row in lst if len(row) == 3}

def _hotbar_to_json(petals):
    return [[p.petal_type, p.rarity] for p in petals]

# ══════════════════════════════════════════════════════════════════
#  SAVE / LOAD
# ══════════════════════════════════════════════════════════════════

def save_game_data():
    if not menu.username or not menu.username.strip():
        return
    rec = AccountManager.load(menu.username)
    pw  = rec.get("password", "") if rec else ""
    AccountManager.save(menu.username, {
        "password":     pw,
        "level":        player.level,
        "xp":           player.xp,
        "xp_to_next":   player.xp_to_next,
        "skill_points": player.skill_points,
        "talents":      player.talents,
        "inventory":    _inv_to_json(player.inventory),
        "hotbar":       _hotbar_to_json(petal_manager.petals),
        "index_counts": index_button.counts,
        "world_id":     current_world_id,
    })

def load_game_data(data):
    global current_world_id, world, _portal_cooldown
    player.level        = data.get("level", 1)
    player.xp           = data.get("xp", 0)
    player.xp_to_next   = data.get("xp_to_next", 100)
    player.skill_points = data.get("skill_points", 0)

    raw_inv = data.get("inventory", None)
    player.inventory = _inv_from_json(raw_inv) if isinstance(raw_inv, list) \
                       else dict(_DEFAULT_INV)

    saved_t = data.get("talents", {})
    for tid in TALENT_IDS:
        player.talents[tid] = int(saved_t.get(tid, 0))
    player._compute_stats()

    wid = int(data.get("world_id", 0))
    _switch_world(wid, restore=True)

    slots    = player.num_petal_slots()
    petal_manager.resize_slots(slots)
    hotbar.num_slots = slots

    saved_hb = data.get("hotbar", [["Glass", "Common"]] * slots)
    while len(saved_hb) < slots:
        saved_hb.append(["Glass", "Common"])
    saved_hb = saved_hb[:slots]
    petal_manager.petals = [Petal(player, rarity=row[1], petal_type=row[0])
                             for row in saved_hb]
    mult = player.reload_multiplier()
    for p in petal_manager.petals:
        from petals import petal_reload_base
        p.reload_time = max(10, int(petal_reload_base(p.petal_type) * mult))

    sc = data.get("index_counts", {})
    for mob in index_button.counts:
        if mob in sc and isinstance(sc[mob], dict):
            for rarity in index_button.counts[mob]:
                index_button.counts[mob][rarity] = int(sc[mob].get(rarity, 0))

    _portal_cooldown = _PORTAL_CD

# ══════════════════════════════════════════════════════════════════
#  WORLD SWITCHING
# ══════════════════════════════════════════════════════════════════

def _switch_world(wid, restore=False):
    global current_world_id, world, _portal_cooldown
    current_world_id = wid
    world            = WORLDS[wid]
    player.world_map = world
    if not restore:
        portal = world.portal
        a      = random.uniform(0, math.pi * 2)
        dist   = portal.radius + player.radius + 15
        player.x = portal.x + math.cos(a) * dist
        player.y = portal.y + math.sin(a) * dist
    _portal_cooldown = _PORTAL_CD

def _check_portal():
    global _portal_cooldown
    if _portal_cooldown > 0:
        _portal_cooldown -= 1
        return
    portal = world.portal
    if portal.contains(player.x, player.y):
        _switch_world(portal.target_world)

# ══════════════════════════════════════════════════════════════════
#  RESET  (on death)
# ══════════════════════════════════════════════════════════════════

def reset_game():
    global petal_manager, garden_mobs, ocean_mobs
    _switch_world(0)
    player.__init__(spawn_x, spawn_y, world_map=garden)
    petal_manager            = PetalManager(player, num_petals=player.num_petal_slots())
    player.petal_manager     = petal_manager
    hotbar.num_slots         = player.num_petal_slots()
    garden_mobs              = MobManager(garden, num_bees=15, num_ladybugs=8,
                                          index_button=index_button)
    ocean_mobs               = OceanMobManager(ocean, num_bubbles=18, num_jellyfish=10, index_button=index_button)
    inv_menu.visible         = False;  inv_menu.target_x   = -inv_menu.width
    craft_menu.visible       = False;  craft_menu.target_x = -craft_menu.width
    talent_menu.visible      = False
    menu.menu_state          = "home"

# ══════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════

def _has_bubble_petal():
    return any(p.petal_type == "Bubble" for p in petal_manager.petals)

def _current_mob_manager():
    return garden_mobs if current_world_id == 0 else ocean_mobs

# ══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════

while True:
    events    = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()

    for event in events:
        if event.type == pygame.QUIT:
            if game_state == "game": save_game_data()
            pygame.quit(); sys.exit()

        if cog_button.is_clicked(event): settings_menu.toggle()
        if index_button.is_clicked(event):
            index_button.menu_open = not index_button.menu_open

        if game_state == "game":
            # Right-click → bubble dash
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 3
                    and not settings_menu.visible and not talent_menu.visible):
                petal_manager.try_bubble_dash()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                talent_menu.toggle()
            if talent_button.is_clicked(event):
                talent_menu.toggle()

            talent_menu.handle_event(event, player)
            hotbar.num_slots = player.num_petal_slots()

            if not talent_menu.visible:
                if inv_button.is_clicked(event):
                    inv_menu.toggle()
                    if inv_menu.visible:
                        craft_menu.visible  = False
                        craft_menu.target_x = -craft_menu.width
                    selected_petal = None

                if craft_button.is_clicked(event):
                    craft_menu.toggle()
                    if craft_menu.visible:
                        inv_menu.visible  = False
                        inv_menu.target_x = -inv_menu.width
                    selected_petal = None

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if craft_menu.visible:
                        craft_menu.handle_click(event.pos, player)

                    picked = inv_menu.handle_click(event.pos, player)
                    if picked:
                        selected_petal = picked
                    elif selected_petal:
                        slot_idx = hotbar.get_slot_clicked(event.pos)
                        if slot_idx is not None:
                            old     = petal_manager.petals[slot_idx]
                            old_key = (old.petal_type, old.rarity)
                            _inv_add(player.inventory, old_key, 1)
                            ptype, rarity = selected_petal
                            new_petal = Petal(player, rarity=rarity, petal_type=ptype)
                            from petals import petal_reload_base
                            new_petal.reload_time = max(
                                10, int(petal_reload_base(ptype) * player.reload_multiplier()))
                            petal_manager.petals[slot_idx] = new_petal
                            _inv_add(player.inventory, selected_petal, -1)
                            selected_petal = None

        settings_menu.handle_event(event)

    # ── MENU STATE ───────────────────────────────────────────────
    if game_state == "menu":
        draw_animated_menu_bg(screen)
        prev_state = game_state
        game_state = menu.update(events)
        menu.draw(screen)
        if prev_state == "menu" and game_state == "game":
            acc = AccountManager.load(menu.username)
            if acc:
                load_game_data(acc)
            else:
                player.inventory = dict(_DEFAULT_INV)
                _switch_world(0, restore=True)
                save_game_data()

    # ── GAME STATE ───────────────────────────────────────────────
    elif game_state == "game":
        player.handle_input(events)
        inv_menu.update()
        craft_menu.update()

        # Crafting resolution
        if craft_menu.is_spinning and craft_menu.spin_timer == 1:
            key = craft_menu.selected_key
            if key and player.inventory.get(key, 0) >= 5:
                ptype_c, rarity_c = key
                tiers = craft_menu.TIERS;  rates = craft_menu.RATES
                if rarity_c in tiers:
                    idx_c = tiers.index(rarity_c)
                    if idx_c < len(tiers) - 1:
                        next_t   = tiers[idx_c + 1]
                        next_key = (ptype_c, next_t)
                        already_u = (
                            any(player.inventory.get((pt, "Unique"), 0) > 0
                                for pt in PETAL_TYPES)
                            or any(p.rarity == "Unique" for p in petal_manager.petals)
                        )
                        if not (next_t == "Unique" and already_u):
                            _inv_add(player.inventory, key, -5)
                            if random.randint(1, 100) <= rates[idx_c]:
                                _inv_add(player.inventory, next_key, 1)

        # Camera
        cam_x = max(0, min(player.x - WIDTH  // 2, world.width_px  - WIDTH))
        cam_y = max(0, min(player.y - HEIGHT // 2, world.height_px - HEIGHT))

        paused = settings_menu.visible or talent_menu.visible
        if not paused:
            player.handle_movement(pygame.key.get_pressed(), world,
                                   settings_menu.selected == 1, (cam_x, cam_y))
            player.update()
            petal_manager.update()
            world.update()

            mm = _current_mob_manager()
            mm.update(player, world, petal_manager)

            _check_portal()

            save_timer += 1
            if save_timer >= 600:
                save_game_data(); save_timer = 0
            if player.health <= 0:
                save_game_data(); reset_game(); game_state = "menu"

        # ── Drawing ───────────────────────────────────────────────
        world.draw(screen, cam_x, cam_y)
        mm = _current_mob_manager()
        mm.draw(screen, cam_x, cam_y)
        petal_manager.draw(screen, cam_x, cam_y)
        player.draw(screen, cam_x, cam_y)

        inv_menu.draw(screen, player)
        craft_menu.draw(screen, player)
        hotbar.draw(screen, petal_manager.petals)
        world.draw_minimap(screen, player, mm.all_mobs)

        cog_button.draw(screen)
        index_button.draw(screen)
        inv_button.draw(screen)
        craft_button.draw(screen)
        talent_button.draw(screen)

        # World label
        wlabel = "Garden" if current_world_id == 0 else "Ocean"
        wcol   = (170, 240, 170) if current_world_id == 0 else (150, 195, 255)
        wsurf  = font_world.render(f"[ {wlabel} ]", True, wcol)
        wshad  = font_world.render(f"[ {wlabel} ]", True, (0, 0, 0))
        screen.blit(wshad, wshad.get_rect(center=(WIDTH // 2 + 1, 15)))
        screen.blit(wsurf, wsurf.get_rect(center=(WIDTH // 2, 14)))

        # Dash cooldown hint (only if bubble petal equipped)


        # Player name tag
        ntxt = f"Lv{player.level}  {menu.username}"
        ns   = font_hud.render(ntxt, True, (255, 255, 255))
        nsh  = font_hud.render(ntxt, True, (0, 0, 0))
        nx   = int(player.x - cam_x)
        ny   = int(player.y - cam_y) - player.radius - 32
        screen.blit(nsh, nsh.get_rect(center=(nx + 1, ny + 1)))
        screen.blit(ns,  ns.get_rect(center=(nx, ny)))

        # Petal drag cursor
        if selected_petal:
            ptype_s, rarity_s = selected_petal
            col_s = RARITY_COLORS.get(rarity_s, (200, 200, 200))
            pygame.draw.circle(screen, (25, 25, 25), mouse_pos, 20)
            pygame.draw.circle(screen, col_s,        mouse_pos, 18)
            _draw_petal_icon(screen, mouse_pos[0], mouse_pos[1], ptype_s, col_s, 12)

        # Overlays (always last)
        index_button.draw_menu(screen)
        settings_menu.draw(screen)
        talent_menu.draw(screen, player)
        Player.draw_level_hud(screen, player, WIDTH, HEIGHT)

    pygame.display.flip()
    clock.tick(60)