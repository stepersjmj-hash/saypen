# 로고(28단위: 파란 배경 + 흰 막대 3개, 3번째 안쪽 초록)를 PNG 아이콘으로 그림
#   icon-180/192/512.png — 홈 화면·앱 바로가기용, 모서리까지 꽉 찬 정사각형 (둥근 모서리는 기기가 깎음)
#   ../logo.png (192px)  — favicon(브라우저 탭·네이버 바로가기가 집는 첫 rel=icon), 둥근 모서리 + 투명 바깥.
#                          64px 처럼 작으면 네이버 바로가기가 버리고 아이콘 없이 만듦 → 크게(kids 는 116px)
# 사용: python tools/mkicon.py icons   (logo.png 는 icons 의 상위 폴더 = 저장소 루트에 생김)
import sys
from PIL import Image, ImageDraw
out = sys.argv[1]

def icon(size, rounded=False):
    k = 4; S = size * k; u = S / 28
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if rounded: d.rounded_rectangle([0, 0, S - 1, S - 1], radius=8 * u, fill='#2f6fed')
    else:       d.rectangle([0, 0, S, S], fill='#2f6fed')
    def bar(x, y, w, h, c): d.rounded_rectangle([x*u, y*u, (x+w)*u, (y+h)*u], radius=w/2*u, fill=c)
    bar(7.5, 9.5, 3, 9, '#ffffff'); bar(12.5, 6, 3, 16, '#ffffff')
    bar(16.5, 7.5, 5, 13, '#ffffff'); bar(17.5, 8.5, 3, 11, '#16a34a')
    im = im.resize((size, size), Image.LANCZOS)
    return im if rounded else im.convert('RGB')   # 홈 화면 아이콘은 투명 없이

for n in (180, 192, 512): icon(n).save(f'{out}/icon-{n}.png', optimize=True)
import os
icon(192, rounded=True).save(os.path.join(out, '..', 'logo.png'), optimize=True)
