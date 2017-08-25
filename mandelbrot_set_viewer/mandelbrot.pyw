import pygame, numpy

def col(x):
    """return colour for x values from 0 - 1023"""
    if x < 256:return (0, 0, x)
    elif x < 512:return (x-256, x-256, 255)
    elif x < 768:return (255, 255-(x-512)/2, 767-x)
    elif x < 1024:return (1023-x, 127-(x-768)/2, 0)
    else:
        raise ValueError("Colour value not in range 0 - 1023)")

def gen_brot(rect, array, maxdepth, SCREEN_X, SCREEN_Y):
    colour_increment = 1024 / maxdepth
    scale_x = SCREEN_X / rect[2]
    scale_y = SCREEN_Y / rect[2] * 1.4
    for y in range(SCREEN_Y):
        point_y = (y / scale_y + rect[1]) * 1j
        for x in range(SCREEN_X):
            c = x / scale_x + rect[0] + point_y
            z = 0
            for depth in range(maxdepth):
                z = z**2 + c
                if z.real**2 + z.imag**2 >= 4:
                    break
            if depth == maxdepth - 1:
                array[x, y] = 0
            else:
                array[x, y] = col(depth * colour_increment)

def main():
    pygame.init()
    SCREEN_X = 350
    SCREEN_Y = int(SCREEN_X / 1.4)
    rect = (-2.5, -1.25, 3.5)

    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    pixelarray = numpy.zeros((SCREEN_X, SCREEN_Y, 3), dtype=numpy.uint16)
    pygame.display.set_caption("The Mandlebrot Set")
    clock = pygame.time.Clock()

    done = False
    selecting = False

    gen_brot(rect, pixelarray, 256, SCREEN_X, SCREEN_Y)
    mandelbrot = pygame.surfarray.make_surface(pixelarray)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    start_mouse_pos = pygame.mouse.get_pos()
                    selecting = True
                if event.button == 3:
                    selecting = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if selecting:
                        scaled_corners = [(pos[0] / SCREEN_X * rect[2] + rect[0], (pos[1] / (SCREEN_Y / rect[2] * 1.4) + rect[1])) for pos in (start_mouse_pos, pygame.mouse.get_pos())]
                        if scaled_corners[0][0] != scaled_corners[1][0]:
                            rect = (min(scaled_corners[0][0], scaled_corners[1][0]), min(scaled_corners[1][1], scaled_corners[0][1]), abs(scaled_corners[1][0] - scaled_corners[0][0]))
                            gen_brot(rect, pixelarray, 256, SCREEN_X, SCREEN_Y)
                            pygame.surfarray.blit_array(mandelbrot, pixelarray)
                        selecting = False
                        
        screen.blit(mandelbrot,(0,0))
        if selecting:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < start_mouse_pos[1]:
                pygame.draw.rect(screen, (255,255,255), (start_mouse_pos[0], start_mouse_pos[1], mouse_pos[0] - start_mouse_pos[0], abs(mouse_pos[0] - start_mouse_pos[0]) / -1.4), 1)
            else:
                pygame.draw.rect(screen, (255,255,255), (start_mouse_pos[0], start_mouse_pos[1], mouse_pos[0] - start_mouse_pos[0], abs(mouse_pos[0] - start_mouse_pos[0]) / 1.4), 1)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

main()
