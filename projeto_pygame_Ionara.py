from pygame import Rect
import pgzrun

LARGURA, ALTURA = 800, 480
INICIO = "inicio"
music_on = True

class Button:
    def __init__(self, text, rect, action):
        self.text = text
        self.rect = Rect(rect)
        self.action = action
    def draw(self):
        screen.draw.filled_rect(self.rect, (40, 80, 160))
        screen.draw.rect(self.rect, (255, 255, 255))
        screen.draw.text(self.text, center=self.rect.center, fontsize=32, color="white")

BUTTONS = []
def make_menu():
    global BUTTONS
    BUTTONS = [
        Button("Jogar", (LARGURA//2-120, 160, 240, 50), "Jogar"),
        Button("Música Ligar/Desligar", (LARGURA//2-120, 230, 240, 50), "Música"),
        Button("Sair", (LARGURA//2-120, 300, 240, 50), "Sair"),
    ]
make_menu()

def start_music():
    if music_on:
        music.set_volume(0.5)
        try: music.play("bg")
        except: pass
    else:
        music.stop()

PLATAFORMA = [
    Rect(0,   440, 800, 40), 
    Rect(130, 360, 220, 20), 
    Rect(390, 290, 200, 20),  
    Rect(620, 230, 150, 20)   
]

def draw_platformas():
    for r in PLATAFORMA:
        screen.draw.filled_rect(r, (60, 60, 60))

class Animated:
    def __init__(self, x, y, idle_frames, walk_frames, speed=0):
        self.x = x; self.y = y
        self.vx = 0; self.vy = 0
        self.speed = speed
        self.idle_frames = idle_frames
        self.walk_frames = walk_frames
        self.state = "idle"
        self.frame = 0
        self.frame_time = 0
        self.actor = Actor(self.idle_frames[0], (self.x, self.y))

    def update_image(self):
        frames = self.idle_frames if self.state == "idle" else self.walk_frames
        self.actor.image = frames[self.frame % len(frames)]
        self.actor.pos = (self.x, self.y)

    def animate(self, dt, fps=8):
        self.frame_time += dt
        if self.frame_time >= 1.0 / fps:
            self.frame = (self.frame + 1) % (len(self.idle_frames) if self.state=="idle" else len(self.walk_frames))
            self.frame_time = 0
        self.update_image()

    def draw(self):
        self.actor.draw()

GRAVIDADE = 900
PULAR = -520 

class Hero(Animated):
    def __init__(self, x, y):
        super().__init__(x, y,
            idle_frames=["hero_idle1", "hero_idle2"],
            walk_frames=["hero_walk1", "hero_walk2", "hero_walk3"],
            speed=200
        )
    def update(self, dt):
        self.vx = 0
        if keyboard.left:  self.vx = -self.speed
        if keyboard.right: self.vx =  self.speed
        self.state = "walk" if self.vx != 0 else "idle"

        self.vy += GRAVIDADE * dt

        self.x += self.vx * dt; self.collide_axis("x")
        self.y += self.vy * dt; self.collide_axis("y")

        rect = self.actor._rect
        self.x = max(rect.width/2, min(LARGURA  - rect.width/2,  self.x))
        self.y = max(rect.height/2, min(ALTURA - rect.height/2, self.y))

        self.animate(dt)

    def collide_axis(self, axis):
        rect = self.actor._rect.copy(); rect.center = (self.x, self.y)
        for g in PLATAFORMA:
            if rect.colliderect(g):
                if axis == "y":
                    if self.vy > 0:  
                        self.y = g.top - rect.height/2
                        self.vy = 0
                    else:            
                        self.y = g.bottom + rect.height/2
                        self.vy = 0
                else:  
                    if self.vx > 0:
                        self.x = g.left - rect.width/2
                    elif self.vx < 0:
                        self.x = g.right + rect.width/2

    def on_jump(self):
        rect = self.actor._rect.copy(); rect.center = (self.x, self.y+2)
        if any(rect.colliderect(g) for g in PLATAFORMA):
            self.vy = PULAR
            try: sounds.jump.play()
            except: pass

class Enemy(Animated):
    def __init__(self, x, y, left, right, speed=80):
        super().__init__(x, y,
            idle_frames=["slime_idle1", "slime_idle2"],
            walk_frames=["slime_walk1", "slime_walk2"],
            speed=speed)
        self.left = left; self.right = right
        self.vx = speed

    def update(self, dt):
        self.state = "walk"
        self.x += self.vx * dt
        if self.x < self.left:
            self.x = self.left; self.vx = abs(self.vx)
        if self.x > self.right:
            self.x = self.right; self.vx = -abs(self.vx)
        self.animate(dt)

hero = Hero(60, 380)
enemies = [
    Enemy(440,  340, 360, 560, speed=70),  
    Enemy(700,  270, 620, 770, speed=80)   
    ]
goal = Rect(760, 140, 30, 220)

def reset_level():
    global enemies, INICIO
    hero.x, hero.y = 60, 380
    hero.vx = hero.vy = 0
    enemies = [
        Enemy(440, 340, 360, 560, speed=70),
        Enemy(700, 270, 620, 770, speed=80)
    ]
    INICIO = "jogar"
def shrunken_rect(actor, shrink=0.3):
    r = actor._rect.copy()
    r.inflate_ip(-r.width * shrink, -r.height * shrink)
    r.center = actor.pos
    return r
def draw():
    screen.clear()
    if INICIO == "inicio":
        screen.draw.text(" Aventuras da Io", center=(LARGURA//2, 90), fontsize=48, color="yellow")
        for b in BUTTONS: b.draw()

    elif INICIO == "jogar":
        screen.fill((20, 20, 30))
        draw_platformas()
        screen.draw.filled_rect(goal, (0, 120, 0))
        hero.draw()
        for e in enemies: e.draw()
        screen.draw.text("Chegue no verde!  ESPAÇO = pular | R = reiniciar", (20, 20), fontsize=24, color="white")

    elif INICIO == "perder":
        screen.fill((0, 0, 0))
        screen.draw.text("VOCÊ PERDEU!", center=(LARGURA//2, ALTURA//2 - 20), fontsize=64, color="red")
        screen.draw.text("Pressione R para reiniciar", center=(LARGURA//2, ALTURA//2 + 40), fontsize=30, color="white")

    elif INICIO == "vencer":
        screen.fill((0, 0, 0))
        screen.draw.text("VOCÊ VENCEU!", center=(LARGURA//2, ALTURA//2 - 20), fontsize=64, color="yellow")
        screen.draw.text("Pressione R para reiniciar", center=(LARGURA//2, ALTURA//2 + 40), fontsize=30, color="white")

def update(dt):
    if INICIO == "jogar":
        hero.update(dt)
        for e in enemies: e.update(dt)
        check_collisions()
def check_collisions():
    global INICIO
    hrect = shrunken_rect(hero.actor, shrink=0.2)
    for e in enemies:
        erect = shrunken_rect(e.actor, shrink=0.3)
        if hrect.colliderect(erect):
            try: sounds.hit.play()
            except: pass
            INICIO = "perder"
            return

    full_h = hero.actor._rect.copy(); full_h.center = (hero.x, hero.y)
    if full_h.colliderect(goal):
        INICIO = "vencer"

def on_key_down(key):
    if INICIO == "jogar":
        if key == keys.SPACE:
            hero.on_jump()
        elif key == keys.R:
            reset_level()
    elif INICIO in ("perder", "vencer"):
        if key == keys.R:
            reset_level()
def on_mouse_down(pos):
    global INICIO, music_on
    if INICIO == "inicio":
        for b in BUTTONS:
            if b.rect.collidepoint(pos):
                try: sounds.click.play()
                except: pass
                if b.action == "Jogar":
                    reset_level()
                    start_music()
                elif b.action == "Música":
                    music_on = not music_on; start_music()
                elif b.action == "Sair":
                    exit()

pgzrun.go()
