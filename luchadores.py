import pygame
import sys
import random

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 700))
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
    def __init__(self, name, damage=0, accuracy=1.0, attack_type="Físico", stat_change=None):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.attack_type = attack_type  # "Físico", "Mágico" o "Estado"
        self.stat_change = stat_change  # {'stat': 'velocidad', 'change': 10} por ejemplo

    def attempt_hit(self):
        return random.random() < self.accuracy

class Fighter:
    def __init__(self, name, hp, physical_attack, magic_attack, defense, magic_defense, speed, attacks):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.physical_attack = physical_attack
        self.magic_attack = magic_attack
        self.defense = defense
        self.magic_defense = magic_defense
        self.speed = speed
        self.attacks = attacks

    def take_damage(self, damage, attack_type):
        if attack_type == "Físico":
            damage -= self.defense * 0.5
        elif attack_type == "Mágico":
            damage -= self.magic_defense * 0.5

        damage = max(0, int(damage))  # Asegurarse de que el daño no sea negativo
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

    def is_defeated(self):
        return self.hp <= 0

# Crear los luchadores y ataques
attacks_pool = [
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Power Up", attack_type="Estado", stat_change={"stat": "ataque_fisico", "change": 5}),
    Attack("Magic Boost", attack_type="Estado", stat_change={"stat": "ataque_magico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
    Attack("Weaken", attack_type="Estado", stat_change={"stat": "defensa", "change": -5}),
    Attack("Slow Down", attack_type="Estado", stat_change={"stat": "velocidad", "change": -5})
]

attacks_pool1 = [
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Magic Boost", attack_type="Estado", stat_change={"stat": "ataque_magico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
    Attack("Slow Down", attack_type="Estado", stat_change={"stat": "velocidad", "change": -5})
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
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Power Up", attack_type="Estado", stat_change={"stat": "ataque_fisico", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
]

fighter1 = Fighter("Fighter 1", 100, 15, 10, 8, 6, 20, attacks_pool1[:5])
fighter2 = Fighter("Fighter 2", 100, 12, 15, 6, 8, 15, attacks_pool2[:5])
fighter3 = Fighter("Fighter 3", 100, 13, 12, 7, 7, 18, attacks_pool3[:5])
fighter4 = Fighter("Fighter 4", 100, 10, 15, 5, 10, 12, attacks_pool4[:5])

players = [
    [fighter1, fighter2],  # Jugador 1
    [fighter3, fighter4]   # Jugador 2
]

# Variables de estado del juego
current_player = 0
active_fighter = [0, 0]  # Índice del luchador activo por cada jugador
turn = 0
selected_attack = None
selected_change = False

# Funciones auxiliares
def draw_text(text, x, y, color=BLACK):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def draw_interface():
    screen.fill(WHITE)

    # Dibujar información de los luchadores
    fighter1 = players[0][active_fighter[0]]
    fighter2 = players[1][active_fighter[1]]

    # Dibujar barras de HP y nombres si los luchadores no están derrotados
    if not fighter1.is_defeated():
        draw_text(f"{fighter1.name} HP: {fighter1.hp}/{fighter1.max_hp}", 50, 50, BLUE)
    if not fighter2.is_defeated():
        draw_text(f"{fighter2.name} HP: {fighter2.hp}/{fighter2.max_hp}", 700, 50, RED)

    # Dibujar botones de ataques en fila en la parte inferior
    current_fighter = players[current_player][active_fighter[current_player]]
    for i, attack in enumerate(current_fighter.attacks):
        button_color = SELECTED_COLOR if selected_attack == i else DARK_GRAY
        pygame.draw.rect(screen, button_color, (100 + i * 160, 550, 140, 40))
        draw_text(attack.name, 110 + i * 160, 560, WHITE)

    # Dibujar botón de "Cambiar" debajo de los ataques
    change_color = SELECTED_COLOR if selected_change else DARK_GRAY
    pygame.draw.rect(screen, change_color, (450, 620, 100, 40))
    draw_text("Cambiar", 465, 630, WHITE)

def attack_fighter(attacker, defender, attack):
    if attack.attempt_hit():
        if attack.attack_type == "Físico":
            damage = attack.damage + 0.5 * attacker.physical_attack
            final_damage = defender.take_damage(damage, "Físico")
            print(f"{attacker.name} used {attack.name} and dealt {final_damage} damage!")
        elif attack.attack_type == "Mágico":
            damage = attack.damage + 0.5 * attacker.magic_attack
            final_damage = defender.take_damage(damage, "Mágico")
            print(f"{attacker.name} used {attack.name} and dealt {final_damage} damage!")
        elif attack.attack_type == "Estado" and attack.stat_change:
            # Determina si el cambio de estado debe aplicarse al atacante o al defensor
            if attack.name in ["Speed Boost", "Power Up", "Magic Boost", "Heal"]:
                # Estos ataques afectan al propio luchador
                target = attacker
            else:
                # Los demás afectan al oponente
                target = defender
            
            # Aplicar cambio de estado
            target.apply_stat_change(attack.stat_change['stat'], attack.stat_change['change'])
            print(f"{attacker.name} used {attack.name} and applied {attack.stat_change['stat']} change on {target.name}!")
    else:
        print(f"{attacker.name} used {attack.name} but it missed!")

def next_fighter(player_index):
    global active_fighter
    active_fighter[player_index] = (active_fighter[player_index] + 1) % len(players[player_index])

def check_defeat_and_switch():
    global running  # Para terminar el bucle del juego si un jugador pierde todos los luchadores
    for i in range(2):
        current_fighter = players[i][active_fighter[i]]
        if current_fighter.is_defeated():
            # Cambiar al siguiente luchador si el actual es derrotado
            next_fighter(i)
            # Verificar si todos los luchadores están derrotados
            if all(fighter.is_defeated() for fighter in players[i]):
                print(f"Player {1 - i + 1} wins!")  # Anunciar la victoria del jugador contrario
                running = False  # Finalizar el juego
                return  # Salir de la función para evitar errores

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
                if 100 + i * 160 <= mouse_x <= 240 + i * 160 and 550 <= mouse_y <= 590:
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
                        next_fighter(current_player)
                        
                        # Restablecer la selección después de ejecutar la acción
                        selected_attack = None
                        selected_change = False
                        
                        # Verificar derrotas y pasar el turno al siguiente jugador
                        check_defeat_and_switch()
                        current_player = 1 - current_player
                    else:
                        # Si no hay otro luchador, mostrar mensaje y continuar el turno actual
                        print("No hay otros luchadores disponibles para cambiar.")

    # Dibujar la interfaz en cada fotograma
    draw_interface()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()