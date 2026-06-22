import random
import json
import os


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 55
        self.height = 45
        self.velocity = 0.0
        self.gravity = 1200.0
        self.jump_strength = -450.0
        self.state = "NORMAL"
        self.buff_timer = 0.0

    def jump(self):
        if self.state != "DEAD":
            self.velocity = self.jump_strength

    def update(self, delta_time):
        if self.state == "DEAD":
            return

        self.velocity += self.gravity * delta_time
        self.y += self.velocity * delta_time

        if self.state in ["SHIELD", "MAGNET", "FUEL"]:
            self.buff_timer -= delta_time
            if self.buff_timer <= 0:
                self.state = "NORMAL"


class Bone:
    def __init__(self):
        self.x = -100
        self.y = -100
        self.width = 25
        self.height = 25
        self.active = False

    def update(self, delta_time, game_speed, player):
        if not self.active:
            return

        if player.state == "MAGNET":
            dx = player.x - self.x
            dy = player.y - self.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if 0 < dist < 500:
                self.x += (dx / dist) * 800 * delta_time
                self.y += (dy / dist) * 800 * delta_time
                return

        self.x -= game_speed * delta_time


class Buff:
    def __init__(self):
        self.x = -100
        self.y = -100
        self.width = 32
        self.height = 32
        self.active = False
        self.type = "SHIELD"

    def update(self, delta_time, game_speed):
        if self.active:
            self.x -= game_speed * delta_time


class ObstaclePair:
    def __init__(self, x, gap_y):
        self.x = x
        self.width = 60
        self.gap_y = gap_y
        self.gap_size = 190

    def update(self, delta_time, game_speed):
        self.x -= game_speed * delta_time


class Meteorite:
    def __init__(self):
        self.x = -100
        self.y = -100
        self.width = 80
        self.height = 40
        self.active = False
        self.speed_multiplier = 2.0

    def update(self, delta_time, game_speed):
        if self.active:
            self.x -= (game_speed * self.speed_multiplier) * delta_time


