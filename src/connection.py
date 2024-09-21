import pygame
import math

class Connection:
    def __init__(self, start_node, end_node):
        if start_node == end_node:  # Check if nodes are the same
            raise ValueError("A connection cannot start and end at the same node.")
        self.start_node = start_node
        self.end_node = end_node
        self.color = (100, 100, 100)
        self.width = 3  # Increase the width for better visibility
        self.confirmed = False
        self.selected = False  # Add a selected attribute

    def update(self):
        # Update logic if needed
        pass

    def draw(self, screen, pan_offset, zoom, dashed=False):
        start_pos = (
            (self.start_node.x + pan_offset[0]) * zoom,
            (self.start_node.y + pan_offset[1]) * zoom
        )
        end_pos = (
            (self.end_node.x + pan_offset[0]) * zoom,
            (self.end_node.y + pan_offset[1]) * zoom
        )

        # Ensure start_pos and end_pos are valid
        if start_pos == end_pos:  # Prevent drawing if positions are the same
            return

        if dashed:
            self._draw_dashed_line(screen, start_pos, end_pos, zoom)
        else:
            pygame.draw.line(screen, self.color, start_pos, end_pos, int(self.width * zoom))

        # Draw arrowhead
        self._draw_arrow(screen, start_pos, end_pos, zoom)

    def _draw_dashed_line(self, screen, start_pos, end_pos, zoom):
        dash_length = 10
        space_length = 5
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance == 0:  # Check for zero distance
            return  # Exit the function if start and end positions are the same
        unit_x = dx / distance
        unit_y = dy / distance
        
        for i in range(int(distance / (dash_length + space_length))):
            start = i * (dash_length + space_length)
            end = start + dash_length
            pygame.draw.line(
                screen,
                self.color,
                (x1 + unit_x * start, y1 + unit_y * start),
                (x1 + unit_x * end, y1 + unit_y * end),
                int(self.width * zoom)
            )

    def _draw_arrow(self, screen, start_pos, end_pos, zoom):
        arrow_size = 10  # Size of the arrowhead
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        angle = math.atan2(dy, dx)

        # Calculate the position at the edge of the end node
        end_node_radius = self.end_node.radius * zoom  # Adjust for zoom
        adjusted_end_pos = (
            end_pos[0] - end_node_radius * math.cos(angle),
            end_pos[1] - end_node_radius * math.sin(angle)
        )

        # Calculate the points for the arrowhead
        arrow_point1 = (adjusted_end_pos[0] - arrow_size * math.cos(angle - math.pi / 6),
                        adjusted_end_pos[1] - arrow_size * math.sin(angle - math.pi / 6))
        arrow_point2 = (adjusted_end_pos[0] - arrow_size * math.cos(angle + math.pi / 6),
                        adjusted_end_pos[1] - arrow_size * math.sin(angle + math.pi / 6))

        # Draw the arrowhead
        pygame.draw.polygon(screen, self.color, [adjusted_end_pos, arrow_point1, arrow_point2])

    def is_inside(self, x, y, tolerance=1):
        # Check if a point is on the connection line
        x1, y1 = self.start_node.x, self.start_node.y
        x2, y2 = self.end_node.x, self.end_node.y
        
        d1 = math.dist((x, y), (x1, y1))
        d2 = math.dist((x, y), (x2, y2))
        line_length = math.dist((x1, y1), (x2, y2))
        
        buffer = tolerance

        return abs(d1 + d2 - line_length) < buffer  # Check if point is near the line