import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, K_SPACE
from sys import exit
import random

# Initialize Pygame
pygame.init()

# Set up window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Player Game")

# Load images
background = pygame.transform.scale(pygame.image.load("game_map.png").convert(), (WIDTH, HEIGHT))
player_image_original = pygame.image.load("player.png").convert_alpha()
bullet_image_original = pygame.image.load("bullet.png").convert_alpha()
zombie_image_original = pygame.image.load("zombie.png").convert_alpha()

# Resize images
player_image = pygame.transform.scale(player_image_original, (80, 80))  # Adjusted size for the player
bullet_image = pygame.transform.scale(bullet_image_original, (20, 10))
zombie_image = pygame.transform.scale(zombie_image_original, (50, 50))

# Flip the player image horizontally
flipped_player_image = pygame.transform.flip(player_image, True, False)

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

# Set up zombies
zombies = []
wave = 1
zombie_speed = 2
zombies_per_wave = 2
total_waves = 10
waves_completed = 0

# Set up health bar
player_health = 100
font = pygame.font.Font(None, 36)

# Main game loop
clock = pygame.time.Clock()

while waves_completed < total_waves and player_health > 0:
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
    bullets = [(bullet_rect, angle) for bullet_rect, angle in bullets if bullet_rect.colliderect(screen.get_rect())]
    for bullet in bullets:
        bullet_rect, bullet_angle = bullet
        bullet_vector = pygame.math.Vector2(1, 0).rotate(-bullet_angle)
        bullet_rect.x += bullet_vector.x * bullet_speed
        bullet_rect.y += bullet_vector.y * bullet_speed

    # Decrease bullet cooldown timer
    if bullet_timer > 0:
        bullet_timer -= 1

    # Spawn zombies
    if not zombies:
        zombies_per_wave += 2
        for _ in range(zombies_per_wave):
            zombie_rect = zombie_image.get_rect()
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                zombie_rect.topleft = (random.randint(0, WIDTH - zombie_rect.width), 0)
            elif side == "bottom":
                zombie_rect.topleft = (random.randint(0, WIDTH - zombie_rect.width), HEIGHT - zombie_rect.height)
            elif side == "left":
                zombie_rect.topleft = (0, random.randint(0, HEIGHT - zombie_rect.height))
            elif side == "right":
                zombie_rect.topleft = (WIDTH - zombie_rect.width, random.randint(0, HEIGHT - zombie_rect.height))

            zombies.append(zombie_rect)

    # Update zombie positions
    for zombie_rect in zombies[:]:  # Iterate over a copy to allow removal in the loop
        zombie_vector = pygame.math.Vector2(player_rect.centerx - zombie_rect.centerx,
                                            player_rect.centery - zombie_rect.centery)
        if zombie_vector.length() > 0:  # Add this check to avoid normalizing a zero-length vector
            zombie_vector.normalize_ip()
            zombie_rect.x += zombie_vector.x * zombie_speed
            zombie_rect.y += zombie_vector.y * zombie_speed

    # Check for collisions between bullets and zombies
    bullets_to_remove = []
    zombies_to_remove = []

    for bullet in bullets:
        bullet_rect, _ = bullet
        for zombie_rect in zombies[:]:  # Iterate over a copy to allow removal in the loop
            if bullet_rect.colliderect(zombie_rect):
                bullets_to_remove.append(bullet)
                zombies_to_remove.append(zombie_rect)

    # Remove collided bullets
    bullets = [bullet for bullet in bullets if bullet not in bullets_to_remove]

    # Remove collided zombies
    zombies = [zombie for zombie in zombies if zombie not in zombies_to_remove]

    # Check for collisions between player and zombies
    for zombie_rect in zombies:
        if player_rect.colliderect(zombie_rect):
            # Check if the player and zombie sprites are colliding
            if player_rect.colliderect(zombie_rect):
                # Decrease player health when hit by a zombie
                player_health -= 10
                print(f"Player Health: {player_health}")

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

    # Draw zombies
    for zombie_rect in zombies:
        screen.blit(zombie_image, zombie_rect.topleft)

    # Draw health bar
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 20))  # Draw the background of the health bar
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, player_health * 2, 20))  # Draw the filled part of the health bar

    pygame.display.update()
    clock.tick(60)  # Limit frames per second

# Check if all zombies are defeated
if not zombies and len(bullets) == 0:
    waves_completed += 1
    print(f"Wave {waves_completed} completed!")

# Game over
pygame.quit()
exit()
