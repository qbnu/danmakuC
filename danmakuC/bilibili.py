# import json
from ._c.ass import Ass
from .protobuf import BiliCommentProto

__all__ = ['proto2ass']


def proto2ass(
        proto_bytes: bytes,
        width: int,
        height: int,
        reserve_blank: int = 0,
        font_face: str = "sans-serif",
        font_size: float = 25.0,
        alpha: float = 1.0,
        duration_marquee: float = 5.0,
        duration_still: float = 5.0,
        comment_filter: str = "",
        reduced: bool = False,
) -> str:
    ass = Ass(width, height, reserve_blank, font_face, font_size, alpha, duration_marquee,
              duration_still, comment_filter, reduced)

    target = BiliCommentProto()
    target.ParseFromString(proto_bytes)
    for elem in target.elems:
        if elem.mode == 8:
            continue  # ignore scripted comment
        ass.add_comment(
            elem.progress / 1000,  # 视频内出现的时间
            elem.ctime,  # 弹幕的发送时间（时间戳）
            elem.content,
            elem.fontsize,
            {1: 0, 4: 2, 5: 1, 6: 3, 7: 4}[elem.mode],
            elem.color,
        )
    return ass.to_string()



NICONICO_COLOR_MAPPINGS = {
    'red': 0xff0000,
    'pink': 0xff8080,
    'orange': 0xffcc00,
    'yellow': 0xffff00,
    'green': 0x00ff00,
    'cyan': 0x00ffff,
    'blue': 0x0000ff,
    'purple': 0xc000ff,
    'black': 0x000000,
    'niconicowhite': 0xcccc99,
    'white2': 0xcccc99,
    'truered': 0xcc0033,
    'red2': 0xcc0033,
    'passionorange': 0xff6600,
    'orange2': 0xff6600,
    'madyellow': 0x999900,
    'yellow2': 0x999900,
    'elementalgreen': 0x00cc66,
    'green2': 0x00cc66,
    'marineblue': 0x33ffcc,
    'blue2': 0x33ffcc,
    'nobleviolet': 0x6633cc,
    'purple2': 0x6633cc,
}

def process_mailstyle(mail, fontsize):
    pos, color, size, patissier = 0, 0xffffff, fontsize, False
    if not mail:
        return pos, color, size #, patissier
    for mailstyle in mail.split():
        if mailstyle == 'ue': #top middle
            pos = 1
        elif mailstyle == 'shita': #bottom middle
            pos = 2
        elif mailstyle == 'naka': #flying left-to-right
            pos = 0
        elif mailstyle == 'big':
            size = fontsize * 1.44
        elif mailstyle == 'small':
            size = fontsize * 0.64
        elif mailstyle in NICONICO_COLOR_MAPPINGS:
            color = NICONICO_COLOR_MAPPINGS[mailstyle]
        elif len(mailstyle) == 7 and re.match('#([a-fA-F0-9]{6})', mailstyle):
            color = int(re.match('#([a-fA-F0-9]{6})', mailstyle).group(1), base=16)
        elif mailstyle == 'patissier': #for comment art/fixed speed?
            patissier = True
        
    return pos, color, size #, patissier

def proto2assnico(
        proto_fp,
        width: int,
        height: int,
        reserve_blank: int = 0,
        font_face: str = "sans-serif",
        font_size: float = 25.0,
        alpha: float = 1.0,
        duration_marquee: float = 5.0,
        duration_still: float = 5.0,
        comment_filter: str = "",
        reduced: bool = False,
) -> str:
    ass = Ass(width, height, reserve_blank, font_face, font_size, alpha, duration_marquee,
              duration_still, comment_filter, reduced)

    w = proto_fp
    while True:
        size = int.from_bytes(w.read(4))
        if size == 0:
            break

        comment_serialized = w.read(size)
        comment = NNDComment()
        comment.ParseFromString(comment_serialized)
        pos, color, size = process_mailstyle(comment.mail, font_size)
        ass.add_comment(
            comment.vpos / 100,
            comment.date,
            comment.content,
            size,
            pos,
            color,
        )
    return ass.to_string()