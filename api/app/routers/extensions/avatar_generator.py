import py_avataaars as pa
import requests
# assigning various parameters to our avatar
import py_avataaars as pa
from py_avataaars import TopType
import random
import time


def create_avatar(filename, sex):
    female_hairs = [
        TopType.LONG_HAIR_BIG_HAIR,
        TopType.LONG_HAIR_BOB,
        TopType.LONG_HAIR_BUN,
        TopType.LONG_HAIR_CURLY,
        TopType.LONG_HAIR_CURVY,
        TopType.LONG_HAIR_DREADS,
        TopType.LONG_HAIR_FRIDA,
        TopType.LONG_HAIR_FRO,
        TopType.LONG_HAIR_FRO_BAND,
        TopType.LONG_HAIR_NOT_TOO_LONG,
        TopType.LONG_HAIR_MIA_WALLACE,
        TopType.LONG_HAIR_SHAVED_SIDES,
        TopType.LONG_HAIR_STRAIGHT,
        TopType.LONG_HAIR_STRAIGHT2,
        TopType.LONG_HAIR_STRAIGHT_STRAND,
    ]
    if sex == 0:
        facial_hair_type = pa.FacialHairType.DEFAULT
        hair_type = random.choice(female_hairs)
    else:
        facial_hair_type = random.choice([color for color in pa.FacialHairType])
        hair_type = list(set([hair for hair in TopType]).difference(female_hairs))
        hair_type.remove(TopType.HIJAB)
        hair_type.remove(TopType.TURBAN)
        hair_type = random.choice(hair_type)

    mouth_type = [top_type for top_type in pa.MouthType]
    mouth_type.remove(pa.MouthType.VOMIT)

    avatar = pa.PyAvataaar(
        background_color=random.choice([color for color in pa.Color]),
        style=pa.AvatarStyle.CIRCLE,
        skin_color=pa.SkinColor.LIGHT,
        hair_color=random.choice([color for color in pa.HairColor]),
        facial_hair_type=facial_hair_type,
        facial_hair_color=random.choice([color for color in pa.HairColor]),
        # top_type=random.choice([top_type for top_type in pa.TopType]),
        top_type=hair_type,
        hat_color=random.choice([color for color in pa.Color]),
        mouth_type=random.choice(mouth_type),
        eye_type=random.choice([eye_type for eye_type in pa.EyesType]),
        eyebrow_type=random.choice([eyebrow_type for eyebrow_type in pa.EyebrowType]),
        nose_type=random.choice([nose_type for nose_type in pa.NoseType]),
        accessories_type=pa.AccessoriesType.DEFAULT,
        # random.choice([accessories for accessories in pa.AccessoriesType]),
        clothe_type=random.choice([clothe for clothe in pa.ClotheType]),
        clothe_color=random.choice([color for color in pa.Color]),
        clothe_graphic_type=random.choice([graphic for graphic in pa.ClotheGraphicType]),
    )
    avatar.render_svg_file(filename)
    return filename


def send_image(image):
    url = "https://api.telegram.org/bot1717340508:AAGOVTeSMnRDP73mbZyc8pFvZg-0IuatSXA/sendPhoto";
    files = {'photo': open(image, 'rb')}
    data = {'chat_id': "-1001289396889"}
    r = requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)


if __name__ == '__main__':
    while True:
        filename = create_avatar("test.svg", 0)
        send_image(filename)
        time.sleep(60)
