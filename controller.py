import pygame


class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.prev_state = self.model.game_state

    def run(self):
        while self.model.is_running:
            delta_time = self.clock.tick(self.fps) / 1000.0
            self.handle_events()
            self.model.update(delta_time)

            # --- ЗВУКИ И МУЗЫКА ---
            if self.prev_state != self.model.game_state:
                if self.model.game_state == "PLAYING":
                    self.view.play_music()
                elif self.model.game_state == "GAME_OVER":
                    self.view.stop_music()
                self.prev_state = self.model.game_state

            for sound in self.model.sounds_to_play:
                self.view.play_sound(sound)
            self.model.sounds_to_play.clear()
            # ----------------------

            self.view.render()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.model.is_running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.process_action()

                elif event.key == pygame.K_ESCAPE:
                    if self.model.game_state == "GAME_OVER":
                        self.model.reset_game()
                        self.model.game_state = "MENU"
                    elif self.model.game_state == "SETTINGS":
                        self.model.game_state = "MENU"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()

                    if self.model.game_state == "MENU":
                        if 300 <= mx <= 500 and 250 <= my <= 300:
                            self.model.game_state = "PLAYING"
                        elif 300 <= mx <= 500 and 330 <= my <= 380:
                            self.model.game_state = "SETTINGS"

                    elif self.model.game_state == "SETTINGS":
                        # Клик по кнопке "-"
                        if 190 <= mx <= 230 and 245 <= my <= 285:
                            self.model.volume = max(0.0, self.model.volume - 0.1)
                            self.view.update_volume()  # Применяем громкость к музыке
                            self.view.play_sound('jump')  # Пикаем для проверки громкости

                        # Клик по кнопке "+"
                        elif 570 <= mx <= 610 and 245 <= my <= 285:
                            self.model.volume = min(1.0, self.model.volume + 0.1)
                            self.view.update_volume()
                            self.view.play_sound('jump')

                        elif 300 <= mx <= 500 and 450 <= my <= 500:
                            self.model.game_state = "MENU"

                    elif self.model.game_state in ["PLAYING", "GAME_OVER"]:
                        self.process_action()

    def process_action(self):
        if self.model.game_state == "MENU":
            self.model.game_state = "PLAYING"
        elif self.model.game_state == "PLAYING":
            self.model.player.jump()
            self.view.play_sound('jump')  # Звук прыжка при нажатии
        elif self.model.game_state == "GAME_OVER":
            self.model.reset_game()
            self.model.game_state = "MENU"
