import pygame

pygame.init()

# ---------------- WINDOW ----------------
WIDTH = 1000
HEIGHT = 650
TOOLBAR_HEIGHT = 80
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Practice 11")
clock = pygame.time.Clock()

# ---------------- FONTS ----------------
font = pygame.font.SysFont("Verdana", 18)
small_font = pygame.font.SysFont("Verdana", 14)

# ---------------- COLORS ----------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
LIGHT_GRAY = (210, 210, 210)
RED = (220, 30, 30)
GREEN = (30, 180, 30)
BLUE = (30, 30, 220)
YELLOW = (255, 220, 0)
PURPLE = (150, 60, 200)

# ---------------- TOOLS ----------------
TOOL_BRUSH = "brush"
TOOL_RECT = "rectangle"
TOOL_CIRCLE = "circle"
TOOL_ERASER = "eraser"
TOOL_SQUARE = "square"
TOOL_TRIANGLE = "triangle"
TOOL_EQ_TRIANGLE = "eq_triangle"
TOOL_RHOMBUS = "rhombus"

current_tool = TOOL_BRUSH
current_color = BLUE
brush_size = 8

# ---------------- CANVAS ----------------
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

drawing = False
start_pos = None
current_pos = None
last_pos = None

# ---------------- PALETTE ----------------
palette = [
    (BLACK, pygame.Rect(20, 20, 30, 30)),
    (RED, pygame.Rect(60, 20, 30, 30)),
    (GREEN, pygame.Rect(100, 20, 30, 30)),
    (BLUE, pygame.Rect(140, 20, 30, 30)),
    (YELLOW, pygame.Rect(180, 20, 30, 30)),
    (PURPLE, pygame.Rect(220, 20, 30, 30)),
]

# ---------------- TOOL BUTTONS ----------------
tool_buttons = {
    TOOL_BRUSH: pygame.Rect(300, 15, 80, 40),
    TOOL_RECT: pygame.Rect(390, 15, 90, 40),
    TOOL_CIRCLE: pygame.Rect(490, 15, 90, 40),
    TOOL_ERASER: pygame.Rect(590, 15, 90, 40),
    TOOL_SQUARE: pygame.Rect(690, 15, 90, 40),
    TOOL_TRIANGLE: pygame.Rect(790, 15, 100, 40),
    TOOL_EQ_TRIANGLE: pygame.Rect(900, 15, 90, 40),
}

