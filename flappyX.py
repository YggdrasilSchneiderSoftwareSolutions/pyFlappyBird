from sprites import *
import random
import json
import datetime
import locale
from yggdrasil_intro import *


class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()

        init_sounds()

        # Umstellung auf Deutsch:
        locale.setlocale(locale.LC_ALL, 'de_DE')

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # TODO: Evtl. Fullscreen?
        #self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption(TITLE)
        # Tasten nur 1x annehmen bei Gedrückthalten
        pygame.key.set_repeat(False)
        pygame.mouse.set_visible(False)
        # Fenster zentrieren
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.clock = pygame.time.Clock()

        # Hintergrund auf das gesamte Fenster vergrößern
        self.background_images = [pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles',
                                                                                 'Background1.png')), (WIDTH, HEIGHT)),
                                  pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles',
                                                                                 'Background2.png')), (WIDTH, HEIGHT)),
                                  pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles',
                                                                                 'Background3.png')), (WIDTH, HEIGHT)),
                                  pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles',
                                                                                 'Background4.png')), (WIDTH, HEIGHT)),
                                  pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles',
                                                                                 'Background5.png')), (WIDTH, HEIGHT))]
        self.image = None

        self.playing = False
        self.running = True

        self.walls = None
        self.player = None

        self.new_highscore = False
        self.saved_highscore = False
        self.save_file = None
        with open("save.json", encoding="utf-8") as f:
            self.save_file = json.load(f)

        self.wallSections = [0, 0, 0, 0]
        self.wallSectionWidth = WIDTH / len(self.wallSections)
        self.levelPosition = 0
        self.wall_space = 0
        self.wall_speed = 0
        self.levels = {0: {"space": 180, "speed": 2, "is_set": False},
                       50: {"space": 180, "speed": 3, "is_set": False},
                       100: {"space": 150, "speed": 3, "is_set": False},
                       250: {"space": 100, "speed": 3, "is_set": False},
                       350: {"space": 80, "speed": 3, "is_set": False},
                       450: {"space": 80, "speed": 4, "is_set": False},
                       550: {"space": 80, "speed": 5, "is_set": False}}

        self.font_score = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 34)
        self.img_score = self.font_score.render('Punkte: ', True, WHITE)
        self.font_highscore = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 34)
        self.img_highscore = self.font_score.render('Highscore: ', True, WHITE)
        self.font_game_over = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 144)
        self.img_game_over = self.font_game_over.render('Game Over', True, RED)
        self.font_main = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 24)
        self.img_continue_white = self.font_main.render('Enter - Neues Spiel ', True, WHITE)
        self.img_continue_black = self.font_main.render('Enter - Neues Spiel ', True, BLACK)
        self.img_quit_white = self.font_main.render('Esc - Hauptmenü ', True, WHITE)
        self.img_quit_black = self.font_main.render('Esc - Hauptmenü ', True, BLACK)
        self.button_color_counter = 0
        self.button_color_interval = FPS

    def new(self):
        # Zufälliger Hintergrund
        random_bg_index = random.randint(0, len(self.background_images) - 1)
        self.image = self.background_images[random_bg_index]

        self.new_highscore = False
        self.saved_highscore = False

        pygame.mixer.music.load(os.path.join(GAME_FOLDER, 'music', 'main_theme.mp3'))
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(.5)
        # start a new game
        # Für weitere Spiele, müssen alle Entities hier neu initialisiert werden
        self.walls = pygame.sprite.Group()
        self.player = Player(WIDTH // 3, HEIGHT // 3, self)

        for level in self.levels.values():
            level["is_set"] = False

        self.wall_space = self.levels[0]["space"]
        self.wall_speed = self.levels[0]["speed"]

        self.button_color_counter = -self.button_color_interval

        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

        pygame.mixer.music.fadeout(1000)

    def update(self):
        if self.player.game_over:
            # Neue Highscore übernehmen
            if self.new_highscore and not self.saved_highscore:
                with open("save.json", "w", encoding="utf-8") as f:
                    self.save_file["score"] = self.player.score
                    self.save_file["date"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    json.dump(self.save_file, f, ensure_ascii=False)
                    self.saved_highscore = True
            return

        if self.player.score > self.save_file["score"] and not self.new_highscore:
            self.new_highscore = True
            play_sound("new_highscore")

        # Game Loop - Update
        self.levelPosition += self.wall_speed
        if self.levelPosition > self.wallSectionWidth:
            random_wall_size = random.randint(0, HEIGHT // 2)
            self.wallSections.pop(0)
            self.wallSections.append(random_wall_size)
            self.levelPosition -= self.wallSectionWidth

            if random_wall_size >= 100:
                bottom_height = random_wall_size + self.wall_space
                top_height = random_wall_size - self.wall_space
                wall_bottom = WallBottom(WIDTH, bottom_height, self)
                self.walls.add(wall_bottom)
                wall_top = WallTop(WIDTH, top_height if top_height >= 0 else 0, self)  # sonst evtl. negative Werte
                self.walls.add(wall_top)

        self.walls.update()
        self.player.update()

        # Level setzen
        try:
            level_check = self.levels[self.player.score]
            if level_check["is_set"] is False:
                self.wall_space = level_check["space"]
                self.wall_speed = level_check["speed"]
                level_check["is_set"] = True
        except KeyError:  # kein neues Level nötig oder zu setzendes Element nicht im Level definiert
            # TODO Am Ende nur noch schneller werden
            pass

    def events(self):
        # Events for keyup and keydown
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                if event.key == pygame.K_RETURN:
                    if self.player.game_over:
                        self.new()
                if event.key == pygame.K_ESCAPE:
                    if self.player.game_over:
                        self.playing = False

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)
        self.screen.blit(self.image, (0, 0))

        for wall in self.walls:  # TODO Refacoring
            # Kopfstück setzen
            if type(wall) == WallBottom:
                self.screen.blit(wall.head_tile, (wall.x, wall.y))
                wall_length = wall.y
                while wall_length < HEIGHT:
                    wall_length += TILESIZE
                    self.screen.blit(wall.body_tile, (wall.x, wall_length))
            else:
                self.screen.blit(pygame.transform.rotate(wall.head_tile, 180), wall.rect.bottomleft)
                wall_length = wall.rect.bottomleft[1]  # y-Wert
                while wall_length > 0:
                    wall_length -= TILESIZE
                    self.screen.blit(wall.body_tile, (wall.x, wall_length))

        # Anzeigen
        self.img_score = self.font_score.render('Punkte: ' + str(self.player.score), True, WHITE)
        self.screen.blit(self.img_score, (35, 35))
        self.img_score = self.font_score.render('Highscore: ' + str(self.save_file["score"]), True, WHITE)
        self.screen.blit(self.img_score, (300, 35))

        # Player am Schluss, damit im Vordergrund
        self.screen.blit(self.player.image, self.player.rect)
        # after drawing everything, flip the display
        if self.player.game_over:
            self.screen.blit(self.img_game_over, (100, 200))

            # Buttons
            self.button_color_counter += 1
            if self.button_color_counter <= 0:
                self.screen.blit(self.img_continue_black, (250, 400))
                self.screen.blit(self.img_quit_black, (250, 450))
            else:
                self.screen.blit(self.img_continue_white, (250, 400))
                self.screen.blit(self.img_quit_white, (250, 450))
                if self.button_color_counter >= self.button_color_interval:
                    self.button_color_counter = -self.button_color_interval

        pygame.display.flip()

    def main_menu(self):
        bird_list = [pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird0.png')), (128, 128)),
                     pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird1.png')), (128, 128)),
                     pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird2.png')), (128, 128)),
                     pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird3.png')), (128, 128))]
        num_frames = 0

        font_title = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 110)
        font_title.set_italic(True)
        font_title.set_underline(True)
        img_title = font_title.render('FlappyX', True, RED)

        font_highscore_title = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 45)
        font_highscore_title.set_underline(1)
        img_highscore_title = font_highscore_title.render('Highscore', True, WHITE)
        font_highscore_actual = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 32)
        img_highscore_actual = font_highscore_actual.render(str(self.save_file["score"]) + " am "
                                                            + datetime.datetime.strptime(self.save_file["date"],
                                                                                         '%d.%m.%Y %H:%M:%S')
                                                            .strftime("%d.%m.%Y %H:%M:%S"),
                                                            True, WHITE)

        selected = {'Start': True, 'Quit': False}

        self.running = True
        play_sound('bird')
        while self.running:
            self.clock.tick(FPS)

            if selected['Start'] is True:
                font_start = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 92)
                img_start = font_start.render('Start!', True, WHITE)
                font_quit = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 72)
                img_quit = font_quit.render('Ende', True, WHITE)
            else:
                font_start = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 72)
                img_start = font_start.render('Start', True, WHITE)
                font_quit = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 92)
                img_quit = font_quit.render('Ende', True, WHITE)

            # Events im Menü
            for event in pygame.event.get():
                # check for closing window
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected['Start'] = True
                        selected['Quit'] = False
                        play_sound('bird')
                    if event.key == pygame.K_DOWN:
                        selected['Start'] = False
                        selected['Quit'] = True
                        play_sound('bird')
                    if event.key == pygame.K_RETURN:
                        if selected['Start'] is True:
                            self.new()
                            # nach dem Spiel Highscore neu setzen
                            img_highscore_actual = font_highscore_actual.render(str(self.save_file["score"]) + " am "
                                                                                + datetime.datetime.strptime(
                                                                                self.save_file["date"],
                                                                                '%d.%m.%Y %H:%M:%S').strftime(
                                "%d.%m.%Y %H:%M:%S"), True, WHITE)
                        else:
                            self.running = False

            self.screen.fill(BLACK)

            num_frames += 1
            if num_frames == FPS:
                num_frames = 0
            self.screen.blit(get_image_for_frames(num_frames, bird_list), (100, 100))
            self.screen.blit(img_title, (300, 100))

            self.screen.blit(img_start, (250, 300))
            self.screen.blit(img_quit, (400, 400))

            self.screen.blit(img_highscore_title, (350, 550))
            self.screen.blit(img_highscore_actual, (300, 600))

            pygame.display.flip()


if __name__ == "__main__":
    g = Game()
    intro = YggdrasilIntro(g)
    intro.load_intro()
    while g.running:
        g.main_menu()

    pygame.quit()
    exit(0)
