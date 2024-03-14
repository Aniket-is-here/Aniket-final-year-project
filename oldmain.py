import pygame
import sys
from pygame import mixer

from Classes.button import Button
from Classes.fighter_class import Fighter
from Classes.gameStateManager import GameStateManager

mixer.init()
pygame.init()

# Constants
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# FONTS
default_font = pygame.font.Font("assets/font/font.ttf", 25)
medium_font = pygame.font.Font("assets/font/font.ttf", 40)
large_font = pygame.font.Font("assets/font/font.ttf", 60)

# loading music
pygame.mixer.music.load("assets/audio/Arena Sound.mpeg")
# pygame.mixer.music.play(-1, 13.0, 5000)
player_attack_sound = pygame.mixer.Sound("assets/audio/sword.wav")
enemy_attack_sound = pygame.mixer.Sound("assets/audio/magic.wav")

# declaration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
intro_count = 3

# images
menu_bg = pygame.image.load("assets/images/background/menu_bg.png").convert_alpha()
victory_image = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
ground_image = pygame.image.load("assets/images/background/ground.png").convert_alpha()
ground_width = ground_image.get_width()
ground_height = ground_image.get_height()

# loading bg images
gamebg_list = []

for i in range(1, 6):
    gamebg_image = pygame.image.load(f"assets/images/background/plx-{i}.png").convert_alpha()
    gamebg_list.append(gamebg_image)
gamebg_width = gamebg_list[0].get_width()
scroll = 0


# drawing bg
def display_gamebg():
    global scroll

    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        if not scroll <= 0 and intro_count <= 0:
            scroll -= 5
    elif key[pygame.K_d]:
        if not scroll >= 600 and intro_count <= 0:
            scroll += 5
    for x in range(0, 5):
        speed = 1
        for a in gamebg_list:
            transformed_bg = pygame.transform.scale(a, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(transformed_bg, ((x * gamebg_width) - scroll * speed, 0))
            speed += 0.2
    for x in range(15):
        transformed_bg = pygame.transform.scale(ground_image, (SCREEN_WIDTH, 120))
        screen.blit(transformed_bg, ((x * ground_width ) - scroll * 2.5, SCREEN_HEIGHT - ground_height - 50))
        # screen.blit(transformed_bg, (0, 600))


pygame.display.set_caption("Menu")
clock = pygame.time.Clock()
FPS = 60

# character info
player_size = 162
player_scale = 4
player_offset = [72, 53]
player_info = [player_size, player_scale, player_offset]

enemy_size = 250
enemy_scale = 3
enemy_offset = [110, 105]
enemy_info = [enemy_size, enemy_scale, enemy_offset]

# spreadsheets
player_sheet = pygame.image.load("assets/images/Sprites/player/player.png").convert_alpha()
player_animation_steps = [10, 8, 1, 7, 7, 3, 7]

enemy_sheet = pygame.image.load("assets/images/Sprites/enemy/enemy.png").convert_alpha()
enemy_animation_steps = [8, 8, 1, 8, 8, 3, 7]


# functions
def display_bg(image):
    transformed_bg = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(transformed_bg, (0, 0))


def display_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))


def controls():
    while True:
        pygame.display.set_caption("Controls")
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        display_bg(menu_bg)
        playinginfo = default_font.render("Player 1 :", True, "black")
        screen.blit(playinginfo, (220, 40))
        playing_control = default_font.render("Move  = A,W,S,D", True, "black")
        screen.blit(playing_control, (220, 80))
        attack1_control = default_font.render("Attack1 = Q", True, "black")
        screen.blit(attack1_control, (220, 120))
        attack2_control = default_font.render("Attack2 = E", True, "black")
        screen.blit(attack2_control, (220, 160))
        playing2info = default_font.render("Player 2 :", True, "black")
        screen.blit(playing2info, (740, 40))
        playing_control2 = default_font.render("Move  = Arrow Keys", True, "black")
        screen.blit(playing_control2, (740, 80))
        attack1_control2 = default_font.render("Attack1 = 1", True, "black")
        screen.blit(attack1_control2, (740, 120))
        attack2_control2 = default_font.render("Attack2 = 2", True, "black")
        screen.blit(attack2_control2, (740, 160))
        BACK_BUTTON = Button(image=pygame.image.load("assets/images/icons/Play Rect.png"), pos=(1200, 20),
                             text_input="BACK", font=default_font, base_color="#d7fcd4", hovering_color="White")
        for button in [BACK_BUTTON]:
            button.changeColor(PLAY_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
        # updating fighters
        pygame.display.update()


round_over_time = None


def singleplayer():
    global round_over_time, intro_count
    won = False
    player = Fighter(1, 200, 420, False, player_info, player_sheet, player_animation_steps, player_attack_sound)
    enemy = Fighter(3, 1000, 420, True, enemy_info, enemy_sheet, enemy_animation_steps, enemy_attack_sound)
    # defining arena stats
    last_count_update = pygame.time.get_ticks()
    level = 1
    round_over = False
    ROUND_OVER_COOLDOWN = 2000

    run = True
    pygame.display.set_caption("Fighting Arena")
    while run:
        clock.tick(FPS)
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        # drawing background
        display_bg(menu_bg)

        # show stats
        display_health_bar(player.health, 50, 40)
        display_health_bar(enemy.health, 830, 40)
        MENU_TEXT = default_font.render(f"Level : {level}", True, "#b68f40")
        screen.blit(MENU_TEXT, (15, 8))

        # intro scene
        if intro_count <= 0:
            # fighter movements
            player.move(target=enemy, round_over=round_over)
            enemy.move(target=player, round_over=round_over)
        else:
            # display count timer
            countdown_text = medium_font.render(str(intro_count), True, RED)
            screen.blit(countdown_text, ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 3)))
            # update count time
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()
        # update fighters animation
        player.update()
        enemy.update()
        # displaying fighters
        player.draw(screen)
        enemy.draw(screen)

        # displaying quit button
        BACK_BUTTON = Button(image=pygame.image.load("assets/images/icons/Play Rect.png"), pos=(1200, 20),
                             text_input="BACK", font=default_font, base_color="#d7fcd4", hovering_color="White")

        if not round_over:
            if not player.alive:
                won = False
                round_over = True
                round_over_time = pygame.time.get_ticks()

            elif not enemy.alive:
                won = True
                level += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else:
            if won:
                screen.blit(victory_image, (500, 50))
            else:
                defeat_text = default_font.render("You Lose !", True, RED)
                screen.blit(defeat_text, (500, 50))

            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False

                intro_count = 3
                player = Fighter(1, 200, 420, False, player_info, player_sheet, player_animation_steps,
                                 player_attack_sound)
                enemy = Fighter(3, 1000, 420, True, enemy_info, enemy_sheet, enemy_animation_steps, enemy_attack_sound)
        for button in [BACK_BUTTON]:
            # button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        # updating fighters
        pygame.display.update()


