import pygame
from node import Node
from connection import Connection
import random
import json
import math

class GraphEditor:
    def __init__(self, screen):
        self.screen = screen
        self.nodes = []
        self.connections = []
        self.selected_nodes = []
        self.selected_connections = []  # Change to selected_connections
        self.pan_offset = [0, 0]
        self.zoom = 1.0
        self.history = []
        self.future = []

    def handle_event(self, event):
        # Check for keydown events
        if event.type == pygame.KEYDOWN:
            print(f"event.type: {event.type}, event.key: {event.key}")  # Log event type and key
            # log key
            print(f"event.key: {event.key}")
            print(f"pygame.K_DELETE: {pygame.K_DELETE}")
            if event.key == pygame.K_RETURN:
                # Confirm all selected connections
                if self.selected_connections:
                    self.confirm_connections()  # Confirm all selected connections
                else:
                    self.create_node()  # Create a new node if no connection is unconfirmed
            elif event.key == pygame.K_BACKSPACE or event.key == 768:  # Handle DELETE key
                self.delete_selected()
            elif event.key == pygame.K_ESCAPE:
                self.selected_connections.clear()  # Clear only temporary connections
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.undo()
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.redo()
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save_graph()
            elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.load_graph()

        # Check for mouse button down events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_left_click(event.pos)
            elif event.button == 4:  # Scroll up (mouse wheel)
                self.zoom_in()
            elif event.button == 5:  # Scroll down (mouse wheel)
                self.zoom_out()
            elif event.button == 6:  # Two-finger scroll up (trackpad)
                self.zoom_in()
            elif event.button == 7:  # Two-finger scroll down (trackpad)
                self.zoom_out()

        # Check for mouse motion events
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # Left button held
                self.handle_drag(event.pos, event.rel)
            else:
                self.handle_mouse_motion(event.pos)

        # Check for trackpad events
        elif event.type == pygame.FINGERDOWN:  # Trackpad touch down
            print("Trackpad touch down")
        elif event.type == pygame.FINGERMOTION:  # Trackpad motion
            print("Trackpad motion detected")
        elif event.type == pygame.FINGERUP:  # Trackpad touch up
            print("Trackpad touch up")

    def create_node(self):
        # Create a new node in the center of the screen
        screen_center = [self.screen.get_width() // 2, self.screen.get_height() // 2]
        world_center = self.screen_to_world(screen_center)
        
        # Avoid overlapping with existing nodes
        while True:
            # Check if the new position is valid
            is_valid_position = True
            for node in self.nodes:
                distance = math.hypot(node.x - world_center[0], node.y - world_center[1])
                if distance < (node.radius + 20):  # 20 is the radius of the new node
                    is_valid_position = False
                    break
            
            if is_valid_position:
                break  # Exit the loop if the position is valid
            
            # Randomly adjust the position if it overlaps
            world_center[0] += random.randint(-50, 50)
            world_center[1] += random.randint(-50, 50)
        
        new_node = Node(world_center[0], world_center[1])
        self.nodes.append(new_node)
        self.add_to_history()

    def delete_selected(self):
        # Remove selected connections first
        self.connections = [c for c in self.connections if not c.selected]

        # Clear selection state for connections
        for connection in self.connections:
            connection.selected = False  # Deselect connections after deletion

        # Remove selected nodes and their connections
        for node in self.selected_nodes:
            self.nodes.remove(node)
            # Remove connections associated with the node
            self.connections = [c for c in self.connections if c.start_node != node and c.end_node != node]
        
        # Clear selected nodes after deletion
        self.selected_nodes.clear()

        self.add_to_history()

    def clear_canvas(self):
        # Clear all nodes and connections
        self.nodes.clear()
        self.connections.clear()
        self.selected_nodes.clear()
        self.selected_connections.clear()  # Clear the list after confirming
        self.add_to_history()

    def handle_left_click(self, pos):
        print(f"Left click at position: {pos}")  # Debugging line
        world_pos = self.screen_to_world(pos)
        clicked_node = self.get_node_at_position(world_pos)
        clicked_connection = self.get_connection_at_position(world_pos)

        if clicked_connection:
            # Toggle selection of the clicked connection
            clicked_connection.selected = not clicked_connection.selected
            if clicked_connection.selected:
                self.selected_connections.append(clicked_connection)
            else:
                if clicked_connection in self.selected_connections:  # Check if it's in the list
                    self.selected_connections.remove(clicked_connection)
            print(f"Selected connections: {self.selected_connections}")
            self.selected_nodes.clear()  # Clear node selection if a connection is selected
        elif clicked_node:
            print(f"Clicked node: {clicked_node}")  # Debugging line
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                # If Shift is held, add to selected nodes without creating connections
                if clicked_node not in self.selected_nodes:
                    self.selected_nodes.append(clicked_node)
            else:
                # Single select without dragging
                if self.selected_nodes:
                    self.selected_nodes.append(clicked_node)

                    print(f"Selected nodes: {self.selected_nodes}")

                    # Create dashed connections between all selected nodes and the new node
                    new_connections = []  # List to hold newly created connections
                    for node in self.selected_nodes[:-1]:  # Exclude the newly added node
                        if node != clicked_node:  # Check for self-connection
                            temp_connection = Connection(node, clicked_node)
                            temp_connection.confirmed = False  # Mark as temporary
                            self.selected_connections.append(temp_connection)
                        
                            new_connections.append(temp_connection)  # Add to the new connections list
                    print(f"New connections: {new_connections}")
                    print(f"Selected connections: {self.selected_connections}")
                    # select all connections in selected_connections
                    for connection in self.selected_connections:
                        connection.selected = True
                        self.connections.append(connection)
                    # Deselect all nodes
                    self.selected_nodes.clear()

                    # Select all newly created connections
                    for connection in new_connections:
                        connection.selected = True
                else:
                    # If no nodes are selected, just select the clicked node
                    self.selected_nodes = [clicked_node]
        else:
            # Clicked empty space, clear selection
            self.selected_nodes.clear()

    def handle_drag(self, pos, rel):
        world_pos = self.screen_to_world(pos)
        dragged_node = self.get_node_at_position(world_pos)

        if dragged_node:
            # Move the node without adding it to selected nodes
            dragged_node.x += rel[0] / self.zoom
            dragged_node.y += rel[1] / self.zoom
            self.selected_nodes.clear()  # Clear the selected nodes list after dragging
        else:
            # Only pan the canvas if no node is being dragged
            self.pan_offset[0] += rel[0] / self.zoom
            self.pan_offset[1] += rel[1] / self.zoom

    def zoom_in(self):
        self.zoom *= 1.1

    def zoom_out(self):
        self.zoom /= 1.1

    def update(self):
        for node in self.nodes:
            node.update()
        for connection in self.connections:
            connection.update()

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw connections
        for connection in self.connections:
            if connection in self.selected_connections:
                connection.draw(self.screen, self.pan_offset, self.zoom, dashed=True)
            else:
                connection.draw(self.screen, self.pan_offset, self.zoom)

        # Draw nodes
        for node in self.nodes:
            highlight = node in self.selected_nodes  # Check if the node is selected
            node.draw(self.screen, self.pan_offset, self.zoom, highlight=highlight)  # Pass highlight flag

    def screen_to_world(self, screen_pos):
        return [(screen_pos[0] / self.zoom) - self.pan_offset[0],
                (screen_pos[1] / self.zoom) - self.pan_offset[1]]

    def get_node_at_position(self, pos):
        for node in self.nodes:
            if node.is_inside(pos[0], pos[1]):
                return node
        return None

    def get_connection_at_position(self, pos):
        # debug connections
        print(f"Connections: {self.connections}")
        for connection in self.connections:
            print(f"is_inside: {connection.is_inside(pos[0], pos[1])}")
            if connection.is_inside(pos[0], pos[1]):
                return connection
        return None

    def export_graph(self):
        graph_data = {
            "nodes": [{"id": i, "x": node.x, "y": node.y} for i, node in enumerate(self.nodes)],
            "connections": [
                {"start": self.nodes.index(conn.start_node),
                 "end": self.nodes.index(conn.end_node)}
                for conn in self.connections
            ]
        }
        return json.dumps(graph_data, indent=2)

    def import_graph(self, json_data):
        graph_data = json.loads(json_data)
        self.clear_canvas()
        
        for node_data in graph_data["nodes"]:
            new_node = Node(node_data["x"], node_data["y"])
            self.nodes.append(new_node)
        
        for conn_data in graph_data["connections"]:
            start_node = self.nodes[conn_data["start"]]
            end_node = self.nodes[conn_data["end"]]
            new_connection = Connection(start_node, end_node)
            new_connection.confirmed = True
            self.connections.append(new_connection)
        
        self.add_to_history()

    def add_to_history(self):
        current_state = self.export_graph()
        self.history.append(current_state)
        self.future.clear()

    def undo(self):
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            previous_state = self.history[-1]
            self.import_graph(previous_state)

    def redo(self):
        if self.future:
            next_state = self.future.pop()
            self.import_graph(next_state)
            self.history.append(next_state)

    def confirm_connections(self):
        for connection in self.selected_connections:
            connection.confirmed = True
            self.connections.append(connection)
        self.selected_connections.clear()  # Clear the list after confirming
        self.add_to_history()

    def save_graph(self):
        graph_data = self.export_graph()
        with open("graph_data.json", "w") as f:
            f.write(graph_data)
        print("Graph saved successfully.")

    def load_graph(self):
        try:
            with open("graph_data.json", "r") as f:
                graph_data = f.read()
            self.import_graph(graph_data)
            print("Graph loaded successfully.")
        except FileNotFoundError:
            print("No saved graph found.")

    def handle_mouse_motion(self, pos):
        world_pos = self.screen_to_world(pos)
        for node in self.nodes:
            node.hover = node.is_inside(world_pos[0], world_pos[1])