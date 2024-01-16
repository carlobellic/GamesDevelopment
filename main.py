import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_SPACE
from sys import exit

# Initialize Pygame
pygame.init()

# Set up window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Player Game")

# Load images
background = pygame.transform.scale(pygame.image.load("game_map.png").convert(), (WIDTH, HEIGHT))
player_image_original = pygame.image.load("player.png").convert_alpha()
bullet_image = pygame.image.load("bullet.png").convert_alpha()

# Flip the player image horizontally
flipped_player_image = pygame.transform.flip(player_image_original, True, False)

# Set up player
player_rect = flipped_player_image.get_rect()
player_rect.center = (WIDTH // 2, HEIGHT // 2)
player_speed = 5

# Set up bullets
bullets = []

# Bullet speed and cooldown
bullet_speed = 10
bullet_cooldown = 30
bullet_timer = 0

# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            exit()

    # Get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate the angle between the player and the mouse
    angle = pygame.math.Vector2(mouse_x - player_rect.centerx, mouse_y - player_rect.centery).angle_to((1, 0))

    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_rect.y -= player_speed
    if keys[pygame.K_s]:
        player_rect.y += player_speed
    if keys[pygame.K_a]:
        player_rect.x -= player_speed
    if keys[pygame.K_d]:
        player_rect.x += player_speed

    # Shooting bullets
    if keys[K_SPACE] and bullet_timer <= 0:
        bullet_rect = bullet_image.get_rect()
        bullet_rect.center = player_rect.center
        bullets.append((bullet_rect, angle))
        bullet_timer = bullet_cooldown

    # Update bullet positions
    for bullet in bullets:
        bullet_rect, bullet_angle = bullet
        bullet_vector = pygame.math.Vector2(1, 0).rotate(-bullet_angle)
        bullet_rect.x += bullet_vector.x * bullet_speed
        bullet_rect.y += bullet_vector.y * bullet_speed

    # Decrease bullet cooldown timer
    if bullet_timer > 0:
        bullet_timer -= 1

    # Rotate the player image with the correct anchor point and scale
    rotated_image = pygame.transform.rotozoom(flipped_player_image, angle, 0.2)
    rotated_rect = rotated_image.get_rect(center=player_rect.center)

    # Update screen
    screen.blit(background, (0, 0))
    screen.blit(rotated_image, rotated_rect.topleft)

    # Draw bullets
    for bullet in bullets:
        bullet_rect, _ = bullet
        screen.blit(bullet_image, bullet_rect.topleft)

    pygame.display.update()
    clock.tick(60)  # Limit frames per second
