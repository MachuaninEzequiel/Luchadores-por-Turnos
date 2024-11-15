import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SELECTED_COLOR = (100, 100, 255)

class Node:
    def __init__(self, x, y, battle=True):
        self.x = x
        self.y = y
        self.battle = battle
        self.connected_nodes = []
        self.selected = False

    def connect(self, other_node):
        self.connected_nodes.append(other_node)

    def draw(self, screen):
        color = SELECTED_COLOR if self.selected else BLUE if self.battle else GREEN
        pygame.draw.circle(screen, color, (self.x, self.y), 15)

class NodeMap:
    def __init__(self, screen):
        self.screen = screen
        self.nodes = []
        self.current_node = None
        self.create_nodes()

    def create_nodes(self):
        # Crear nodos en posiciones aleatorias, por ejemplo
        for i in range(5):
            x = random.randint(100, 1000)
            y = random.randint(100, 600)
            node = Node(x, y)
            if i > 0:
                self.nodes[i - 1].connect(node)
            self.nodes.append(node)
        self.current_node = self.nodes[0]
        self.current_node.selected = True

    def draw(self):
        for node in self.nodes:
            node.draw(self.screen)
            for connected_node in node.connected_nodes:
                pygame.draw.line(self.screen, BLACK, (node.x, node.y), (connected_node.x, connected_node.y), 2)

    def select_next_node(self):
        for node in self.current_node.connected_nodes:
            node.selected = True
            self.current_node = node
            break  # Select only the next node

    def get_selected_node(self):
        return self.current_node
