from settings import *
from utils import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.tiles = [pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird0.png')), (48, 48)),
                      pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird1.png')), (48, 48)),
                      pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird2.png')), (48, 48)),
                      pygame.transform.scale(load_image(os.path.join(GAME_FOLDER, 'tiles', 'bird3.png')), (48, 48))]
        self.image = self.tiles[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0
        self.score = 0
        self.game_over = False
        self.num_frames = 0
        self.greeting_player = True

    def get_image(self):
        self.num_frames += 1
        if self.num_frames == FPS:
            self.num_frames = 0

        return get_image_for_frames(self.num_frames, self.tiles)

    def jump(self):
        # nur wenn schon wieder in Abwährtsbewegung
        if self.gravity > 0:
            self.gravity = -PLAYER_JUMP

    def update(self):
        if self.greeting_player:
            play_sound('new_game')
            self.greeting_player = False

        # physics stuff
        self.gravity += PLAYER_GRAV
        if self.gravity > MAX_GRAVITY:
            self.gravity = MAX_GRAVITY

        self.rect.y += self.gravity

        hit = pygame.sprite.spritecollide(self, self.game.walls, False)
        if hit or self.rect.y > HEIGHT:
            self.game_over = True
            play_sound('game_over')
        else:
            for wall in self.game.walls:
                if wall.passed is False and wall.rect.x < self.rect.x - TILESIZE:
                    self.score += WALL_SCORE
                    wall.passed = True

        self.image = self.get_image()


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.game = game
        self.passed = False
        self.body_tile = load_image(os.path.join(GAME_FOLDER, 'tiles', 'wall_body.png'))
        self.head_tile = load_image(os.path.join(GAME_FOLDER, 'tiles', 'wall_head.png'))

    def update(self):
        self.rect.x -= self.game.wall_speed
        self.x = self.rect.x
        self.y = self.rect.y
        if self.rect.x < 0 - TILESIZE:
            self.kill()

    def set_rect(self):
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class WallTop(Wall):
    def __init__(self, x, y, game):
        Wall.__init__(self, x, 0, game)
        self.image = pygame.Surface((TILESIZE, y))
        self.set_rect()


class WallBottom(Wall):
    def __init__(self, x, y, game):
        Wall.__init__(self, x, y, game)
        self.image = pygame.Surface((TILESIZE, HEIGHT - y))
        self.set_rect()

