import pygame
import sys
from graph_editor import GraphEditor

def main():
    print("Starting the application...")
    pygame.init()
    print("Pygame initialized successfully.")
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Graph Editor")

    editor = GraphEditor(screen)
    print("GraphEditor initialized successfully.")

    clock = pygame.time.Clock()  # Create a Clock object
    fps = 144  # Set the desired frames per second

    while True:
        for event in pygame.event.get():
            # print(f"Event type: {event.type}")
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            editor.handle_event(event)

        editor.update()
        editor.draw()
        pygame.display.flip()

        clock.tick(fps)  # Control the frame rate

if __name__ == "__main__":
    main()