class GameModel:
    def __init__(self):
        self.is_running = True
        self.game_state = "MENU"
        self.volume = 0.5
        self.base_speed = 200.0
        self.sounds_to_play = []

        self.score = 0.0
        self.high_score = 0
        self.total_bones = 0
        self.current_run_bones = 0

        self.markov_matrix = {0: [0.4, 0.5, 0.1], 1: [0.2, 0.6, 0.2], 2: [0.1, 0.5, 0.4]}
        self.state_heights = {0: 100, 1: 225, 2: 350}

        self.bones = [Bone() for _ in range(10)]
        self.buff = Buff()
        self.meteorites = [Meteorite() for _ in range(2)]

        self.load_progress()
        self.reset_game()

    def load_progress(self):
        if os.path.exists("save.json"):
            try:
                with open("save.json", "r") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
                    self.total_bones = data.get("total_bones", 0)
            except:
                pass

    def save_progress(self):
        with open("save.json", "w") as f:
            json.dump({"high_score": self.high_score, "total_bones": self.total_bones}, f)

    def get_next_markov_gap(self):
        probs = self.markov_matrix[self.current_markov_state]
        r, cum = random.random(), 0.0
        for i, p in enumerate(probs):
            cum += p
            if r <= cum:
                self.current_markov_state = i
                break
        return self.state_heights[self.current_markov_state] + random.randint(-30, 30)

    def reset_game(self):
        self.player = Player(100, 300)
        self.score = 0.0
        self.current_run_bones = 0
        self.current_markov_state = 1

        for b in self.bones: b.active = False
        self.buff.active = False
        for m in self.meteorites: m.active = False

        self.obstacles = []
        for i in range(4):
            obs = ObstaclePair(800 + i * 350, self.get_next_markov_gap())
            self.obstacles.append(obs)

            for b in self.bones:
                if not b.active:
                    b.x = obs.x + 20
                    b.y = obs.gap_y + 65
                    b.active = True
                    break

    def update(self, delta_time):
        if self.game_state != "PLAYING":
            return

        current_speed = self.base_speed * 3 if self.player.state == "FUEL" else self.base_speed
        self.score += (current_speed / 20) * delta_time
        self.player.update(delta_time)

        for obs in self.obstacles:
            obs.update(delta_time, current_speed)
            if obs.x < -obs.width:
                obs.x = max([o.x for o in self.obstacles]) + 350
                obs.gap_y = self.get_next_markov_gap()

                if not self.buff.active and random.random() < 0.15:
                    self.buff.x = obs.x + 15
                    self.buff.y = obs.gap_y + 60
                    self.buff.type = random.choice(["SHIELD", "MAGNET", "FUEL"])
                    self.buff.active = True
                else:
                    spawned = 0
                    target = random.choice([1, 2])
                    for b in self.bones:
                        if not b.active:
                            b.x = obs.x + 5 + (spawned * 30)
                            b.y = obs.gap_y + 65
                            b.active = True
                            spawned += 1
                            if spawned >= target: break

                for m in self.meteorites:
                    if not m.active and random.random() < 0.20:
                        m.x = 1000 + random.randint(0, 500)
                        m.y = random.randint(50, 550)
                        m.speed_multiplier = random.uniform(1.5, 2.5)
                        m.active = True
                        break

        for b in self.bones:
            b.update(delta_time, current_speed, self.player)
            if b.x < -50: b.active = False

        self.buff.update(delta_time, current_speed)
        if self.buff.x < -50: self.buff.active = False

        for m in self.meteorites:
            m.update(delta_time, current_speed)
            if m.x < -100: m.active = False

        self.check_collisions()

        if self.player.y > 600 - self.player.height:
            self.trigger_game_over()
        if self.player.y < 0:
            self.player.y, self.player.velocity = 0, 0

    def trigger_game_over(self):
        self.sounds_to_play.append('crash')
        self.player.state = "DEAD"
        self.game_state = "GAME_OVER"
        self.total_bones += self.current_run_bones
        if int(self.score) > self.high_score:
            self.high_score = int(self.score)
        self.save_progress()

    def check_collisions(self):
        px, py, pw, ph = self.player.x, self.player.y, self.player.width, self.player.height

        for b in self.bones:
            if b.active and (px < b.x + b.width and px + pw > b.x and py < b.y + b.height and py + ph > b.y):
                b.active = False
                self.current_run_bones += 1
                self.sounds_to_play.append('fish')

        if self.buff.active:
            bx, by, bw, bh = self.buff.x, self.buff.y, self.buff.width, self.buff.height
            if (px < bx + bw and px + pw > bx and py < by + bh and py + ph > by):
                self.player.state = self.buff.type
                self.player.buff_timer = 5.0
                self.buff.active = False
                self.sounds_to_play.append('buff')

        for m in self.meteorites:
            if m.active:
                if (px < m.x + m.width and px + pw > m.x and py < m.y + m.height and py + ph > m.y):
                    if self.player.state == "FUEL":
                        m.active = False
                    elif self.player.state == "SHIELD":
                        pass
                    else:
                        self.trigger_game_over()

        for obs in self.obstacles:
            top_rect = (obs.x, 0, obs.width, obs.gap_y)
            bottom_rect = (obs.x, obs.gap_y + obs.gap_size, obs.width, 600 - (obs.gap_y + obs.gap_size))

            collision = False
            if (px < top_rect[0] + top_rect[2] and px + pw > top_rect[0] and py < top_rect[1] + top_rect[
                3] and py + ph > top_rect[1]):
                collision = True
            if (px < bottom_rect[0] + bottom_rect[2] and px + pw > bottom_rect[0] and py < bottom_rect[1] + bottom_rect[
                3] and py + ph > bottom_rect[1]):
                collision = True

            if collision:
                if self.player.state == "FUEL":
                    obs.x = -100
                elif self.player.state == "SHIELD":
                    pass
                else:
                    self.trigger_game_over()
