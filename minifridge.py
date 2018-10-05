__author__ = 'Clayton Knittel'
__version__ = '1.1.0'


from datetime import datetime

from PIL import Image
from PIL import ImageDraw

from graphics import TextBox, bg_color, configure_draw_parameters
from files import FridgeFile, save_to_location, lab_computer, black
from times import Date
from methods import get_most_recent_record_date


width, height = 2048, 2048


# the main method, reads files from location, draws a nice
# visualization of all important information, then saves it to
# save_location as a .png image with the name 'fridgelog'.
# Automatically closes all open files and cleans resources
def main_m():
    table_files = []
    date = get_most_recent_record_date(Date(str(datetime.now())))

    yt = ('T', 'P')
    units = ('numeral', 'K', 'numeral', 'bar')
    xt = (1, 2, 5, 6)
    pressure_chambers = (2, 3, 1, 4)

    try:
        print('running backup program: ' + date.tostring())
    except IndexError:
        print(date.tostring())

    # print("collecting data from " + date.tostring())

    for y in range(0, len(yt)):
        table_files.append([])
        for x in range(0, len(xt)):
            try:
                if y == 0:
                    table_files[y].append(FridgeFile(date.tostring(), str(yt[y]), xt[x]))
                else:
                    table_files[y].append(FridgeFile(date.tostring(), str(yt[y])))
                table_files[y][x].open()
            except IOError:
                print(table_files[y][x].tostring() + ' not found')
                table_files[y][x] = None
                pass

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    data = [[]]
    data[0] = ['40k', '4k', 'Still', 'MC']
    data.append([])
    for x in table_files[0]:
        if x is not None:
            data[1].append(str(x.get_last_measurement()))
        else:
            data[1].append("no data")
    data.append([])
    data[2] = ['Still', 'Condense', 'OVC', 'Scroll 1']
    data.append([])
    for x in pressure_chambers:
        try:
            data[3].append(table_files[1][0].get_last_measurement(chamber=x) / 1000)
        except AttributeError:
            print("file not found")
            data[3].append("no data")
            pass

    try:
        flowmeter_file = FridgeFile(date.tostring(), 'Flowmeter')
        data[1].append("Flowmeter")
        flowmeter_file.open()
        data[2].append(flowmeter_file.get_last_measurement())
        flowmeter_file.close()
    except IOError:
        print("Flowmeter not found")
        data[2].append("no data")
        pass

    datetext = TextBox(date.to_string_display(), [.5, .05])
    textboxes = [[]]

    for i in range(0, len(data)):
        textboxes.append([])
        for j in range(0, len(data[i])):
            if data[i][j] is not None:
                if units[i] is not "numeral":
                    textboxes[i].append(TextBox(str(data[i][j]), [(i + 1) / (len(data) + 1) - .04,
                                                                  (j + 1) / (len(data[0]) + 1) - .07], units=units[i]))
                else:
                    textboxes[i].append(TextBox(str(data[i][j]), [(i + 1) / (len(data) + 1) - .04,
                                                                  (j + 1) / (len(data[0]) + 1) - .07]))
            else:
                textboxes[i].append(TextBox("", [(i + 1) / (len(data) + 1) - .04, (j + 1) / (len(data[0]) + 1) - .07]))

    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            if data[i][j] is not None:
                configure_draw_parameters(img.width, img.height, draw.line, draw.text)
                textboxes[i][j].draw()
    datetext.draw('#000000')

    if lab_computer == black:
        save_loc = 'fridgelogB.png'
    else:
        save_loc = 'fridgelog.png'

    try:
        img.save(save_to_location + save_loc)
    except IOError:
        file = open(save_to_location + save_loc, 'w+')
        img.save(save_to_location + save_loc)
        file.close()

    img.close()
    for y in range(0, len(table_files)):
        for x in range(0, len(table_files[y])):
            if table_files[y][x] is not None:
                table_files[y][x].close()
