import pygame
import math

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = (200, 200, 200)
        self.selected = False
        self.hover = False

    def update(self):
        # Return a fixed radius when hovered or not hovered
        if self.hover:
            return self.radius + 1  # Slightly larger when hovered
        return self.radius  # Stable radius when not hovered

    def draw(self, screen, pan_offset, zoom, highlight=False):
        # Calculate position with pan and zoom
        pos = ((self.x + pan_offset[0]) * zoom, (self.y + pan_offset[1]) * zoom)
        
        # Draw the node (e.g., as a circle)
        color = (180, 180, 180)  # Light grey color for the node
        if self.hover:  # Change color if hovered
            color = (210, 210, 210)  # Change to light green when hovered
        pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), int(self.radius * zoom))

        if highlight:  # If the node is highlighted
            self.draw_dashed_border(screen, pos, zoom)  # Call the method to draw dashed border

    def draw_dashed_border(self, screen, pos, zoom):
        # Draw a dashed border around the node
        highlight_color = (80, 80, 80)
        dash_length = 20
        space_length = 20
        for i in range(0, 360, dash_length + space_length):
            start_angle = math.radians(i)
            end_angle = math.radians(i + dash_length)
            start_pos = (pos[0] + self.radius * zoom * math.cos(start_angle),
                         pos[1] + self.radius * zoom * math.sin(start_angle))
            end_pos = (pos[0] + self.radius * zoom * math.cos(end_angle),
                       pos[1] + self.radius * zoom * math.sin(end_angle))
            pygame.draw.line(screen, highlight_color, start_pos, end_pos, 4)  # Draw dashed line

    def is_inside(self, x, y):
        # Check if a point is inside the node using the updated radius
        adjusted_radius = self.update()  # Get the current radius considering hover
        distance = ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5
        return distance <= adjusted_radius