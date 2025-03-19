import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos, radians

# Define colors for each suit
SUIT_COLORS = {
    "hearts": (1.0, 0.0, 0.0),  # Red
    "diamonds": (0.0, 0.0, 1.0),  # Blue
    "clubs": (0.0, 0.5, 0.0),  # Green
    "spades": (0.0, 0.0, 0.0),  # Black
}

# Card dimensions
CARD_WIDTH = 1.5
CARD_HEIGHT = 2.0
CARD_THICKNESS = 0.008

# Mouse rotation sensitivity
ROTATION_SENSITIVITY = 0.5

def draw_text(x, y, text, color):
    """Render text on the screen using Pygame."""
    font = pygame.font.SysFont("arial", 32)
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos2f(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_card_front(rank, suit):
    """Draw the front of the card with the rank and suit."""
    glColor3f(*SUIT_COLORS[suit])  # Set suit color
    glBegin(GL_QUADS)
    glVertex3f(-CARD_WIDTH / 2, -CARD_HEIGHT / 2, CARD_THICKNESS / 2)
    glVertex3f(CARD_WIDTH / 2, -CARD_HEIGHT / 2, CARD_THICKNESS / 2)
    glVertex3f(CARD_WIDTH / 2, CARD_HEIGHT / 2, CARD_THICKNESS / 2)
    glVertex3f(-CARD_WIDTH / 2, CARD_HEIGHT / 2, CARD_THICKNESS / 2)
    glEnd()

    # Display rank and suit
    glColor3f(1.0, 1.0, 1.0)  # White text
    draw_text(-0.2, 0.8, rank, (255, 255, 255))
    draw_text(-0.2, 0.6, suit, (255, 255, 255))

def draw_card_back():
    """Draw the back of the card (plain white)."""
    glColor3f(1.0, 1.0, 1.0)  # White
    glBegin(GL_QUADS)
    glVertex3f(-CARD_WIDTH / 2, -CARD_HEIGHT / 2, -CARD_THICKNESS / 2)
    glVertex3f(CARD_WIDTH / 2, -CARD_HEIGHT / 2, -CARD_THICKNESS / 2)
    glVertex3f(CARD_WIDTH / 2, CARD_HEIGHT / 2, -CARD_THICKNESS / 2)
    glVertex3f(-CARD_WIDTH / 2, CARD_HEIGHT / 2, -CARD_THICKNESS / 2)
    glEnd()

def draw_card(rank, suit):
    """Draw the entire card (front and back)."""
    draw_card_front(rank, suit)
    draw_card_back()

def main():
    # Get user input for rank and suit
    rank = input("Enter the rank (e.g., A, 2, 3, ..., K): ").strip().upper()
    suit = input("Enter the suit (hearts, diamonds, clubs, spades): ").strip().lower()

    if suit not in SUIT_COLORS:
        print("Invalid suit! Please choose from hearts, diamonds, clubs, or spades.")
        return

    # Initialize Pygame and OpenGL
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # Mouse rotation variables
    mouse_dragging = False
    last_mouse_pos = (0, 0)
    rotation_x, rotation_y = 0, 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = True
                    last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_dragging:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    rotation_x += dy * ROTATION_SENSITIVITY
                    rotation_y += dx * ROTATION_SENSITIVITY
                    last_mouse_pos = event.pos

        # Clear screen and set up transformation
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)

        # Draw the card
        draw_card(rank, suit)

        # Reset transformation
        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()