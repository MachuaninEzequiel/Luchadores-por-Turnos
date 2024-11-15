import pygame
import os
import sys
import random
from PIL import Image, ImageSequence


# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((1100, 700))
pygame.display.set_caption("Turn-based Battle Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
SELECTED_COLOR = (100, 100, 255)

# Clases de los luchadores y ataques
class Attack:
    def __init__(self, name, damage=0, accuracy=1.0, attack_type="Físico", stat_change=None, effect_duration=0):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.attack_type = attack_type
        self.stat_change = stat_change
        self.effect_duration = effect_duration

    def attempt_hit(self):
        return random.random() < self.accuracy

class Fighter:
    def __init__(self, name, hp, physical_attack, magic_attack, defense, magic_defense, speed, attacks, gif_path, mirrored=False):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.physical_attack = physical_attack
        self.magic_attack = magic_attack
        self.defense = defense
        self.magic_defense = magic_defense
        self.speed = speed
        self.attacks = attacks
        self.frames = self.load_gif(gif_path, mirrored)
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_delay = 5
        self.active_effects = {}

    def load_gif(self, gif_path, mirrored=False):
        gif_image = Image.open(gif_path)
        frames = []
        for frame in ImageSequence.Iterator(gif_image):
            frame = frame.convert("RGBA")
            frame = frame.resize((280, 280))
            frame_surface = pygame.image.frombuffer(frame.tobytes(), frame.size, frame.mode)
            if mirrored:
                frame_surface = pygame.transform.flip(frame_surface, True, False)
            frames.append(frame_surface)
        return frames

    def update_animation(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.frame_counter = 0

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def take_damage(self, damage, attack_type):
        if attack_type == "Físico":
            damage -= self.defense * 0.5
        elif attack_type == "Mágico":
            damage -= self.magic_defense * 0.5
        damage = max(0, int(damage))
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return damage

    def apply_stat_change(self, stat, change):
        if stat == "velocidad":
            self.speed += change
        elif stat == "ataque_fisico":
            self.physical_attack += change
        elif stat == "ataque_magico":
            self.magic_attack += change
        elif stat == "defensa":
            self.defense += change
        elif stat == "defensa_magica":
            self.magic_defense += change
        elif stat == "curar":
            self.hp = min(self.max_hp, self.hp + change)

    def apply_effect(self, effect):
        self.active_effects[effect.name] = effect.effect_duration

    def update_effects(self):
        for effect in list(self.active_effects.keys()):
            if self.active_effects[effect] <= 0:
                del self.active_effects[effect]
                continue

            # Aplicar daño y debilitaciones según el tipo de efecto
            if effect == "Tóxico":
                self.hp -= 5
                print(f"{self.name} sufre 5 puntos de daño por Tóxico.")
            elif effect == "Quemar":
                self.hp -= 3
                self.physical_attack = max(0, self.physical_attack - 1)
                print(f"{self.name} sufre 3 puntos de daño por Quemar y pierde ataque físico.")
            elif effect == "Cursed":
                self.magic_attack = max(0, self.magic_attack - 1)
                self.hp -= 4  # Añadido un pequeño daño por la maldición
                print(f"{self.name} sufre la maldición y pierde ataque mágico.")

            # Reducir la duración del efecto
            self.active_effects[effect] -= 1

    def get_status(self):
        if "Tóxico" in self.active_effects and self.active_effects["Tóxico"] > 0:
            return "toxic"
        elif "Quemar" in self.active_effects and self.active_effects["Quemar"] > 0:
            return "burn"
        elif "Cursed" in self.active_effects and self.active_effects["Cursed"] > 0:
            return "cursed"
        else:
            return "normal"

    def is_defeated(self):
        return self.hp <= 0

def choose_fighter(player_index):
    global active_fighter
    selectable_fighters = [i for i, fighter in enumerate(players[player_index]) if not fighter.is_defeated()]

    current_selection = 0  # Variable para rastrear la selección actual
    choosing = True
    while choosing:
        screen.fill(WHITE)
        text = font.render("Selecciona tu luchador y presiona Enter:", True, BLACK)
        screen.blit(text, (50, 50))

        for i, fighter_index in enumerate(selectable_fighters):
            fighter = players[player_index][fighter_index]
            color = SELECTED_COLOR if i == current_selection else DARK_GRAY
            pygame.draw.rect(screen, color, (50, 100 + i * 60, 400, 50))
            name_text = font.render(fighter.name, True, WHITE)
            screen.blit(name_text, (60, 110 + i * 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_selection = (current_selection - 1) % len(selectable_fighters)
                elif event.key == pygame.K_DOWN:
                    current_selection = (current_selection + 1) % len(selectable_fighters)
                elif event.key == pygame.K_RETURN:
                    active_fighter[player_index] = selectable_fighters[current_selection]
                    choosing = False

def check_defeat_and_switch():
    global running
    for i in range(2):
        if all(fighter.is_defeated() for fighter in players[i]):
            print(f"Player {1 - i + 1} wins!")
            running = False
            return
        elif players[i][active_fighter[i]].is_defeated():
            choose_fighter(i)



# Crear los luchadores y ataques
attacks_pool = [
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),

    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Power Up", attack_type="Estado", stat_change={"stat": "ataque_fisico", "change": 5}),
    Attack("Magic Boost", attack_type="Estado", stat_change={"stat": "ataque_magico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
    Attack("Weaken", attack_type="Estado", stat_change={"stat": "defensa", "change": -5}),
    Attack("Slow Down", attack_type="Estado", stat_change={"stat": "velocidad", "change": -5}),

    Attack("Tóxico", attack_type="Estado", effect_duration=3),
    Attack("Quemar", attack_type="Estado", effect_duration=2),
    Attack("Cursed", attack_type="Estado", effect_duration=2)
]

attacks_pool1 = [
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Magic Boost", attack_type="Estado", stat_change={"stat": "ataque_magico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
    Attack("Tóxico", attack_type="Estado", effect_duration=3)
]

attacks_pool2 = [
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Power Up", attack_type="Estado", stat_change={"stat": "ataque_fisico", "change": 5}),
    Attack("Magic Boost", attack_type="Estado", stat_change={"stat": "ataque_magico", "change": 5}),
]

attacks_pool3 = [
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Magic Boost", attack_type="Estado", stat_change={"stat": "ataque_magico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
    Attack("Weaken", attack_type="Estado", stat_change={"stat": "defensa", "change": -5}),
]

attacks_pool4 = [
    Attack("unch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Power Up", attack_type="Estado", stat_change={"stat": "ataque_fisico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
]

# Crear los luchadores con GIFs
fighter1 = Fighter("Fighter 1", 100, 15, 10, 8, 6, 20, attacks_pool1[:5], gif_path="assets/fighter1.gif")
fighter2 = Fighter("Fighter 2", 100, 12, 15, 6, 8, 15, attacks_pool2[:5], gif_path="assets/fighter2.gif")
fighter3 = Fighter("Fighter 3", 100, 15, 10, 8, 6, 20, attacks_pool1[:5], gif_path="assets/fighter3.gif")
fighter4 = Fighter("Fighter 4", 100, 12, 15, 6, 8, 15, attacks_pool2[:5], gif_path="assets/fighter4.gif")
fighter5 = Fighter("Fighter 5", 100, 13, 12, 7, 7, 18, attacks_pool3[:5], gif_path="assets/fighter5.gif", mirrored=True)
fighter6 = Fighter("Fighter 6", 100, 10, 15, 5, 10, 12, attacks_pool4[:5], gif_path="assets/fighter6.gif", mirrored=True)
fighter7 = Fighter("Fighter 7", 100, 13, 12, 7, 7, 18, attacks_pool3[:5], gif_path="assets/fighter7.gif", mirrored=True)
fighter8 = Fighter("Fighter 8", 100, 10, 15, 5, 10, 12, attacks_pool4[:5], gif_path="assets/fighter8.gif", mirrored=True)

players = [
    [fighter1],  # Jugador 1
    [fighter5]   # Jugador 2
]


#players = [
    #[fighter1, fighter2 , fighter3, fighter4],  # Jugador 1
    #[fighter5, fighter6, fighter7, fighter8]   # Jugador 2
#]


# Variables de estado del juego
current_player = 0
active_fighter = [0, 0]
turn = 0
selected_attack = None
selected_change = False


def end_turn(attacker, defender):
    attacker.update_effects()
    defender.update_effects()

def attack_fighter(attacker, defender, attack):
    if attack.attempt_hit():
        if attack.attack_type == "Físico":
            damage = attack.damage + (0.5 * attacker.physical_attack - 0.5 * defender.defense)
            final_damage = defender.take_damage(damage, "Físico")
            print(f"{attacker.name} used {attack.name} and dealt {final_damage} damage!")
        elif attack.attack_type == "Mágico":
            damage = attack.damage + (0.5 * attacker.magic_attack - 0.5 * defender.magic_defense)
            final_damage = defender.take_damage(damage, "Mágico")
            print(f"{attacker.name} used {attack.name} and dealt {final_damage} damage!")
        elif attack.attack_type == "Estado":
            if attack.stat_change:
                target = attacker if attack.name in ["Speed Boost", "Power Up", "Magic Boost", "Heal"] else defender
                target.apply_stat_change(attack.stat_change['stat'], attack.stat_change['change'])
                print(f"{attacker.name} used {attack.name} and applied {attack.stat_change['stat']} change on {target.name}!")
            else:
                defender.apply_effect(attack)
                print(f"{attacker.name} used {attack.name} and applied {attack.name} effect!")
    else:
        print(f"{attacker.name} used {attack.name} but it missed!")

    # Actualizamos los efectos al final del ataque
    attacker.update_effects()
    defender.update_effects()


# Funciones auxiliares
def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


small_font = pygame.font.Font(None, 24)

def draw_interface():
    global screen, current_player, selected_attack, selected_change

    screen.fill(WHITE)

    # Asegúrate de que small_font esté inicializado
    try:
        small_font
    except NameError:
        small_font = pygame.font.Font(None, 24)

    # Dibujar información de los luchadores
    fighter1 = players[0][active_fighter[0]]
    fighter2 = players[1][active_fighter[1]]

    # Dibujar barras de HP y nombres
    if not fighter1.is_defeated():
        draw_text(f"{fighter1.name} HP: {fighter1.hp}/{fighter1.max_hp}", 50, 50, BLUE)
    if not fighter2.is_defeated():
        draw_text(f"{fighter2.name} HP: {fighter2.hp}/{fighter2.max_hp}", 700, 50, RED)

    # Dibujar botones de ataques
    button_width = 180
    button_height = 40
    button_x_start = 100
    button_y = 550
    button_spacing = 10

    current_fighter = players[current_player][active_fighter[current_player]]
    for i, attack in enumerate(current_fighter.attacks):
        button_x = button_x_start + i * (button_width + button_spacing)
        button_color = SELECTED_COLOR if selected_attack == i else DARK_GRAY

        pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))

        text_surface = font.render(attack.name, True, WHITE)
        text_rect = text_surface.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(text_surface, text_rect)

    # Botón de "Cambiar"
    change_button_x = 450
    change_button_y = 620
    change_button_width = 140
    change_button_height = 40

    change_color = SELECTED_COLOR if selected_change else DARK_GRAY
    pygame.draw.rect(screen, change_color, (change_button_x, change_button_y, change_button_width, change_button_height))

    change_text_surface = font.render("Cambiar", True, WHITE)
    change_text_rect = change_text_surface.get_rect(center=(change_button_x + change_button_width // 2, change_button_y + change_button_height // 2))
    screen.blit(change_text_surface, change_text_rect)

    # Dibujar luchadores y mostrar estadísticas
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if not fighter1.is_defeated():
        fighter1_frame = fighter1.get_current_frame()
        if fighter1_frame:
            fighter1_rect = fighter1_frame.get_rect(topleft=(50, 100))
            screen.blit(fighter1_frame, fighter1_rect.topleft)
            if fighter1_rect.collidepoint(mouse_x, mouse_y):
                stats_texts = [
                    f"Ataque Físico: {fighter1.physical_attack}",
                    f"Ataque Mágico: {fighter1.magic_attack}",
                    f"Velocidad: {fighter1.speed}",
                    f"Defensa: {fighter1.defense}",
                    f"Defensa Mágica: {fighter1.magic_defense}",
                    f"Estado: {fighter1.get_status()}"
                ]
                for i, text in enumerate(stats_texts):
                    stat_label = small_font.render(text, True, BLACK)
                    screen.blit(stat_label, (100, 400 + i * 20))

    if not fighter2.is_defeated():
        fighter2_frame = fighter2.get_current_frame()
        if fighter2_frame:
            fighter2_rect = fighter2_frame.get_rect(topleft=(700, 100))
            screen.blit(fighter2_frame, fighter2_rect.topleft)
            if fighter2_rect.collidepoint(mouse_x, mouse_y):
                stats_texts = [
                    f"Ataque Físico: {fighter2.physical_attack}",
                    f"Ataque Mágico: {fighter2.magic_attack}",
                    f"Velocidad: {fighter2.speed}",
                    f"Defensa: {fighter2.defense}",
                    f"Defensa Mágica: {fighter2.magic_defense}",
                    f"Estado: {fighter2.get_status()}"
                ]
                for i, text in enumerate(stats_texts):
                    stat_label = small_font.render(text, True, BLACK)
                    screen.blit(stat_label, (800, 400 + i * 20))





# Bucle principal del juego
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Verificar si se hizo clic en algún ataque
            for i in range(len(players[current_player][active_fighter[current_player]].attacks)):
                button_x = 100 + i * (180 + 10)  # Calcula la posición del botón en la iteración
                if button_x <= mouse_x <= button_x + 180 and 550 <= mouse_y <= 550 + 40:
                    selected_attack = i
                    selected_change = False
                    break

            # Verificar si se hizo clic en el botón "Cambiar"
            if 450 <= mouse_x <= 550 and 620 <= mouse_y <= 660:
                # Comprobar si hay otro luchador disponible para cambiar
                available_fighters = [fighter for fighter in players[current_player] if not fighter.is_defeated()]
                if len(available_fighters) > 1:
                    selected_attack = None
                    selected_change = True
                else:
                    # Mostrar un mensaje de error
                    print("No hay otros luchadores disponibles para cambiar.")
                    selected_attack = None
                    selected_change = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                attacker = players[current_player][active_fighter[current_player]]
                defender = players[1 - current_player][active_fighter[1 - current_player]]
                
                # Ejecutar el ataque seleccionado
                if selected_attack is not None:
                    attack = attacker.attacks[selected_attack]
                    attack_fighter(attacker, defender, attack)
                
                    # Restablecer la selección después de ejecutar la acción
                    selected_attack = None
                    selected_change = False
                
                    # Verificar derrotas y pasar el turno al siguiente jugador
                    check_defeat_and_switch()
                    current_player = 1 - current_player

                # Cambiar de luchador si se seleccionó el botón "Cambiar"
                elif selected_change:
                    # Verificar nuevamente si hay otro luchador disponible
                    available_fighters = [fighter for fighter in players[current_player] if not fighter.is_defeated()]
                    if len(available_fighters) > 1:
                        choose_fighter(current_player)
                        
                        # Restablecer la selección después de ejecutar la acción
                        selected_attack = None
                        selected_change = False
                        
                        # Verificar derrotas y pasar el turno al siguiente jugador
                        check_defeat_and_switch()
                        current_player = 1 - current_player
                    else:
                        # Si no hay otro luchador, mostrar mensaje y continuar el turno actual
                        print("No hay otros luchadores disponibles para cambiar.")

    # Actualizar animación de luchadores
    players[0][active_fighter[0]].update_animation()
    players[1][active_fighter[1]].update_animation()

    # Dibujar la interfaz en cada fotograma
    draw_interface()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
