import pygame
import math
import sys
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()  # Initialize the mixer explicitly

# Set up the screen
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shrinking Circle with Gravity and Bouncing Ball")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Get ball size multiplier and initial speed from user
size_multiplier = float(input("Enter ball size multiplier (1 for standard size): "))
initial_speed = float(input("Enter initial ball speed multiplier (1 for standard speed): "))
ball_radius = int(10 * size_multiplier)

# Ball settings
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_speed_x = initial_speed * 3
ball_speed_y = initial_speed * 2
gravity = 0.1  # Gravity that will increase vertical speed
bounce_damping = 0.8  # Damping factor for energy loss on each bounce
speed_boost = 1.1  # Speed boost on each collision with the circle boundary
min_speed = initial_speed * 3 * 0.9  # Minimum speed threshold (90% of initial speed)

# Circle settings
circle_radius = 250
circle_center = (WIDTH // 2, HEIGHT // 2)
shrink_rate = 5

# Load multiple ding sounds from 1 to 10
ding_sounds = [
    pygame.mixer.Sound(f'ding{i}.wav') for i in range(1, 11)  # Assumes you have ding1.wav, ding2.wav, ..., ding10.wav
]

# Trail settings
trail = []
trail_delay = 2  # Frames to delay before adding a new trail circle (reduced to 2)
trail_timer = 0  # Timer to control the addition of trail circles

# Contact lock to prevent multiple bounces
contact_lock = False

# Set up font for display
font = pygame.font.Font(None, 36)

# Clock for consistent FPS
clock = pygame.time.Clock()
FPS = 60  # Target frames per second

# Function to calculate distance between two points
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to play a random ding sound with a limit of 0.4 seconds
def play_random_ding():
    sound = random.choice(ding_sounds)  # Randomly select a sound from 1 to 10
    print(f"Playing sound: {ding_sounds.index(sound) + 1}")  # Print which sound is being played
    sound.play()
    pygame.time.set_timer(pygame.USEREVENT, 400)  # Set a timer for 400 milliseconds

# Main game loop
running = True
while running:
    # Fill background with white
    screen.fill(WHITE)

    # Draw the shrinking circle
    pygame.draw.circle(screen, BLACK, circle_center, int(circle_radius), 2)

    # Draw the ball's trail (hollow circles with black borders)
    for tx, ty in trail:
        pygame.draw.circle(screen, BLACK, (int(tx), int(ty)), ball_radius, 1)  # Draw hollow circles

    # Draw the ball
    pygame.draw.circle(screen, BLUE, (int(ball_x), int(ball_y)), ball_radius)

    # Update the ball's position and apply gravity
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    ball_speed_y += gravity  # Increase vertical speed due to gravity

    # Check for collision with the circle boundary
    dist_to_center = distance(ball_x, ball_y, *circle_center)
    if dist_to_center >= circle_radius - ball_radius and not contact_lock:
        # Calculate the normal angle of collision
        angle_to_center = math.atan2(ball_y - circle_center[1], ball_x - circle_center[0])

        # Reflect the ball's velocity vector with a random bounce angle
        random_bounce_angle = random.uniform(-0.3, 0.3)
        angle_to_center += random_bounce_angle

        # Reflect and apply damping
        speed = math.sqrt(ball_speed_x ** 2 + ball_speed_y ** 2)
        ball_speed_x = -speed * math.cos(angle_to_center) * bounce_damping
        ball_speed_y = -speed * math.sin(angle_to_center) * bounce_damping

        # Apply a slight speed boost to keep the ball bouncing actively
        ball_speed_x *= speed_boost
        ball_speed_y *= speed_boost

        # Enforce the minimum speed threshold
        if abs(ball_speed_x) < min_speed:
            ball_speed_x = min_speed * (1 if ball_speed_x > 0 else -1)
        if abs(ball_speed_y) < min_speed:
            ball_speed_y = min_speed * (1 if ball_speed_y > 0 else -1)

        # Shrink the circle
        circle_radius -= shrink_rate
        if circle_radius < ball_radius:
            running = False

        # Play a random ding sound on collision
        play_random_ding()  # Play ding sound

        # Lock contact to prevent multiple triggers
        contact_lock = True
    elif dist_to_center < circle_radius - ball_radius:
        # Reset contact lock when ball is fully away from the circle boundary
        contact_lock = False

    # Check for bounce on the bottom edge of the window
    if ball_y + ball_radius >= HEIGHT:
        ball_y = HEIGHT - ball_radius  # Place ball right on the edge
        ball_speed_y = -ball_speed_y * bounce_damping  # Reverse and dampen speed

        # Play a random ding sound on bounce
        play_random_ding()  # Play ding sound

    # Ensure the ball stays within the circle after each position update
    dist_to_center = distance(ball_x, ball_y, *circle_center)
    if dist_to_center > circle_radius - ball_radius:
        # Move the ball back to the edge of the circle
        angle_to_center = math.atan2(ball_y - circle_center[1], ball_x - circle_center[0])
        ball_x = circle_center[0] + (circle_radius - ball_radius) * math.cos(angle_to_center)
        ball_y = circle_center[1] + (circle_radius - ball_radius) * math.sin(angle_to_center)

    # Handle trail drawing based on timer
    trail_timer += 1
    if trail_timer >= trail_delay:
        trail.append((ball_x, ball_y))
        trail_timer = 0  # Reset the timer

    # Calculate and display ball size and circle circumference at the bottom
    circumference = 2 * math.pi * circle_radius
    size_text = font.render(f"Ball Size: {ball_radius}", True, BLACK)
    circ_text = font.render(f"Circle Circumference: {circumference:.2f}", True, BLACK)

    # Display size and circumference texts at the bottom of the screen
    screen.blit(size_text, (10, HEIGHT - 60))
    screen.blit(circ_text, (10, HEIGHT - 30))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            # Stop all sounds after 0.4 seconds
            pygame.mixer.stop()

    # Update display and maintain consistent FPS
    pygame.display.flip()
    clock.tick(FPS)  # Cap the frame rate

# Quit Pygame
pygame.quit()
sys.exit()
