

import pygame
import datetime
import os
from tools import draw_line_smooth, flood_fill

pygame.init()

# ── Window ────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1100, 680
TOOLBAR_H = 90
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint — TSIS 2")
clock = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────────────────────────
small_font = pygame.font.SysFont("Verdana", 13)
text_font  = pygame.font.SysFont("Arial", 20)

# ── Colors ────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
LIGHT_GRAY = (215, 215, 215)
DARK_GRAY  = (80,  80,  80)
HIGHLIGHT  = (255, 220,  50)

PALETTE = [
    (0,   0,   0),
    (255, 255, 255),
    (220, 30,  30),
    (30,  180, 30),
    (30,  30,  220),
    (255, 220, 0),
    (150, 60,  200),
    (255, 140, 0),
    (0,   200, 200),
    (180, 90,  40),
]

# ── Tools ─────────────────────────────────────────────────────────
TOOLS = [
    "pencil", "line", "rectangle", "circle",
    "square", "triangle", "eq_triangle", "rhombus",
    "eraser", "fill", "text",
]

# ── State ─────────────────────────────────────────────────────────
current_tool  = "pencil"
current_color = BLACK
brush_size    = 5          # medium default

drawing    = False
start_pos  = None
curr_pos   = None
last_pos   = None

# Text-tool state
text_active = False
text_pos    = None
text_buffer = ""

# ── Canvas ────────────────────────────────────────────────────────
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill(WHITE)

# ── Layout helpers ────────────────────────────────────────────────
def _btn(x, y, w=78, h=32):
    return pygame.Rect(x, y, w, h)

# Palette rects  (top-left of toolbar)
palette_rects = [pygame.Rect(10 + i * 34, 10, 28, 28) for i in range(len(PALETTE))]

# Tool buttons  (two rows)
ROW1_Y, ROW2_Y = 8, 46
tool_rects = {}
tool_labels = {
    "pencil":      "Pencil",
    "line":        "Line",
    "rectangle":   "Rect",
    "circle":      "Circle",
    "square":      "Square",
    "triangle":    "Tri-R",
    "eq_triangle": "Tri-Eq",
    "rhombus":     "Rhombus",
    "eraser":      "Eraser",
    "fill":        "Fill",
    "text":        "Text",
}

_tool_order = list(tool_labels.keys())
for i, t in enumerate(_tool_order[:6]):
    tool_rects[t] = _btn(360 + i * 84, ROW1_Y)
for i, t in enumerate(_tool_order[6:]):
    tool_rects[t] = _btn(360 + i * 84, ROW2_Y)

# Brush-size buttons
SIZE_BTNS = {
    2:  pygame.Rect(950, 10, 42, 28),
    5:  pygame.Rect(997, 10, 42, 28),
    10: pygame.Rect(1044, 10, 42, 28),
}

# ── Draw toolbar ──────────────────────────────────────────────────
def draw_toolbar():
    pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, WIDTH, TOOLBAR_H))

    # Palette
    for color, rect in zip(PALETTE, palette_rects):
        pygame.draw.rect(screen, color, rect)
        border = 3 if color == current_color else 1
        pygame.draw.rect(screen, BLACK, rect, border)

    # Current color preview
    pygame.draw.rect(screen, current_color, pygame.Rect(360-38, 10, 28, 28))
    pygame.draw.rect(screen, BLACK, pygame.Rect(360-38, 10, 28, 28), 2)

    # Tool buttons
    for tool, rect in tool_rects.items():
        bg = HIGHLIGHT if tool == current_tool else WHITE
        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, DARK_GRAY, rect, 2)
        label = small_font.render(tool_labels[tool], True, BLACK)
        screen.blit(label, (rect.x + 4, rect.y + 8))

    # Brush size buttons
    for size, rect in SIZE_BTNS.items():
        bg = HIGHLIGHT if size == brush_size else WHITE
        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, DARK_GRAY, rect, 2)
        lbl = small_font.render(f"S{size}", True, BLACK)
        screen.blit(lbl, (rect.x + 6, rect.y + 6))

    # Hint
    hint = small_font.render("1/2/3 = size   Ctrl+S = save", True, DARK_GRAY)
    screen.blit(hint, (950, 52))

# ── Canvas utilities ──────────────────────────────────────────────
def to_canvas(pos):
    return (pos[0], pos[1] - TOOLBAR_H)

def in_toolbar(pos):
    return pos[1] < TOOLBAR_H

