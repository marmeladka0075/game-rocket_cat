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

            if self.prev_state != self.model.game_state:
                if self.model.game_state == "PLAYING":
                    self.view.play_music()
                elif self.model.game_state == "GAME_OVER":
                    self.view.stop_music()
                self.prev_state = self.model.game_state

            for sound in self.model.sounds_to_play:
                self.view.play_sound(sound)
            self.model.sounds_to_play.clear()

            self.view.render()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.model.is_running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.process_action()

                elif event.key == pygame.K_ESCAPE and self.model.game_state == "GAME_OVER":
                    self.model.reset_game()
                    self.model.game_state = "MENU"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.process_action()

    def process_action(self):
        if self.model.game_state == "MENU":
            self.model.game_state = "PLAYING"
        elif self.model.game_state == "PLAYING":
            self.model.player.jump()
            self.view.play_sound('jump')
        elif self.model.game_state == "GAME_OVER":
            self.model.reset_game()
            self.model.game_state = "PLAYING"
