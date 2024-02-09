import line
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util

# --- Initialise PyGame --- 

pygame.init()
pygame_clock = pygame.time.Clock()

pygame_display_surface = pygame.display.set_mode((400, 300), RESIZABLE)

is_main_game_loop_running = True

pygame_font = pygame.font.SysFont(None, 48)

# --- Initialise PyMunk --- 

pymonk_gravity_scale = -900.0
pymonk_wind_scale = 0.0

pymonk_physics_space = pymunk.Space()
pymonk_physics_space.gravity = (pymonk_gravity_scale, pymonk_wind_scale)

# --- Main Gameplay Loop --- 

while is_main_game_loop_running:
  pygame_clock.tick(60)
  for pygame_user_input_event in pygame.event.get():
    if pygame_user_input_event.type == pygame.QUIT:
      is_main_game_loop_running = False

  

  pygame.display.update()

pygame.quit()


# rad = 14
# ball_elasticity = 0.8
# friction = 1.0
# circles = []

# def create_circle(position):
#     mass = 1
#     inertia = pymunk.moment_for_circle(mass, 0, rad)
#     body = pymunk.Body(mass, inertia)
#     body.position = position
#     shape = pymunk.Circle(body,rad)
#     shape.elasticity = ball_elasticity
#     shape.friction = friction
#     space.add(body,shape)

#     return shape

# def create_line(p1,p2):
#     static_body = space.static_body
#     static_body.position = (400, 600)
#     line_shape = pymunk.Segment(static_body, p1, p2, 15)
#     line_shape.elasticity = 1.0
#     line_shape.color = (100, 200, 0)
#     space.add(line_shape)
#     return line_shape

# create_line((400,-500),(400,0))
# create_line((-400,-500),(-400,0))


# while running:
#     clock.tick(60)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.MOUSEBUTTONDOWN:
#             originalMousePos = pygame.mouse.get_pos()
#             realPos = pymunk.pygame_util.to_pygame(originalMousePos, screen)
#             newCircle = create_circle(realPos)
#             circles.append(newCircle)
#             print(len(circles))

#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_RIGHT:
#                 wind+=50
#             if event.key == pygame.K_LEFT:
#                 wind-=50
#             if event.key == pygame.K_UP:
#                 gravity+=50
#             if event.key == pygame.K_DOWN:
#                 gravity-=50
#             if event.key == pygame.K_l:
#                 rad = 1
#                 friction = 0.1

#     screen.fill((50,50,50))

#     for circle in circles:
#         circlePosition = int(circle.body.position.x), 600-int(circle.body.position.y)
#         pygame.draw.circle(screen, (35, 88, 150), circlePosition, int(circle.radius), 0)


#     circleCount = font.render(str(len(circles)), 1, (255, 0, 0))
#     screen.blit(circleCount, (30, 10))

#     currentFPS = font.render(str(int(clock.get_fps())), 1, (255, 0, 0))
#     screen.blit(currentFPS, (30, 40))


#     pygame.draw.line(screen, line.color,(0,500),(800, 500), 30)
#     pygame.draw.line(screen, line.color,(0,500),(0,0),30)
#     pygame.draw.line(screen, line.color,(800,500),(800,0),30)

#     space.gravity = (wind, gravity)
#     space.step(1/60.0)
#     pygame.display.update()

# pygame.quit()
