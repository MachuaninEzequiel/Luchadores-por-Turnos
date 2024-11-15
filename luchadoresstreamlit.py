import streamlit as st
import random

# Inicialización de datos de los luchadores y ataques
class Attack:
    def __init__(self, name, damage=0, accuracy=1.0, attack_type="Físico", stat_change=None):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.attack_type = attack_type
        self.stat_change = stat_change

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

    def is_defeated(self):
        return self.hp <= 0

# Inicializar los luchadores y ataques
attacks_pool = [
    Attack("Punch", damage=10, accuracy=0.9, attack_type="Físico"),
    Attack("Fireball", damage=18, accuracy=0.75, attack_type="Mágico"),
    Attack("Speed Boost", attack_type="Estado", stat_change={"stat": "velocidad", "change": 5}),
    Attack("Heal", attack_type="Estado", stat_change={"stat": "curar", "change": 20}),
]

# Guardar la información inicial en `session_state` si no existe
if 'fighter1' not in st.session_state:
    st.session_state.fighter1 = Fighter("Fighter 1", 100, 15, 10, 8, 6, 20, attacks_pool[:4])
if 'fighter2' not in st.session_state:
    st.session_state.fighter2 = Fighter("Fighter 2", 100, 12, 15, 6, 8, 15, attacks_pool[:4])
if 'current_player' not in st.session_state:
    st.session_state.current_player = 0

# Función para manejar el ataque
def handle_attack(attack_index):
    attacker = st.session_state.fighter1 if st.session_state.current_player == 0 else st.session_state.fighter2
    defender = st.session_state.fighter2 if st.session_state.current_player == 0 else st.session_state.fighter1
    attack = attacker.attacks[attack_index]

    if attack.attempt_hit():
        damage = attack.damage + (0.5 * attacker.physical_attack if attack.attack_type == "Físico" else 0.5 * attacker.magic_attack)
        dealt_damage = defender.take_damage(damage, attack.attack_type)
        st.write(f"{attacker.name} used {attack.name} and dealt {dealt_damage} damage!")
    else:
        st.write(f"{attacker.name} used {attack.name} but it missed!")

    st.session_state.current_player = 1 - st.session_state.current_player  # Cambiar de turno

# Visualización en Streamlit
st.title("Turn-based Battle Game")

# Mostrar la información del jugador 1
st.subheader(f"{st.session_state.fighter1.name} HP: {st.session_state.fighter1.hp}/{st.session_state.fighter1.max_hp} ")
st.progress(st.session_state.fighter1.hp / st.session_state.fighter1.max_hp)
for i, attack in enumerate(st.session_state.fighter1.attacks):
    if st.button(f"Attack: {attack.name}", key=f"p1_attack_{i}"):
        if st.session_state.current_player == 0:
            handle_attack(i)

# Mostrar la información del jugador 2
st.subheader(f"{st.session_state.fighter2.name} HP: {st.session_state.fighter2.hp}/{st.session_state.fighter2.max_hp}")
st.progress(st.session_state.fighter2.hp / st.session_state.fighter2.max_hp)
for i, attack in enumerate(st.session_state.fighter2.attacks):
    if st.button(f"Attack: {attack.name}", key=f"p2_attack_{i}"):
        if st.session_state.current_player == 1:
            handle_attack(i)



# Mostrar el estado del juego
if st.session_state.fighter1.is_defeated():
    st.write("Jugador 2 gana!")
elif st.session_state.fighter2.is_defeated():
    st.write("Jugador 1 gana!")
