import pygame
import math

pygame.init()

# --- KONFIGURASI LAYAR ---
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulasi Engine 4 Silinder FO 1 2 4 3 by Gathan Alfarabi Agusti")
clock = pygame.time.Clock()

# --- WARNA ---
BLACK    = (0, 0, 0)
WHITE    = (255, 255, 255)
GRAY     = (200, 200, 200)
DARKGRAY = (100, 100, 100)
BLUE     = (0, 0, 255)
RED      = (255, 0, 0)
LIGHTRED = (255, 100, 100)
GREEN    = (0, 200, 0)
DARKGREEN = (0, 150, 0)
SEMITRANSPARENT_GRAY = (100, 100, 100, 128)

font = pygame.font.SysFont(None, 24)

# Load background image
try:
    bg_path = os.path.join(BASE_DIR, "bocchi.png")
    if os.path.exists(bg_path):
        bg_image = pygame.image.load(bg_path).convert()
        print("Background bocchi.png berhasil dimuat.")
    else:
        raise FileNotFoundError
except Exception:
    print("Gagal memuat bocchi.png, menggunakan background abu-abu.")
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((200, 200, 200))


# Tombol
button_rect = pygame.Rect(400, 500, 200, 40)
left_button = pygame.Rect(300, 550, 100, 30)
right_button = pygame.Rect(600, 550, 100, 30)

engine_on = False

engine_cycle = {
    0: {1: ("Hisap", True, False), 2: ("Buang", False, True), 3: ("Kompresi", False, False), 4: ("Usaha", False, False)},
    1: {1: ("Kompresi", False, False), 2: ("Hisap", True, False), 3: ("Usaha", False, True), 4: ("Buang", True, True)},
    2: {1: ("Usaha", False, False), 2: ("Kompresi", False, False), 3: ("Buang", False, True), 4: ("Hisap", True, False)},
    3: {1: ("Buang", False, True), 2: ("Usaha", False, False), 3: ("Hisap", True, False), 4: ("Kompresi", False, False)},
    4: {1: ("Hisap", True, False), 2: ("Buang", False, True), 3: ("Kompresi", False, False), 4: ("Usaha", False, False)}
}

def get_cycle_data(angle, cyl):
    div = int(angle // 180)
    if div >= 4:
        div = 4
    next_div = div + 1 if div < 4 else 4

    base_angle = div * 180
    next_angle = next_div * 180 if next_div <= 4 else 720
    ratio = (angle - base_angle) / (next_angle - base_angle) if next_angle != base_angle else 0

    strokeA, inA, exA = engine_cycle[div][cyl]
    strokeB, inB, exB = engine_cycle[next_div][cyl]
    return (strokeA, inA, exA) if ratio < 0.5 else (strokeB, inB, exB)

offset_map = {1: 180, 2: 0, 3: 0, 4: 180}

R = 30
L = 80

def get_piston_disp(angle, cyl):
    offset = offset_map[cyl]
    theta = math.radians((angle + offset) % 360)
    return (L + R) - (R * math.cos(theta) + math.sqrt(max(0, L**2 - (R * math.sin(theta))**2)))

def get_relative_piston_pos(angle, cyl):
    disp = get_piston_disp(angle, cyl)
    disp_TDC = get_piston_disp(180, cyl) if cyl in [1, 4] else get_piston_disp(0, cyl)
    return disp - disp_TDC

def valve_adjustable_text(isOpen):
    return "Ga bisa disetel" if isOpen else "Bisa disetel"

def draw_cylinder(x, y, angle, cyl):
    stroke, in_open, ex_open = get_cycle_data(angle, cyl)
    pygame.draw.rect(screen, BLACK, (x, y, 80, 200), 3)
    piston_disp = get_relative_piston_pos(angle % 720, cyl)
    pygame.draw.rect(screen, DARKGRAY, (x+5, y+50 + piston_disp, 70, 30))
    intake_color = BLUE if in_open else BLACK
    exhaust_color = RED if ex_open else BLACK
    pygame.draw.circle(screen, intake_color, (x+20, y-20), 10)
    pygame.draw.circle(screen, exhaust_color, (x+60, y-20), 10)
    text_in = font.render(f"IN: {valve_adjustable_text(in_open)}", True, BLACK)
    text_ex = font.render(f"EX: {valve_adjustable_text(ex_open)}", True, BLACK)
    screen.blit(text_in, (x+5, y-80))
    screen.blit(text_ex, (x+5, y-60))
    label = font.render(f"Cyl {cyl}: {stroke}", True, BLACK)
    screen.blit(label, (x, y+210))

def draw_crankshaft(angle, center):
    pygame.draw.circle(screen, BLACK, center, 80, 3)
    angle_rad = math.radians(angle % 360)
    end_x = center[0] + int(60 * math.cos(angle_rad - math.pi/2))
    end_y = center[1] + int(60 * math.sin(angle_rad - math.pi/2))
    pygame.draw.line(screen, RED, center, (end_x, end_y), 4)
    label = font.render(f"Crankshaft: {angle % 720}°", True, BLACK)
    screen.blit(label, (center[0]-70, center[1]+90))

def draw_buttons():
    btn_color = DARKGREEN if engine_on else GREEN
    pygame.draw.rect(screen, btn_color, button_rect)
    label = font.render("Stop Engine" if engine_on else "Start Engine", True, WHITE)
    screen.blit(label, (button_rect.x + 50, button_rect.y + 10))
    pygame.draw.rect(screen, DARKGRAY, left_button)
    pygame.draw.rect(screen, DARKGRAY, right_button)
    screen.blit(font.render("<<", True, WHITE), (left_button.x + 35, left_button.y + 5))
    screen.blit(font.render(">>", True, WHITE), (right_button.x + 35, right_button.y + 5))

def draw_engine(angle):
    screen.blit(bg_image, (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(SEMITRANSPARENT_GRAY)
    screen.blit(overlay, (0, 0))
    base_x, base_y = 100, 200
    for cyl in range(1, 5):
        draw_cylinder(base_x + (cyl-1)*150, base_y, angle, cyl)
    draw_crankshaft(angle, (850, 300))
    draw_buttons()
    pygame.display.flip()

running = True
crank_angle = 180
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                engine_on = not engine_on
            elif left_button.collidepoint(event.pos):
                crank_angle = (crank_angle - 2) % 720
            elif right_button.collidepoint(event.pos):
                crank_angle = (crank_angle + 2) % 720

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        crank_angle = (crank_angle + 2) % 720
    if keys[pygame.K_LEFT]:
        crank_angle = (crank_angle - 2) % 720

    if engine_on:
        crank_angle = (crank_angle + 2) % 720

    draw_engine(crank_angle)

pygame.quit()
