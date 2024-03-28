import pygame, random
from pygame import mixer

pygame.init()
mixer.init()

# defaults
player_size = 162
player_scale = 4
player_offset = [72, 53]
screen = pygame.display.set_mode((10, 50))
player_info = [player_size, player_scale, player_offset]

try:
    player_sheet = pygame.image.load("assets/images/Sprites/player/player.png").convert_alpha()
    player_attack_sound = pygame.mixer.Sound("assets/audio/sword.wav")
except FileNotFoundError:
    player_sheet = pygame.image.load("../assets/images/Sprites/player/player.png").convert_alpha()
    player_attack_sound = pygame.mixer.Sound("../assets/audio/sword.wav")

player_animation_steps = [10, 8, 1, 7, 7, 3, 7]


class MultiplayerFighter:
    def __init__(self, player, x, y, flip):
        self.player = player
        self.x = x
        self.y = y
        self.size = player_info[0]
        self.image_scale = player_info[1]
        self.offset = player_info[2]
        self.flip = flip
        # self.animation_list = self.load_images(player_sheet, player_animation_steps)
        self.action = 0  # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        # self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        # self.attack_sound = player_attack_sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        # extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(
                    pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, target, round_over):

        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # get keypress
        key = pygame.key.get_pressed()

        # can only perform other actions if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False:
            # check player 1 controls
            if self.player == 1:
                # movement
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                # jump
                if key[pygame.K_SPACE] and not self.jump:
                    self.vel_y = -35
                    self.jump = True
                # attack
                if key[pygame.K_q] or key[pygame.K_e]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_q]:
                        self.attack_type = 1
                    if key[pygame.K_e]:
                        self.attack_type = 2

            # check player 2 controls
            if self.player == 2:
                # movement
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                # jump
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                # attack
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2
            if self.player == 3:
                # randomized movement
                random_number = random.randint(0, 3)
                if self.flip:
                    if self.rect.left >= 0:
                        dx -= random_number
                elif not self.flip:
                    if self.rect.right <= 1280:
                        dx += random_number

                attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                             2 * self.rect.width, self.rect.height)
                if attacking_rect.colliderect(target.rect):
                    random_chances = random.randint(1, 20)
                    if random_chances == 3:
                        self.attack(target)
                        self.attack_type = random.randint(1, 2)

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > 1280:
            dx = 1280 - self.rect.right
        if self.rect.bottom + dy > 610:
            self.vel_y = 0
            self.jump = False
            dy = 610 - self.rect.bottom

        # ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    # handle animation updates
    def update(self):
        animation_list = self.load_images(player_sheet, player_animation_steps)
        # check what action the player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # 6:death
        elif self.hit == True:
            self.update_action(5)  # 5:hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)  # 3:attack1
            elif self.attack_type == 2:
                self.update_action(4)  # 4:attack2
        elif self.jump == True:
            self.update_action(2)  # 2:jump
        elif self.running == True:
            self.update_action(1)  # 1:run
        else:
            self.update_action(0)  # 0:idle

        animation_cooldown = 30
        # update image
        image = animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if the animation has finished
        if self.frame_index >= len(animation_list[self.action]):
            # if the player is dead then end the animation
            if self.alive == False:
                self.frame_index = len(animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                # check if damage was taken
                if self.action == 5:
                    self.hit = False
                    # if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            # execute attack
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                         2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface, image):
        img = pygame.transform.flip(image, self.flip, False)
        surface.blit(img, (
            self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))


class Fighter:
    def __init__(self, player, x, y, flip, data=None, sprite_sheet=player_sheet, animation_steps=None,
                 sound=player_attack_sound):
        if animation_steps is None:
            animation_steps = player_animation_steps
        if data is None:
            data = player_info
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        # extract images from spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(
                    pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, target, round_over):

        SPEED = 5
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # get keypress
        key = pygame.key.get_pressed()

        # can only perform other actions if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False:
            # check player 1 controls
            if self.player == 1:
                # movement
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                # jump
                if key[pygame.K_SPACE] and not self.jump:
                    self.vel_y = -35
                    self.jump = True
                # attack
                if key[pygame.K_q] or key[pygame.K_e]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_q]:
                        self.attack_type = 1
                    if key[pygame.K_e]:
                        self.attack_type = 2

            # check player 2 controls
            if self.player == 2:
                # movement
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                # jump
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                # attack
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    # determine which attack type was used
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2
            if self.player == 3:
                # randomized movement
                random_number = random.randint(0, 3)
                if self.flip:
                    if self.rect.left >= 0:
                        dx -= random_number
                elif not self.flip:
                    if self.rect.right <= 1280:
                        dx += random_number

                attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                             2 * self.rect.width, self.rect.height)
                if attacking_rect.colliderect(target.rect):
                    random_chances = random.randint(1, 20)
                    if random_chances == 3:
                        self.attack(target)
                        self.attack_type = random.randint(1, 2)

        # apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > 1280:
            dx = 1280 - self.rect.right
        if self.rect.bottom + dy > 610:
            self.vel_y = 0
            self.jump = False
            dy = 610 - self.rect.bottom

        # ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # update player position
        self.rect.x += dx
        self.rect.y += dy

    # handle animation updates
    def update(self):
        # check what action the player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # 6:death
        elif self.hit == True:
            self.update_action(5)  # 5:hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)  # 3:attack1
            elif self.attack_type == 2:
                self.update_action(4)  # 4:attack2
        elif self.jump == True:
            self.update_action(2)  # 2:jump
        elif self.running == True:
            self.update_action(1)  # 1:run
        else:
            self.update_action(0)  # 0:idle

        animation_cooldown = 40
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # check if the animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            # if the player is dead then end the animation
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                # check if damage was taken
                if self.action == 5:
                    self.hit = False
                    # if the player was in the middle of an attack, then the attack is stopped
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            # execute attack
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y,
                                         2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (
            self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
