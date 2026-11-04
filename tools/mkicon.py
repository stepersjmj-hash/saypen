# 파비콘(28단위 SVG)과 같은 모양을 꽉 찬 정사각형 아이콘으로 그림
import sys
from PIL import Image, ImageDraw
out=sys.argv[1]
def icon(size):
    k=4; S=size*k; u=S/28
    im=Image.new('RGB',(S,S),'#2f6fed'); d=ImageDraw.Draw(im)
    def bar(x,y,w,h,c): d.rounded_rectangle([x*u,y*u,(x+w)*u,(y+h)*u],radius=w/2*u,fill=c)
    bar(7.5,9.5,3,9,'#ffffff'); bar(12.5,6,3,16,'#ffffff')
    bar(16.5,7.5,5,13,'#ffffff'); bar(17.5,8.5,3,11,'#16a34a')
    return im.resize((size,size),Image.LANCZOS)
for n in (180,192,512): icon(n).save(f'{out}/icon-{n}.png',optimize=True)