# ── Preview (live shape while dragging) ───────────────────────────
def draw_preview():
    screen.blit(canvas, (0, TOOLBAR_H))

    # Text cursor preview
    if text_active and text_pos:
        rendered = text_font.render(text_buffer + "|", True, current_color)
        screen.blit(rendered, (text_pos[0], text_pos[1] + TOOLBAR_H))
        return

    if not (drawing and start_pos and curr_pos):
        return

    tmp = canvas.copy()
    sp, cp = start_pos, curr_pos
    w = brush_size

    if current_tool == "line":
        draw_line_smooth(tmp, current_color, sp, cp, w)

    elif current_tool == "rectangle":
        pygame.draw.rect(tmp, current_color,
                         pygame.Rect(sp, (cp[0]-sp[0], cp[1]-sp[1])), w)

    elif current_tool == "circle":
        pygame.draw.ellipse(tmp, current_color,
                            pygame.Rect(sp, (cp[0]-sp[0], cp[1]-sp[1])), w)

    elif current_tool == "square":
        side = max(abs(cp[0]-sp[0]), abs(cp[1]-sp[1]))
        pygame.draw.rect(tmp, current_color, (*sp, side, side), w)
    elif current_tool == "triangle":

        pts = [sp, (sp[0], cp[1]), cp]
        pygame.draw.polygon(tmp, current_color, pts, w)

    elif current_tool == "eq_triangle":
        size = abs(cp[0]-sp[0])
        pts = [sp, (sp[0]-size//2, sp[1]+size), (sp[0]+size//2, sp[1]+size)]
        pygame.draw.polygon(tmp, current_color, pts, w)

    elif current_tool == "rhombus":
        cx = (sp[0]+cp[0])//2;  cy = (sp[1]+cp[1])//2
        dx = abs(cp[0]-sp[0])//2; dy = abs(cp[1]-sp[1])//2
        pts = [(cx, cy-dy), (cx-dx, cy), (cx, cy+dy), (cx+dx, cy)]
        pygame.draw.polygon(tmp, current_color, pts, w)

    screen.blit(tmp, (0, TOOLBAR_H))

# ── Commit shape to canvas
def commit_shape():
    if not (start_pos and curr_pos):
        return
    sp, cp = start_pos, curr_pos
    w = brush_size

    if current_tool == "line":
        draw_line_smooth(canvas, current_color, sp, cp, w)

    elif current_tool == "rectangle":
        pygame.draw.rect(canvas, current_color,
                         pygame.Rect(sp, (cp[0]-sp[0], cp[1]-sp[1])), w)

    elif current_tool == "circle":
        pygame.draw.ellipse(canvas, current_color,
                            pygame.Rect(sp, (cp[0]-sp[0], cp[1]-sp[1])), w)

    elif current_tool == "square":
        side = max(abs(cp[0]-sp[0]), abs(cp[1]-sp[1]))
        pygame.draw.rect(canvas, current_color, (*sp, side, side), w)

    elif current_tool == "triangle":
        pts = [sp, (sp[0], cp[1]), cp]
        pygame.draw.polygon(canvas, current_color, pts, w)

    elif current_tool == "eq_triangle":
        size = abs(cp[0]-sp[0])
        pts = [sp, (sp[0]-size//2, sp[1]+size), (sp[0]+size//2, sp[1]+size)]
        pygame.draw.polygon(canvas, current_color, pts, w)

    elif current_tool == "rhombus":
        cx = (sp[0]+cp[0])//2;  cy = (sp[1]+cp[1])//2
        dx = abs(cp[0]-sp[0])//2; dy = abs(cp[1]-sp[1])//2
        pts = [(cx, cy-dy), (cx-dx, cy), (cx, cy+dy), (cx+dx, cy)]
        pygame.draw.polygon(canvas, current_color, pts, w)

# ── Save canvas
def save_canvas():
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"canvas_{ts}.png"
    pygame.image.save(canvas, name)
    print(f"[OK] Saved: {name}")

# ── Main loop
def main():
    global drawing, start_pos, curr_pos, last_pos
    global current_tool, current_color, brush_size
    global text_active, text_pos, text_buffer

    running = True
    while running:
        for event in pygame.event.get():

            # ── Quit
            if event.type == pygame.QUIT:
                running = False

            #Keyboard
            elif event.type == pygame.KEYDOWN:

                # Text tool input
                if text_active:
                    if event.key == pygame.K_RETURN:
                        # Commit text to canvas
                        rendered = text_font.render(text_buffer, True, current_color)
                        canvas.blit(rendered, text_pos)
                        text_active = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
                    continue  # skip other key handling while typing

                # Ctrl+S — save
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    save_canvas()

                # Escape — quit
                elif event.key == pygame.K_ESCAPE:
                    running = False

                # Brush size shortcuts
                elif event.key == pygame.K_1:
                    brush_size = 2
                elif event.key == pygame.K_2:
                    brush_size = 5
                elif event.key == pygame.K_3:
                    brush_size = 10

            #Mouse down
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                if in_toolbar(pos):
                    # Palette
                    for color, rect in zip(PALETTE, palette_rects):
                        if rect.collidepoint(pos):
                            current_color = color

                    # Tool buttons
                    for tool, rect in tool_rects.items():
                        if rect.collidepoint(pos):
                            current_tool = tool
                            text_active  = False

                    # Size buttons
                    for size, rect in SIZE_BTNS.items():
                        if rect.collidepoint(pos):
                            brush_size = size

                else:
                    cp = to_canvas(pos)

                    if current_tool == "fill":
                        flood_fill(canvas, cp, current_color)

                    elif current_tool == "text":
                        text_active = True
                        text_pos    = cp
                        text_buffer = ""

                    else:
                        drawing   = True
                        start_pos = cp
                        curr_pos  = cp
                        last_pos  = cp

            #Mouse up
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing:
                    commit_shape()
                    drawing = False

            #Mouse motion
            elif event.type == pygame.MOUSEMOTION and drawing:
                curr_pos = to_canvas(event.pos)

                if current_tool == "pencil":
                    draw_line_smooth(canvas, current_color, last_pos, curr_pos, brush_size)
                elif current_tool == "eraser":
                    draw_line_smooth(canvas, WHITE, last_pos, curr_pos, brush_size * 3)

                last_pos = curr_pos

        #Render
        draw_toolbar()
        draw_preview()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()