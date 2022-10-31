from settings import *
from utils import *


class YggdrasilIntro:
    def __init__(self, game):
        self.game = game
        self.finished = False
        self.load_time = FPS * 3  # ca 3 Sekunden

    def load_intro(self):
        font_title = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 110)
        font_title.set_italic(True)
        font_title.set_underline(True)
        img_yggdrasil = font_title.render('YGGDRASIL', True, GRAY)
        img_gaming = font_title.render('GAMING', True, GRAY)
        font_presents = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 54)
        img_presents = font_presents.render('presents', True, WHITE)
        font_copyright = pygame.font.Font(os.path.join(GAME_FOLDER, 'font', 'font.ttf'), 18)
        img_copyright = font_copyright.render('(c) Yggdrasil Gaming 2021', True, WHITE)

        num_frames = 0
        y_yggdrasil = -500
        y_gaming = -350
        yggdrasil_set = False
        gaming_set = False
        title_set = False
        play_title_sound = True

        while not self.finished:
            if title_set:
                if play_title_sound:
                    play_sound('intro_title')
                    play_title_sound = False

                num_frames += 1
                if num_frames == self.load_time:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            if y_yggdrasil != 100:
                y_yggdrasil += 10
            else:
                yggdrasil_set = True
            if y_gaming != 250:
                y_gaming += 10
            else:
                gaming_set = True

            title_set = yggdrasil_set and gaming_set

            self.game.clock.tick(FPS)

            for event in pygame.event.get():
                # check for closing window
                if event.type == pygame.QUIT:
                    self.finished = True

            self.game.screen.fill(BLACK)

            self.game.screen.blit(img_yggdrasil, (200, y_yggdrasil))
            self.game.screen.blit(img_gaming, (300, y_gaming))
            if title_set:
                self.game.screen.blit(img_presents, (370, 450))
                self.game.screen.blit(img_copyright, (100, 700))

            pygame.display.flip()
