import random
from datetime import datetime
from PIL import ImageDraw, Image, ImageFont
import math
from datetime import datetime, timedelta
import textwrap
from io import BytesIO
from collections import Counter



class CalendarDrawer:


    def __init__(self, min_hour = 10, max_hour = 20):

        # We set min-max hour by default 10 and 20 None and let user choose if he wants
        self.min_hour = min_hour
        self.max_hour = max_hour
        self.interval = max_hour - min_hour
        self.font_file = 'fonts/blueberrydays/Blueberry Days.ttf'
        self.font_size = 60

        #Much literals below
        self.start_items_x = 548
        self.start_items_y = 400  # 415  #380
        self.x_step = 475  #x(column step) is static neigther dinamical y_step(which depends on chosen start-end hours)
        self.calendar_width = 2040 #Thit means width of useful drawspace
        self.y_step = self.calendar_width / self.interval

        self.y_drawing_hours_start_point = 328 #the start points from first day of week, can use only literals
        self.y_drawing_lines_start_point = 430
        self.x_column_start = 435
        self.y_column_start = 260

        self.fontsize_coefficient = 0.6  # 0.7
        self.chars_per_line_coefficient = 0.65
        self.extra_y_limit = 34

        self.changing_y_after_overcome_extra_y_limit = 12
        self.coefficient_when_overcome_extra_y_limit = 1.55
        self.coefficient_when_overcome_three_lines = 1

        self.img = Image.open('raw_pictures/english_lang_picture.png')
        self.draw = ImageDraw.Draw(self.img)

        self.font = ImageFont.truetype(self.font_file, size=int(self.font_size))
        self.daynames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


        self.coefficient_slot_y = 1560
        self.slot_height = self.coefficient_slot_y/self.interval
        self.slot_width = 410
        self.start_font_for_calculations = ImageFont.truetype('fonts/blueberrydays/Blueberry Days.ttf', size=int(65))
        self.day_start = datetime.strptime('00:00', '%H:%M')
        self.color = (195, 124, 180)
        self.start_font_size_for_items = 65 #font size in this lib is dinamical and can be changed, start font means max font size

    def __draw_columns(self, week: list):

        pointed_week_day = week[0][0]
        start_week = pointed_week_day - timedelta(days=pointed_week_day.weekday())
        x_start = self.x_column_start

        for count, day_name in enumerate(self.daynames):
            self.draw.text((x_start, self.y_column_start),
                           f'{day_name} {datetime.strftime(start_week + timedelta(days=count), "%d.%m")}',
                           font=self.font,
                           stroke_fill='black', stroke_width=5)
            x_start += self.x_step



    def __calculations(self, date: datetime):

        filtered_date = datetime.strptime(datetime.strftime(date, '%Y-%m-%d %H:00'),
                                                 '%Y-%m-%d %H:00')
        week_start = filtered_date - timedelta(days=filtered_date.weekday(), hours=filtered_date.hour)

        total = []

        day_number = 0
        count = 0
        for i in range(7 * self.interval):

            if count >= self.interval:
                count = 0
                day_number += 1
            dat = datetime.strptime(datetime.strftime(week_start, f'%Y-%m-{week_start.day + day_number} {self.min_hour}:00'),
                                             '%Y-%m-%d %H:00') + timedelta(hours=count)
            total.append(dat)
            count += 1
        index = total.index(filtered_date)
        return index




    def __draw_lines_and_hours(self):

        y_drawing_hours_start = self.y_drawing_hours_start_point + (624/self.interval)
        y_drawing_lines_start = self.y_drawing_lines_start_point + (824/self.interval)
        for i in range(self.interval):

            self. draw.text((125, y_drawing_hours_start),
            f'{datetime.strftime(datetime.strptime(f"{self.min_hour}:00", "%H:%M") + timedelta(hours=i), "%H:%M")}',
                      font=self.font,
                      stroke_fill='black', stroke_width=5)
            y_drawing_hours_start += self.y_step

            #draw 7(like on each weekday) lines on each hour
            x = 350
            for i in range(7):
                self.draw.line(((x, y_drawing_lines_start), (x + 400, y_drawing_lines_start)), fill=self.color, width=3)
                x += 475
            y_drawing_lines_start += self.y_step

    def __draw_items(self, data: list):

        for item in data:
            #Here we start define cords and other measures, to consider where and how draw lines if these not overcome slot's area
            text = item[1]
            date = item[0]
            index = self.__calculations(date)
            column_index = index // self.interval
            row_index = index % self.interval
            x_central  = self.start_items_x + (self.x_step * column_index)
            y_central = self.start_items_y + (self.y_step * row_index)

            slot_area = self.slot_width * self.slot_height
            letter_area = slot_area / len(text)

            #We define required fontsize not the text to overzome borders of slot, after this we break text on lines
            dynamic_font_size = self.fontsize_coefficient * math.sqrt(1.6 * letter_area)

            font = ImageFont.truetype('fonts/blueberrydays/Blueberry Days.ttf', size=int(dynamic_font_size))
            average_font_width = sum([font.getsize(word)[0] for word in text]) / len(text)
            chars_per_line = (self.slot_width // average_font_width) / (self.chars_per_line_coefficient*(len(text)/12))
            lines = textwrap.wrap(text, width=round(chars_per_line), break_long_words=False)

            #Then we define whether the height of wrapped text not more than the slots's height. If yes, we * it on coefficient (0.7 by default)
            max_height_of_item_text = max(font.getsize(line)[1] for line in lines)
            num_lines = len(lines)

            if len(text) > self.extra_y_limit:
                y_central -= self.changing_y_after_overcome_extra_y_limit

            if max_height_of_item_text*num_lines >= self.slot_height:
                lines = textwrap.wrap(text, width=len(text)//2, break_long_words=False, max_lines=3)
                font = ImageFont.truetype('fonts/blueberrydays/Blueberry Days.ttf',
                                          size=int(dynamic_font_size * self.coefficient_when_overcome_three_lines))

            random_color = (random.randint(100, 255), random.randint(170, 255), random.randint(80, 255))
            step = 0
            lines_num = len(lines)

            for line in lines:
                 line_width, line_height = font.getsize(line)
                 y_calc = (line_height * lines_num)/2
                 finish_y = y_central - y_calc + y_calc*step
                 finish_x = x_central - (line_width/2)
                 self.draw.text((finish_x, finish_y), line, font=font, fill=random_color, stroke_fill='black', stroke_width=5)
                 step += 1


            x_central += (self.x_step * column_index)
            y_central += self.y_step * row_index
            #font = ImageFont.truetype('fonts/blueberrydays/Blueberry Days.ttf', size=int(dynamic_font_size))

    def __define_weeks(self, data: list):
        dates = [date[0] for date in data]
        week_numbers = set(date.isocalendar().week for date in dates)
        weeks = []
        for number in week_numbers:
            week = []
            for item in data:
                date = item[0]
                if date.isocalendar().week == number:
                    week.append(item)
            weeks.append(week)

        return weeks

    def __exception_filter(self, data):
        dates = []
        texts = []
        for i in data:

            if i[0].hour < self.min_hour or i[0].hour > self.max_hour:
                raise Exception(
                    "The datetime doesnt belong to chosen time interval. If you didnt set min and max times, by default "
                    "min time is 10:00 and max is 20:00. Change min_hour and max_hour to remove error, or you can set print_all_dates"
                    "in arguments of class")

            elif self.min_hour > self.max_hour:
                raise Exception(
                    "Min_hour is more than max_hour. Change min_hour and max_hour to remove error")
            dates.append(datetime.strftime(i[0], '%Y-%m-%d %H:00'))
            texts.append(i[1])


        uniq_dates = list(set(dates))
        c_dates = Counter(dates)
        c_uniq_dates = Counter(uniq_dates)
        results = c_dates - c_uniq_dates
        indexes = []
        for i in tuple(results):
            indexes.append(dates.index(i))
        if results:
            raise Exception(f"Can't draw items with equal dates. The dates: {[result for result in tuple(results)]} "
                            f"texts: {[texts[index] for index in indexes]}")


    def draw_calendar(self, data: list):
        weeks = self.__define_weeks(data)

        for num, week in enumerate(weeks):

            self.__exception_filter(week)
            self.__draw_columns(week)
            self.__draw_lines_and_hours()
            self.__draw_items(week)
            self.img.save(f'Results/result{num}.png')
            self.img.close()

    def draw_calendar_bytesio(self,data: list) -> list:

        weeks = self.__define_weeks(data)
        pics = []
        for num, week in enumerate(weeks):

            self.__exception_filter(week)
            self.__draw_columns(week)
            self.__draw_lines_and_hours()
            self.__draw_items(week)
            finished_image_content = BytesIO()
            finished_image_content.seek(0)
            self.img.save(finished_image_content, format='PNG')

            finished_image_content.name = (
                f'/home/root/your/folder/result{num}.png'
            )
            pics.append(finished_image_content)

        return pics

data_set_en = [
        [datetime.strptime('2022-08-15 11:00:00', '%Y-%m-%d %H:%M:%S'), 'What is love?'],
        [datetime.strptime('2022-08-16 13:00:00', '%Y-%m-%d %H:%M:%S'), 'Baby dont hurt me dont hurt me']
        ]

calendar = CalendarDrawer()
calendar.draw_calendar(data_set_en)