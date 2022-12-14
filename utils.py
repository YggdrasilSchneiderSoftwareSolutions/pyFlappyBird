import pygame
import settings
import os

GAME_FOLDER = os.path.dirname(__file__)

SOUNDS = {}


def load_image(filename, color_key=None):
    # Pygame das Bild laden lassen.
    image = pygame.image.load(filename)

    # Das Pixelformat der Surface an den Bildschirm (genauer: die screen-Surface) anpassen.
    # Dabei die passende Funktion verwenden, je nach dem, ob wir ein Bild mit Alpha-Kanal haben oder nicht.
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()

    # Colorkey des Bildes setzen, falls nicht None.
    # Bei -1 den Pixel im Bild an Position (0, 0) als Colorkey verwenden.
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key, pygame.RLEACCEL)

    return image


def get_image_for_frames(num_frames, images_list):
    # Schauen, wie oft die Bildersequenz in die FPS passt (+1 wegen Array): FPS/nBilder + 1
    # Ermittlen, welches Bild zum aktuellen Frame passt: nFrames / Bilder pro FPS
    image_index = num_frames / (settings.FPS / (len(images_list) + 1))
    return images_list[int(image_index - 1)]  # -1 wegen Arrayindex


def init_sounds():
    global SOUNDS
    global GAME_FOLDER
    SOUNDS['intro_title'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'intro_title.wav'))
    SOUNDS['bird'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'bird.wav'))
    SOUNDS['game_over'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'game_over.wav'))
    SOUNDS['new_game'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'new_game.wav'))
    SOUNDS['new_highscore'] = pygame.mixer.Sound(os.path.join(GAME_FOLDER, 'sounds', 'new_highscore.wav'))


def play_sound(name):
    global SOUNDS
    sound = SOUNDS[name]
    if sound is not None:
        sound.play()
