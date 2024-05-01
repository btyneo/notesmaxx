from PIL import Image, ImageDraw, ImageFont
import uuid
import string
import random

import io
import string
import random


def create_image(bullet_points):
    # bullet_points is the 'format_for_notes' list from other file.
    background = Image.open('notesmaxx_template.jpg')
    font = ImageFont.truetype('impact.ttf', 34)
    font_header = ImageFont.truetype('impact.ttf', 50)
    object1 = ImageDraw.Draw(background)
    color = 'black'

    width, height = background.size

    starting_pos = 100
    if len(bullet_points) < 10:
        min_index = 0
        max_index = 13
    else:
        min_index = 3
        max_index = 15
    for num, point in enumerate(bullet_points):
        if point.strip() in ["", "", "  ", "   ", "   "]:
            continue
        if '-' in point:
            point = point[2::]
        if num != 0:
            point = point.strip()
            point = f"• {point}."
        length = len(point)
        text_bbox = object1.textbbox((0, 0), point, font=font)
        image_width, image_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        if num == 13:
            break
        if num == 0:
            x = (width // 2)
            object1.text((x - 82, starting_pos), 'NOTESMAXX', font=font_header, fill=color)
            starting_pos += image_height + 150
            x = (width // 9.5) - 15
        if num >= min_index or (max_index <= num >= min_index):
            if length >= 70:
                split_index = point.rfind(' ', 0, 68)  # Find the last space within the first 50 characters
                second_point = point[split_index:]
                if len(second_point) >= 75:
                    split_index2 = second_point.rfind(' ', 0, 73)
                    if second_point.lower().endswith('and'):
                        split_index2 -= 3
                    elif second_point.lower().endswith('and '):
                        split_index2 -= 4
                else:
                    split_index2 = len(second_point)
                if split_index == -1:
                    split_index = 70  # If no space found, split at character 68
                object1.text((x, starting_pos), point[:split_index], font=font, fill=color)
                object1.text((x, starting_pos + 35), f"{second_point[:split_index2].lstrip()}", font=font, fill=color)
                starting_pos += image_height + 90
            else:
                object1.text((x, starting_pos), point, font=font, fill=color)
                starting_pos += image_height + 70

        # if length > 65:
        #     object1.text((x, starting_pos), point[:50], font=font, fill=color)
        #     starting_pos += image_height + 70
        #     object1.text((x, starting_pos+35), point[50::], font=font, fill=color)
        # else:
        #     object1.text((x, starting_pos), point, font=font, fill=color)
        #     starting_pos += image_height + 70


    random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    background.save(f'{random_filename}.png')
    return f"{random_filename}.png"

    # print("\nCreated image!")
    # show_or_not = input("Display Image: (Y/N) ")
    # if show_or_not.lower() in ["yes", 'y']:
    #     show_image(random_filename)


# def show_image(file_path):
#     img = Image.open(f"{file_path}.png")
#     img.show()
#----------------------------
# def create_image(bullet_points):
#     # bullet_points is the 'format_for_notes' list from other file.
#     background = Image.open('notesmaxx_template.jpg')
#     font = ImageFont.truetype('arial.ttf', 30)
#     object1 = ImageDraw.Draw(background)
#     color = 'black'
#
#     width, height = background.size
#     starting_pos = 100
#
#     for num, point in enumerate(bullet_points):
#         length = len(point)
#         text_bbox = object1.textbbox((0, 0), point, font=font)
#         image_width, image_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
#         x = ((width - image_width) // 2)
#         if num == 7:
#             break
#         if num == 0:
#             object1.text((x-100, starting_pos), 'NOTESMAXX', font=font, fill=color)
#             starting_pos += image_height + 250
#             x += 400
#         if length > 65:
#             split_index = point.rfind(' ', 0, 50)  # Find the last space within the first 50 characters
#             if split_index == -1:
#                 split_index = 50  # If no space found, split at character 50
#
#             object1.text((x, starting_pos), point[:split_index], font=font, fill=color)
#             starting_pos += image_height + 70
#             object1.text((x, starting_pos + 35), point[split_index:].lstrip(), font=font, fill=color)
#         else:
#             object1.text((x, starting_pos), point, font=font, fill=color)
#             starting_pos += image_height + 70
#         # if length > 65:
#         #     object1.text((x, starting_pos), point[:50], font=font, fill=color)
#         #     starting_pos += image_height + 70
#         #     object1.text((x, starting_pos+35), point[50::], font=font, fill=color)
#         # else:
#         #     object1.text((x, starting_pos), point, font=font, fill=color)
#         #     starting_pos += image_height + 70
#
#     random_filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#     background.save(f'{random_filename}.png')
#     print("\nCreated image!")