# ---------------- UI ----------------
def draw_toolbar():
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    for color, rect in palette:
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2 if color == current_color else 1)

    for tool, rect in tool_buttons.items():
        pygame.draw.rect(screen, YELLOW if tool == current_tool else WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        label = small_font.render(tool, True, BLACK)
        screen.blit(label, (rect.x + 5, rect.y + 10))

# ---------------- DRAW HELPERS ----------------
def draw_line(surface, color, start, end, width):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    steps = max(abs(dx), abs(dy))

    for i in range(steps + 1):
        x = int(start[0] + (end[0] - start[0]) * i / steps)
        y = int(start[1] + (end[1] - start[1]) * i / steps)
        pygame.draw.circle(surface, color, (x, y), width)

def canvas_position(pos):
    return pos[0], pos[1] - TOOLBAR_HEIGHT

def toolbar_hit(pos):
    return pos[1] < TOOLBAR_HEIGHT

# ---------------- PREVIEW ----------------
def draw_preview():
    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    if drawing and start_pos and current_pos:
        temp = canvas.copy()

        if current_tool == TOOL_RECT:
            rect = pygame.Rect(start_pos, (current_pos[0]-start_pos[0], current_pos[1]-start_pos[1]))
            pygame.draw.rect(temp, current_color, rect, 2)

        elif current_tool == TOOL_CIRCLE:
            rect = pygame.Rect(start_pos, (current_pos[0]-start_pos[0], current_pos[1]-start_pos[1]))
            pygame.draw.ellipse(temp, current_color, rect, 2)

        elif current_tool == TOOL_SQUARE:
            size = max(abs(current_pos[0]-start_pos[0]), abs(current_pos[1]-start_pos[1]))
            pygame.draw.rect(temp, current_color, (*start_pos, size, size), 2)

        elif current_tool == TOOL_TRIANGLE:
            points = [start_pos, (start_pos[0], current_pos[1]), current_pos]
            pygame.draw.polygon(temp, current_color, points, 2)

        elif current_tool == TOOL_EQ_TRIANGLE:
            size = abs(current_pos[0]-start_pos[0])
            points = [
                start_pos,
                (start_pos[0]-size//2, start_pos[1]+size),
                (start_pos[0]+size//2, start_pos[1]+size)
            ]
            pygame.draw.polygon(temp, current_color, points, 2)

        elif current_tool == TOOL_RHOMBUS:
            cx = (start_pos[0]+current_pos[0])//2
            cy = (start_pos[1]+current_pos[1])//2
            dx = abs(current_pos[0]-start_pos[0])//2
            dy = abs(current_pos[1]-start_pos[1])//2

            points = [(cx, cy-dy),(cx-dx, cy),(cx, cy+dy),(cx+dx, cy)]
            pygame.draw.polygon(temp, current_color, points, 2)

        screen.blit(temp, (0, TOOLBAR_HEIGHT))

# ---------------- COMMIT ----------------
def commit_shape():
    if not start_pos or not current_pos:
        return

    if current_tool == TOOL_RECT:
        pygame.draw.rect(canvas, current_color, (*start_pos, current_pos[0]-start_pos[0], current_pos[1]-start_pos[1]), 2)

    elif current_tool == TOOL_CIRCLE:
        pygame.draw.ellipse(canvas, current_color, (*start_pos, current_pos[0]-start_pos[0], current_pos[1]-start_pos[1]), 2)

    elif current_tool == TOOL_SQUARE:
        size = max(abs(current_pos[0]-start_pos[0]), abs(current_pos[1]-start_pos[1]))
        pygame.draw.rect(canvas, current_color, (*start_pos, size, size), 2)

    elif current_tool == TOOL_TRIANGLE:
        pygame.draw.polygon(canvas, current_color, [start_pos,(start_pos[0], current_pos[1]),current_pos], 2)

    elif current_tool == TOOL_EQ_TRIANGLE:
        size = abs(current_pos[0]-start_pos[0])
        points = [
            start_pos,
            (start_pos[0]-size//2, start_pos[1]+size),
            (start_pos[0]+size//2, start_pos[1]+size)
        ]
        pygame.draw.polygon(canvas, current_color, points, 2)

    elif current_tool == TOOL_RHOMBUS:
        cx = (start_pos[0]+current_pos[0])//2
        cy = (start_pos[1]+current_pos[1])//2
        dx = abs(current_pos[0]-start_pos[0])//2
        dy = abs(current_pos[1]-start_pos[1])//2

        points = [(cx, cy-dy),(cx-dx, cy),(cx, cy+dy),(cx+dx, cy)]
        pygame.draw.polygon(canvas, current_color, points, 2)

# ---------------- MAIN ----------------
def main():
    global drawing, start_pos, current_pos, last_pos, current_tool, current_color

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if toolbar_hit(event.pos):
                        for color, rect in palette:
                            if rect.collidepoint(event.pos):
                                current_color = color
                        for tool, rect in tool_buttons.items():
                            if rect.collidepoint(event.pos):
                                current_tool = tool
                    else:
                        drawing = True
                        start_pos = canvas_position(event.pos)
                        current_pos = start_pos
                        last_pos = start_pos

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    commit_shape()
                    drawing = False

            if event.type == pygame.MOUSEMOTION and drawing:
                current_pos = canvas_position(event.pos)

                if current_tool == TOOL_BRUSH:
                    draw_line(canvas, current_color, last_pos, current_pos, brush_size)
                elif current_tool == TOOL_ERASER:
                    draw_line(canvas, WHITE, last_pos, current_pos, brush_size*2)

                last_pos = current_pos

        draw_toolbar()
        draw_preview()
        pygame.display.flip()
        clock.tick(60)

main()