def multiplayer():
    global round_over_time, intro_count
    player1 = Fighter(1, 200, 420, False, player_info, player_sheet, player_animation_steps, player_attack_sound)
    player2 = Fighter(2, 1000, 420, True, player_info, player_sheet, player_animation_steps, player_attack_sound)
    winner = None

    # defining arena stats
    last_count_update = pygame.time.get_ticks()
    player1score = 0
    player2score = 0
    round_over = False
    ROUND_OVER_COOLDOWN = 2000

    run = True
    pygame.display.set_caption("Menu")
    while run:
        clock.tick(FPS)
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        # drawing background
        display_gamebg()

        # show stats
        display_health_bar(player1.health, 50, 40)
        display_health_bar(player2.health, 830, 40)
        player1_score = default_font.render(f"P1-Score : {player1score}", True, "#b68f40")
        player2_score = default_font.render(f"P2-Score : {player2score}", True, "#b68f40")
        screen.blit(player1_score, (15, 8))
        screen.blit(player2_score, (800, 8))

        # intro scene
        if intro_count <= 0:
            # fighter movements
            player1.move(target=player2, round_over=round_over)
            player2.move(target=player1, round_over=round_over)
        else:
            # display count timer
            countdown_text = medium_font.render(str(intro_count), True, RED)
            screen.blit(countdown_text, ((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 3)))
            # update count time
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()
        # update fighters animation
        player1.update()
        player2.update()
        # displaying fighters
        player1.draw(screen)
        player2.draw(screen)

        # displaying quit button
        BACK_BUTTON = Button(image=pygame.image.load("assets/images/icons/Play Rect.png"), pos=(1200, 20),
                             text_input="BACK", font=default_font, base_color="#d7fcd4", hovering_color="White")

        if not round_over:
            if not player1.alive:
                round_over = True
                winner = "player_2"
                round_over_time = pygame.time.get_ticks()
            elif not player2.alive:
                round_over = True
                winner = "player_1"
                round_over_time = pygame.time.get_ticks()
        else:
            screen.blit(victory_image, (500, 50))

            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 3
                if winner == "player_1":
                    player1score += 1
                elif winner == "player_2":
                    player2score += 1
                player1 = Fighter(1, 200, 420, False, player_info, player_sheet, player_animation_steps,
                                  player_attack_sound)
                player2 = Fighter(2, 1000, 420, True, player_info, player_sheet, player_animation_steps,
                                  player_attack_sound)
        for button in [BACK_BUTTON]:
            # button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
        # updating fighters
        pygame.display.update()


def main_menu():
    while True:
        display_bg(menu_bg)

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = medium_font.render("Samurai's Adventure", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 150))

        singlePlayer_option = Button(image=pygame.image.load("assets/images/icons/Play Rect.png"), pos=(1040, 250),
                                     text_input="Single Player", font=default_font, base_color="#d7fcd4",
                                     hovering_color="White")
        multiPlayer_option = Button(image=pygame.image.load("assets/images/icons/Play Rect.png"), pos=(1040, 300),
                                    text_input="Multi Player", font=default_font, base_color="#d7fcd4",
                                    hovering_color="White")
        control_option = Button(image=pygame.image.load("assets/images/icons/Play Rect.png"), pos=(1040, 350),
                                text_input="Controls", font=default_font, base_color="#d7fcd4",
                                hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/images/icons/Quit Rect.png"), pos=(1200, 40),
                             text_input="QUIT", font=default_font, base_color="#d7fcd4", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [singlePlayer_option, multiPlayer_option, control_option, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if singlePlayer_option.checkForInput(MENU_MOUSE_POS):
                    singleplayer()
                if multiPlayer_option.checkForInput(MENU_MOUSE_POS):
                    multiplayer()
                if control_option.checkForInput(MENU_MOUSE_POS):
                    controls()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


main_menu()
