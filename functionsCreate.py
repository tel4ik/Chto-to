import pdfplumber
from PIL import Image, ImageFont, ImageDraw

groups = {'1РА-20-1уп', '1РА-20-2', '1МРЭП-20-1', '1КСК-20-1', '1ИСИП-20-1', '1ИСИП-20-2к', '1ИС-20-1к', '1РЭТ-20-1к', '1ИБАС-20-1',
          '2ПКС-19-1с', '3РА-18-1уп'}

week = {'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'}

def find_group(group, timetable):
    i = 0
    for gr in timetable:
        if gr == group:
            return i
        i += 1


def timetable_group(timetable, group):
    schedule = []
    ind = find_group(group, timetable)
    for num in range(ind, len(timetable)):
        schedule.append(timetable[num])
        if timetable[num + 1] in groups:
            break
    return schedule


# Сборка предметов с преподавателями
def parse_class(mas_class):
    # print(mas_class)
    if mas_class[0].find('нет') != -1:
        clas = mas_class[0].split(' ')
        prof_name = ''
        i = 0
    elif len(mas_class) < 2:
        clas = mas_class[0].split(' ')
        prof_name = clas[0] + f' {clas[1]}'
        i = 2
    else:
        clas = mas_class[1].split(' ')
        prof_name = mas_class[0] + f'. {clas[0] + clas[1]}'
        i = 2

    name_subject = ''
    while not clas[i].isdigit():
        name_subject += f' {clas[i]}'
        i += 1
    number_lecture = clas[-1]

    subject = f'{prof_name.center(30, " ")} {name_subject.center(30, " ")} {number_lecture.center(5, " ")}'
    return subject


# Конкатинация строк, Преподавателей и предмета, когда два предмета повтроряются
def parse_union(timetable, num):
    delete_ind = []
    print(num)
    while len(num) > 0:
        string = timetable[num[0]].split(' ')
        string = ' '.join(string[:-1]) + ' ' + timetable[num[1]] + ' ' + str(num[0]) + ' ' + timetable[num[0]][-1] + f' {timetable[num[1]].split(" ")[-1]}'
        timetable[num[0]] = string

        string = timetable[num[2]].split(' ')
        string = ' '.join(string[:-1]) + ' ' + timetable[num[1]] + ' ' + str(num[2]) + ' ' + timetable[num[2]][-1] + f' {timetable[num[1]].split(" ")[-1]}'
        timetable[num[2]] = string
        if timetable[num[1]].isdigit():
            print(timetable[num[1]])
            timetable[num[0]] += f' {timetable[num[1]]}'
            timetable[num[2]] += f' {timetable[num[1]]}'
        delete_ind.append(num[1])

        for i in range(3):
            del num[0]

    for i in range(len(delete_ind)):
        del timetable[delete_ind.pop()]


def del_different_info(timetable):
    for i in range(len(timetable)):
        if (timetable[i] in week) or (timetable[i].find('Page') != -1):
            del timetable[i]


def parse_timetable(timetable, group):
    schedule = timetable_group(timetable, group)
    num = []
    new_timetable = []
    for i in range(1, len(schedule)):
        if schedule[i].find('вся группа') != -1:
            schedule[i] = schedule[i].replace('вся группа', '').strip()
        if ((len(schedule[i].split(' ')) > 4) or schedule[i].find('нет') != -1) and schedule[i].find('3Д') == -1:
            continue
        num.append(i)
    del_different_info(schedule)
    print(schedule)

    if len(num) > 1:
        parse_union(schedule, num)

    new_timetable.append(schedule[0].center(65, ' '))

    for ind in schedule:
        if ind not in groups:
            subject = parse_class(ind.split('./'))
            new_timetable.append(subject)
    return new_timetable


def create_image(timetable):
    im = Image.new('RGB', (500, 200), color=('#D3D2D1'))
    font = ImageFont.truetype(r'C:\Users\tawer\PycharmProjects\123\font\Roboto-Black.ttf', size=14)
    draw_text = ImageDraw.Draw(im)
    row = 10
    for key in timetable:
        draw_text.text((10, row),
                       key,
                       font=font,
                       fill='#1C0606')
        row += 20

    im.save('output.png')

def open_pdf(filename, pages):
    text = ''
    with pdfplumber.open(filename) as pdf:
        for page in pages:
            page = pdf.pages[page]
            text += page.extract_text()
    return text


def create_timetable(pages, filename, group):
    timetable = open_pdf(filename, pages)
    timetable = timetable.split('\n')
    timetable = parse_timetable(timetable, group)
    create_image(timetable)
    for i in timetable:
        print(i)


create_timetable([0, 1], 'p.pdf', '2ПКС-19-1с')
