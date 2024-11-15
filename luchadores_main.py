import pygame
import sys
from node_map import NodeMap
from luchadoresprueba import Fighter, Attack, players, end_turn, attack_fighter, choose_fighter, check_defeat_and_switch, draw_interface

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((1100, 700))
pygame.display.set_caption("Roguelike Turn-based Battle Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

WHITE = (255, 255, 255)

# Estado del juego
GAME_STATE_MAP = "map"
GAME_STATE_BATTLE = "battle"
game_state = GAME_STATE_MAP

# Crear mapa de nodos
node_map = NodeMap(screen)

# Variables de combate
current_player = 0
active_fighter = [0, 0]
turn = 0
selected_attack = None
selected_change = False

def handle_map_events():
    global game_state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if node_map.get_selected_node():
                    game_state = GAME_STATE_BATTLE
                    reset_screen()  # Reinicializa screen al cambiar al estado BATTLE
            elif event.key == pygame.K_SPACE:
                node_map.select_next_node()

def handle_battle_events():
    global game_state, current_player, selected_attack, selected_change

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                selected_attack = None
                selected_change = False
                end_turn(players[0][active_fighter[0]], players[1][active_fighter[1]])
                check_defeat_and_switch()
                if all(fighter.is_defeated() for fighter in players[1]):
                    game_state = GAME_STATE_MAP
                    reset_screen()  # Reinicializa screen al cambiar al estado MAP

def reset_screen():
    global screen
    pygame.quit()  # Apaga Pygame por completo
    pygame.init()  # Reinicia Pygame
    screen = pygame.display.set_mode((1100, 700))
    pygame.display.set_caption("Roguelike Turn-based Battle Game")

def draw_map():
    screen = pygame.display.set_mode((1100, 700))
    if not screen:
        print("Reinicializando pantalla en draw_map")
        reset_screen()
    else:
        print("screen está inicializado en draw_map")

    screen.fill(WHITE)
    node_map.draw()
    pygame.display.flip()

def draw_battle():
    screen = pygame.display.set_mode((1100, 700))
    if not screen:
        print("Reinicializando pantalla en draw_battle")
        reset_screen()
    else:
        print("screen está inicializado en draw_battle")

    draw_interface()
    pygame.display.flip()

# Bucle principal
running = True
while running:
    if game_state == GAME_STATE_MAP:
        handle_map_events()
        draw_map()
    elif game_state == GAME_STATE_BATTLE:
        handle_battle_events()
        draw_battle()

    clock.tick(30)
