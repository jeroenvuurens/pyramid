import os
import json
import time
import socket
import selectors

os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_VIDEODRIVER', 'fbcon')

import pygame

pygame.init()
HEIGHT=1920
WIDTH=1080
screen = pygame.display.set_mode((HEIGHT, WIDTH))
screen.fill((0, 0, 0))
pygame.display.update()

# Persistent state
all_styles = {}
all_structures = {}
all_objects = {}

class CallbackBot:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.on_connect = None
        self.on_message = None
        self.on_disconnect = None
        self.connections = 

    def listen(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        server.setblocking(False)
        self.selector.register(server, selectors.EVENT_READ, data=("server", None))

    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex((host, port))
        self.selector.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=("client", None))

    def send(self, sock, msg):
        sock.send(msg.encode())

    def poll(self, timeout=0):
        """Call this periodically instead of running a loop forever."""
        events = self.selector.select(timeout)
        for key, mask in events:
            sock = key.fileobj
            typ, _ = key.data

            # new incoming connection
            if typ == "server" and mask & selectors.EVENT_READ:
                conn, addr = sock.accept()
                conn.setblocking(False)
                self.selector.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, data=("peer", addr))
                if self.on_connect:
                    self.on_connect(conn, addr)
                continue

            # received data
            if mask & selectors.EVENT_READ:
                data = sock.recv(4096)
                if not data:
                    self.selector.unregister(sock)
                    sock.close()
                    if self.on_disconnect:
                        self.on_disconnect(sock)
                else:
                    if self.on_message:
                        self.on_message(sock, data.decode())
        

# Create TCP server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 9999))
s.listen(1)
print("FB server listening...")

def draw_object(obj, structures, styles):
    struct = structures.get(obj['structure'])
    if not struct:
        return
    params = obj.get('params', {})
    for comp in struct['components']:
        ctype = comp['type']
        style_name = comp.get('style')
        style = styles.get(style_name, {})
        color = tuple(style.get('color', (255,255,255)))
        thickness = style.get('thickness', 1)
        if ctype == 'rect':
            rect = params.get(comp['name'], comp.get('rect', [0,0,100,100]))
            pygame.draw.rect(screen, color, rect, thickness)
        elif ctype == 'circle':
            circle = params.get(comp['name'], comp.get('circle', [50,50,30]))
            pygame.draw.circle(screen, color, (circle[0], circle[1]), circle[2], thickness)
        elif ctype == 'polygon':
            points = params.get(comp['name'], comp.get('rect_corners', []))
            if points:
                pygame.draw.polygon(screen, color, points, thickness)

while True:
    time.sleep(0.01)
    conn, addr = s.accept()
    data = conn.recv(4096)
    if not data:
        conn.close()
        continue
    cmd = json.loads(data.decode())
    # Update persistent styles
    for k, v in cmd.get('styles', {}).items():
        all_styles[k] = v
    # Update persistent structures
    for k, v in cmd.get('structures', {}).items():
        all_structures[k] = v
    # Update persistent objects (replace or add by name)
    if 'objects' in cmd:
        for obj in cmd['objects']:
            all_objects[obj['name']] = obj
    # Render all current objects
    screen.fill((0,0,0))  # clear screen
    for obj in all_objects.values():
        draw_object(obj, all_structures, all_styles)
    pygame.display.update()
    conn.close()
