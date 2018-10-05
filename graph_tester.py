from graphics import Graph, configure_draw_parameters, font_location
from files import OutputLine
import pygame


s = '{:.6f}'.format(10.0)
print(s)
exit(0)


w = 1200
h = 800

screen = pygame.display.set_mode((w, h))
screen.convert()
pygame.display.set_caption('Graph tester')

vals = [10 ** -4.698970004336019, 10 ** -5.873712505420023, 10 ** -5, 10 ** -5, 10 ** -5, 10 ** -5, 10 ** -4.9, 10 ** -5.1]
graph = None

pygame.font.init()
fontf = pygame.font.Font(font_location, 12)

def draw_text(pos, txt, font=None, fill=(0, 0, 0, 0xff)):
    global fontf
    text = fontf.render(txt, True, html_to_tuple(fill))
    screen.blit(text, (pos[0] + 70, pos[1]))


def crt_grph(data):
    lista = []
    t = 0
    for v in vals:
        lista.append(OutputLine('23-07-18,00:' + str(t) + ':00,' + str(v), 'T', 1))
        t += 10
    global graph
    graph = Graph(lista, (.1, .1), .8, .8, axis_label='Val', units='C', graph_width=2, log_vals=True)


def html_to_tuple(html_color):
    return (int(html_color[1:3], 16), int(html_color[3:5], 16), int(html_color[5:7], 16), 0xff)


def draw(poses, fill, width=1):
    fill = html_to_tuple(fill)
    pygame.draw.line(screen, fill, poses[0], poses[1], width)


configure_draw_parameters(w, h, draw, draw_text)


def draw():
    # vals[0] *= 1.004
    # global vals
    # vals += [40]
    crt_grph(vals)
    screen.fill((0x00, 0xee, 0xee, 0xff))
    graph.draw()
    pygame.display.flip()


run = True


def inputs():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global run
            run = False


while run:
    draw()
    inputs()

pygame.display.quit()
