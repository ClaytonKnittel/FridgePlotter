__author__ = 'Clayton Knittel'
__version__ = '1.1.0'

from times import Time, Date
from files import graph_time, lab_computer, black, save_to_location, DynamicFile
from graphics import bg_color, TextBox, Graph, configure_draw_parameters

from PIL import Image
from PIL import ImageDraw

""" ImageDraw done from top left of screen """


loop = True


width, height = 2048, 2048


pres = {
        'ovc': 1,
        'still': 2,
        'condense': 3,
        'scroll 1': 4,
        'scroll1': 4,
}


expls = [
    'quit the program',
    'list all valid commands'
]


def print_cmds(cmdse):
    ar = cmdse.keys()
    print('\nCommands:')
    for e, ex in zip(ar, expls):
        print('\t' + e + '  -  ' + ex)
    print('\nExample input:\n\tdate: 17-11-14 (november 14, 2017)\n\tdata: T1 (temperature chamber 1)')
    print('')


cmds = {
    'quit': lambda: exit(0),
    'help': lambda: print_cmds(cmds),
}


def dissect(data):
    val = pres.get(data.lower())
    if val is not None:
        return 'maxigauge', val
    print(val)
    if data[-1:].isnumeric():
        return data[:-1].strip(), int(data[-1:])
    return data.strip(), 0


def max_format(data):
    return data.lower() == 'maxigauge'


def _input(text):
    i = input(text)
    cmd = cmds.get(i)
    if cmd is not None:
        cmd()
        return _input(text)
    return i


# the main method, reads files from location, draws a nice
# visualization of all important information, then saves it to
# save_location as a .png image with the name 'fridgelog'.
# Automatically closes all open files and cleans resources
def main(datee, data, save=False, graphtime=graph_time):
    date = Date(datee)

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    configure_draw_parameters(img.width, img.height, draw.line, draw.text)

    t, c = dissect(data)

    file = DynamicFile(date, t, c, graphtime)

    g = Graph.fromfile(file, (.13, .13), .8, .8, graph_width=2)
    g.draw()
    tb = TextBox("Data from " + date.to_string_display() + '      data type: ' + data, (.5, .02), is_cell=True)
    tb.draw()

    try:
        print(date.tostring() + ' at ' +
              Time.get_time_without_seconds(file.get_last_measurement_time()))
    except IndexError:
        print(date.tostring())

    img.show()

    if save:
        if lab_computer == black:
            save_str = 'fridgelogB_'
        else:
            save_str = 'fridgelog_'

        try:
            img.save(save_to_location + save_str + data + '.png')
        except IOError:
            file = open(save_to_location + save_str + data + '.png', 'w+')
            img.save(save_to_location + save_str + data + '.png')
            file.close()

    img.close()
    file.close()


main(_input('date: '), _input('data: '), save=_input('save (y/n): ') == 'y',
     graphtime=int(_input('graph time (hours): ')) * 3600)
