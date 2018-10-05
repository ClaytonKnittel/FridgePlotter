__author__ = 'Clayton Knittel'
__version__ = '1.1.0'


from datetime import datetime
import time

import traceback

from minifridge import main_m, get_most_recent_record_date
from times import Time, Date
from files import FridgeFile, lab_computer, black, save_to_location, DynamicFile, tester
from graphics import bg_color, TextBox, Graph, Table, configure_draw_parameters
from methods import convert, scientific_sf

from PIL import Image
from PIL import ImageDraw

""" ImageDraw done from top left of screen """


loop = True


width, height = 2048, 2048


# the main method, reads files from location, draws a nice
# visualization of all important information, then saves it to
# save_location as a .png image with the name 'fridgelog'.
# Automatically closes all open files and cleans resources
def main():
    pressure_file = None
    date = get_most_recent_record_date(Date(str(datetime.now())))
    temperature_files = []
    graph_files = []

    types = ('T', 'maxigauge')
    temperature_chambers = (1, 2, 5, 6)
    pressure_chambers = (1, 2, 3, 4, 5, 6)

    try:
        pressure_file = FridgeFile(date.tostring(), types[1])
        pressure_file.open()
    except IOError:
        print(pressure_file.tostring() + ' not found')

    for x in range(0, len(temperature_chambers)):
        try:
            temperature_files.append(FridgeFile(date.tostring(), types[0], temperature_chambers[x]))
        except IOError:
            print(temperature_files[x].tostring() + ' not found')
            temperature_files[x] = None

    img = []
    draw = []
    for i in range(0, 11):
        img.append(Image.new('RGB', (width, height), bg_color))
        draw.append(ImageDraw.Draw(img[-1]))

    i = 0
    for t, chambers in zip(types, [temperature_chambers, pressure_chambers]):
        for c in chambers:
            configure_draw_parameters(img[i].width, img[i].height, draw[i].line, draw[i].text)

            if t == 'maxigauge':
                graph_files.append(DynamicFile(date, t, c, scale_nums=1))
            else:
                graph_files.append(DynamicFile(date, t, c))

            if lab_computer == tester:
                print(graph_files[-1])

            if not graph_files[-1].is_empty():
                g = Graph.fromfile(graph_files[-1], (.13, .33), .8, .6, graph_width=2, log_vals=t == 'maxigauge')
                g.draw()
                try:
                    tb = TextBox.datetime_box(date, graph_files[-1].get_last_measurement_time(), i)
                except IndexError:
                    tb = TextBox("Data from " + date.to_string_display() + '     ' + 'Chamber ' +
                                 str(convert(i)).replace('_', ' '), (.5, .02), is_cell=True)
                tb.draw()
            i += 1

    data = []
    for t in graph_files:
        data.append(t.get_last_measurement())
    t_temp = Table((.1, .05), .4, .2, ['Plate', 'Temperature'], ['T1: 40k', 'T2: 4k', 'T5: Still', 'T6: MC'],
                   ['numeral', 'K'], [data[:4]])
    t_pres = Table((.5, .05), .4, .2, ['Gauge', 'Pressure'],
                   ['P1: OVC1', 'P2: Still', 'P3: Condense', 'P4: LN2 Trap', 'P5: Tank', 'P6: OVC2'],
                   ['numeral', 'bar'], [data[4:]])

    for imgs, draws in zip(img, draw):
        configure_draw_parameters(imgs.width, imgs.height, draws.line, draws.text)
        t_temp.draw()
        t_pres.draw()

    try:
        configure_draw_parameters(img[-1].width, img[-1].height, draw[-1].line, draw[-1].text)
        flowmeter_file = FridgeFile(date.tostring(), 'Flowmeter')
        flowmeter_file.open()

        flow = Table((.65, .27), .23, .05, ['Flow'],
                     [], ['mol/s'], [scientific_sf(flowmeter_file.get_last_measurement())])

        g = Graph.fromfile(flowmeter_file, (.13, .33), .8, .6, graph_width=2)
        g.draw()
        try:
            tb = TextBox.datetime_box(date, graph_files[-1].get_last_measurement_time(), i)
        except IndexError:
            tb = TextBox("Data from " + date.to_string_display() + '     ' + 'Chamber ' +
                         str(convert(i)).replace('_', ' '), (.5, .02), is_cell=True)
        tb.draw()

        for i in range(0, len(img)):
            configure_draw_parameters(img[i].width, img[i].height, draw[i].line, draw[i].text)
            flow.draw()

        flowmeter_file.close()
    except IOError:
        print("Flowmeter not found")
        pass

    try:
        print(date.tostring() + ' at ' +
              Time.get_time_without_seconds(graph_files[0].get_last_measurement_time()))
    except IndexError:
        print(date.tostring())

    if lab_computer == black:
        save_str = 'fridgelogB_'
    else:
        save_str = 'fridgelog_'

    for i in range(0, len(img)):
        try:
            img[i].save(save_to_location + save_str + str(convert(i)) + '.png')
        except IOError:
            file = open(save_to_location + save_str + str(convert(i)) + '.png', 'w+')
            img[i].save(save_to_location + save_str + str(convert(i)) + '.png')
            file.close()

        img[i].close()
        if i < len(graph_files):
            graph_files[i].close()


if loop:
    while True:
        print('Data from:')
        try:
            main()
        except Exception as e:
            traceback.print_exc()
            main_m()
        if lab_computer == tester:
            exit(0)
        time.sleep(60)
else:
    try:
        main()
    except Exception as e:
        main_m()
