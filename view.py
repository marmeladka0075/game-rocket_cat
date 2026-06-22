import pygame
import os


class GameView:
    def __init__(self, model):
        self.model = model
        self.width = 800
        self.height = 600

        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Rocket Cat: 8-bit Space Odyssey")

        self.font_large = pygame.font.SysFont("Courier New", 48, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 24, bold=True)

        self.color_bg = (10, 10, 30)
        self.color_player = (255, 140, 0)
        self.color_obstacle = (100, 100, 100)
        self.color_bone = (255, 215, 0)
        self.color_meteorite = (255, 50, 0)
        self.buff_colors = {"SHIELD": (0, 255, 255), "MAGNET": (255, 0, 255), "FUEL": (255, 50, 50)}

        self.bg_x = 0

        self.sprites = {}
        self.sounds = {}
        self.load_sprites()
        self.load_audio()

    def load_sprites(self):
        def load_image(name, size=None):
            path = os.path.join("assets", name)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    if size:
                        img = pygame.transform.scale(img, size)
                    return img
                except:
                    print(f"Ошибка загрузки {name}. Проверь формат файла!")
            return None

        self.sprites['bg'] = load_image("bg.png", (self.width, self.height))
        self.sprites['player'] = load_image("player.png", (55, 45))
        self.sprites['bone'] = load_image("fish.png", (25, 25))
        self.sprites['SHIELD'] = load_image("shield.png", (32, 32))
        self.sprites['MAGNET'] = load_image("magnet.png", (32, 32))
        self.sprites['FUEL'] = load_image("fuel.png", (32, 32))
        self.sprites['asteroid'] = load_image("asteroid.png")
        self.sprites['meteorite'] = load_image("meteorite.png", (80, 40))

        self.sprites['player_default'] = load_image("player.png")
        self.sprites['player_red_rocket'] = load_image("player_red_rocket.png")
        self.sprites['player_gold_rocket'] = load_image("player_gold_rocket.png")
        self.sprites['player_neon_rocket'] = load_image("player_neon_rocket.png")

    def load_audio(self):
        def load_sound(name):
            path = os.path.join("assets", name)
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
            return None

        self.sounds['jump'] = load_sound("jump.wav")
        self.sounds['fish'] = load_sound("fish.wav")
        self.sounds['buff'] = load_sound("buff.wav")
        self.sounds['crash'] = load_sound("crash.wav")

        music_path = os.path.join("assets", "music.mp3")
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.3)

    def play_sound(self, sound_name):
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def update_volume(self):
        pygame.mixer.music.set_volume(self.model.volume * 0.3)

    def play_music(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def draw_text(self, text, font, color, x, y, center=False):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def draw_bg(self, delta_time, speed):
        if self.sprites['bg']:
            self.bg_x -= (speed * 0.3) * delta_time
            if self.bg_x <= -self.width:
                self.bg_x = 0
            self.screen.blit(self.sprites['bg'], (self.bg_x, 0))
            self.screen.blit(self.sprites['bg'], (self.bg_x + self.width, 0))
        else:
            self.screen.fill(self.color_bg)

    def render(self):
        delta_time = 1.0 / 60.0
        current_speed = self.model.base_speed
        if self.model.game_state == "PLAYING":
            current_speed = self.model.base_speed * 3 if self.model.player.state == "FUEL" else self.model.base_speed

        self.draw_bg(delta_time if self.model.game_state == "PLAYING" else 0, current_speed)

        if self.model.game_state == "MENU":
            self.render_menu()

        elif self.model.game_state == "SETTINGS":
            self.render_settings()

        elif self.model.game_state == "SHOP":
            self.render_shop()

        elif self.model.game_state in ("PLAYING", "GAME_OVER"):
            ast_img = self.sprites.get('asteroid')
            for obs in self.model.obstacles:
                if ast_img:
                    top_ast = pygame.transform.scale(ast_img, (obs.width, obs.gap_y))
                    self.screen.blit(top_ast, (obs.x, 0))

                    bottom_y = obs.gap_y + obs.gap_size
                    bottom_height = self.height - bottom_y

                    if bottom_height > 0:
                        bottom_ast = pygame.transform.scale(ast_img, (obs.width, bottom_height))
                        self.screen.blit(bottom_ast, (obs.x, bottom_y))
                else:
                    pygame.draw.rect(self.screen, self.color_obstacle, (obs.x, 0, obs.width, obs.gap_y))
                    bottom_y = obs.gap_y + obs.gap_size
                    bottom_height = self.height - bottom_y
                    if bottom_height > 0:
                        pygame.draw.rect(self.screen, self.color_obstacle, (obs.x, bottom_y, obs.width, bottom_height))

            meteor_img = self.sprites.get('meteorite')
            for m in self.model.meteorites:
                if m.active:
                    if meteor_img:
                        self.screen.blit(meteor_img, (m.x, m.y))
                    else:
                        pygame.draw.rect(self.screen, self.color_meteorite, (m.x, m.y, m.width, m.height))

            bone_img = self.sprites.get('bone')
            for b in self.model.bones:
                if b.active:
                    if bone_img:
                        self.screen.blit(bone_img, (b.x, b.y))
                    else:
                        pygame.draw.rect(self.screen, self.color_bone, (b.x, b.y, b.width, b.height))

            buff = self.model.buff
            if buff.active:
                buff_img = self.sprites.get(buff.type)
                if buff_img:
                    self.screen.blit(buff_img, (buff.x, buff.y))
                else:
                    pygame.draw.rect(self.screen, self.buff_colors[buff.type],
                                     (buff.x, buff.y, buff.width, buff.height))

            p = self.model.player
            current_skin = getattr(self.model, 'current_skin', 'default')

            player_img = self.sprites.get(f'player_{current_skin}')
            if not player_img and current_skin == 'default':
                player_img = self.sprites.get('player')

            skin_colors = {"default": (255, 140, 0), "red_rocket": (255, 0, 0), "gold_rocket": (255, 215, 0),
                           "neon_rocket": (0, 255, 0)}
            current_color = skin_colors.get(current_skin, self.color_player)

            if p.state == "SHIELD":
                pygame.draw.rect(self.screen, self.buff_colors["SHIELD"],
                                 (p.x - 5, p.y - 5, p.width + 10, p.height + 10), 3)
            elif p.state == "MAGNET":
                pygame.draw.rect(self.screen, self.buff_colors["MAGNET"],
                                 (p.x - 5, p.y - 5, p.width + 10, p.height + 10), 3)
            elif p.state == "FUEL":
                pygame.draw.rect(self.screen, self.buff_colors["FUEL"], (p.x - 30, p.y + 5, 30, p.height - 10))

            if p.state == "DEAD" and not player_img:
                pygame.draw.rect(self.screen, (255, 0, 0), (p.x, p.y, p.width, p.height))
            else:
                if player_img:
                    scaled_player = pygame.transform.scale(player_img, (int(p.width), int(p.height)))
                    self.screen.blit(scaled_player, (p.x, p.y))
                else:
                    pygame.draw.rect(self.screen, current_color, (p.x, p.y, p.width, p.height))

            self.draw_text(f"Score: {int(self.model.score)}", self.font_small, (255, 255, 255), 10, 10)
            self.draw_text(f"Fish: {self.model.current_run_bones}", self.font_small, self.color_bone, 10, 40)

            if self.model.game_state == "GAME_OVER":
                self.draw_text("GAME OVER", self.font_large, (255, 0, 0), 400, 250, center=True)
                self.draw_text("Press SPACE to Restart", self.font_small, (255, 255, 255), 400, 320, center=True)
                self.draw_text("Press ESC for Menu", self.font_small, (255, 255, 255), 400, 360, center=True)

        pygame.display.flip()

    def render_menu(self):
        self.draw_text("ROCKET CAT", self.font_large, (255, 215, 0), 400, 150, center=True)
        self.draw_text(f"Total Fish: {self.model.total_bones}", self.font_small, self.color_bone, 400, 200, center=True)

        pygame.draw.rect(self.screen, (50, 50, 100), (300, 240, 200, 50))
        self.draw_text("PLAY", self.font_small, (255, 255, 255), 400, 265, center=True)

        pygame.draw.rect(self.screen, (50, 50, 100), (300, 310, 200, 50))
        self.draw_text("SHOP", self.font_small, (255, 255, 255), 400, 335, center=True)

        pygame.draw.rect(self.screen, (50, 50, 100), (300, 380, 200, 50))
        self.draw_text("SETTINGS", self.font_small, (255, 255, 255), 400, 405, center=True)

    def render_settings(self):
        self.draw_text("SETTINGS", self.font_large, (255, 255, 255), 400, 80, center=True)

        vol_pct = int(self.model.volume * 100)
        self.draw_text(f"VOLUME: {vol_pct}%", self.font_small, (255, 255, 255), 400, 220, center=True)

        pygame.draw.rect(self.screen, (100, 100, 100), (250, 260, 300, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (250, 260, int(300 * self.model.volume), 20))

        pygame.draw.rect(self.screen, (50, 50, 100), (190, 245, 40, 40))
        self.draw_text("-", self.font_small, (255, 255, 255), 210, 265, center=True)

        pygame.draw.rect(self.screen, (50, 50, 100), (570, 245, 40, 40))
        self.draw_text("+", self.font_small, (255, 255, 255), 590, 265, center=True)

        pygame.draw.rect(self.screen, (150, 50, 50), (300, 450, 200, 50))
        self.draw_text("BACK", self.font_small, (255, 255, 255), 400, 475, center=True)

    def render_shop(self):
        self.draw_text("SPACE SHOP", self.font_large, (255, 215, 0), 400, 80, center=True)
        self.draw_text(f"Your Fish: {self.model.total_bones}", self.font_small, (255, 255, 255), 400, 130, center=True)

        y_offset = 180
        skin_colors = {"default": (255, 140, 0), "red_rocket": (255, 0, 0), "gold_rocket": (255, 215, 0),
                       "neon_rocket": (0, 255, 0)}

        for skin, price in self.model.skins_catalog.items():
            pygame.draw.rect(self.screen, (30, 30, 60), (150, y_offset, 500, 50))
            pygame.draw.rect(self.screen, skin_colors[skin], (170, y_offset + 10, 30, 30))
            self.draw_text(skin.upper(), self.font_small, (255, 255, 255), 220, y_offset + 25, center=False)

            if self.model.current_skin == skin:
                btn_text, btn_color = "EQUIPPED", (100, 100, 100)
            elif skin in self.model.unlocked_skins:
                btn_text, btn_color = "EQUIP", (50, 100, 50)
            else:
                btn_text, btn_color = f"BUY: {price}", (100, 50, 150)

            pygame.draw.rect(self.screen, btn_color, (500, y_offset + 10, 130, 30))
            self.draw_text(btn_text, self.font_small, (255, 255, 255), 565, y_offset + 25, center=True)
            y_offset += 60

        pygame.draw.rect(self.screen, (150, 50, 50), (300, 500, 200, 50))
        self.draw_text("BACK", self.font_small, (255, 255, 255), 400, 525, center=True)
