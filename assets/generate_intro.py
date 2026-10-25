#!/usr/bin/env python3
"""Build the Schedule Updater README hero GIF and static preview.

A deterministic, locally rendered visual asset. The generator has no network,
GitHub, credential, or calendar access. Requires Pillow and FFmpeg for GIF output.
"""
from __future__ import annotations
import argparse, math, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 400
FPS, FRAMES = 12, 60
NAVY = (7, 13, 29); NAVY2 = (10, 20, 40)
WHITE = (242, 247, 255); MUTED = (162, 180, 206)
CYAN = (65, 219, 255); BLUE = (79, 139, 255)
VIOLET = (180, 125, 255); TEAL = (65, 226, 192)
GREEN = (85, 232, 172); LINE = (42, 62, 96)
FONT_CANDIDATES = {
 'regular': ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'],
 'bold': ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'],
 'mono': ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf','/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf'],
 'mono_bold': ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf'],
}

def font(kind, size):
    for p in FONT_CANDIDATES[kind]:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def mix(a,b,t): return tuple(round(x+(y-x)*t) for x,y in zip(a,b))
def rect(d, box, radius, fill, outline=None, width=1):
    d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)
def glow_circle(img, xy, color, radius=7, blur=12, alpha=110):
    layer=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    x,y=xy; d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*color,alpha))
    layer=layer.filter(ImageFilter.GaussianBlur(blur)); img.alpha_composite(layer)

def static_background():
    im=Image.new('RGB',(W,H)); p=im.load()
    for y in range(H):
        t=y/(H-1); c=mix(NAVY,(4,8,19),t)
        for x in range(W): p[x,y]=c
    im=im.convert('RGBA'); d=ImageDraw.Draw(im)
    for x in range(26,W,32):
        for y in range(18,H,32): d.ellipse((x,y,x+1,y+1),fill=(39,72,115,72))
    halo=Image.new('RGBA',(W,H),(0,0,0,0)); hd=ImageDraw.Draw(halo)
    hd.ellipse((40,-90,460,160),fill=(0,145,255,22))
    hd.ellipse((790,80,1260,470),fill=(65,80,230,14))
    halo=halo.filter(ImageFilter.GaussianBlur(58)); im.alpha_composite(halo)
    return im

BG=static_background()

def render(t):
    im=BG.copy(); d=ImageDraw.Draw(im)
    # Header icon
    icon_box=(38,28,98,88)
    halo=Image.new('RGBA',(W,H),(0,0,0,0)); hd=ImageDraw.Draw(halo)
    hd.rounded_rectangle(icon_box,radius=16,fill=(0,190,255,25),outline=(*CYAN,150),width=2)
    halo=halo.filter(ImageFilter.GaussianBlur(12)); im.alpha_composite(halo); d=ImageDraw.Draw(im)
    rect(d,icon_box,16,(9,25,48,255),(*CYAN,190),2)
    rect(d,(48,41,88,77),7,(9,18,36,255),(*BLUE,240),2)
    rect(d,(48,41,88,52),4,(*CYAN,240))
    for x in (58,78): rect(d,(x,34,x+4,45),2,(209,247,255,255))
    for r in range(2):
        for c in range(4):
            x=54+c*8; y=59+r*8
            col=TEAL if (r,c)==(0,2) else (82,116,159)
            d.rounded_rectangle((x,y,x+4,y+4),radius=1,fill=col)
    # Main identity
    d.text((119,27),'SCHEDULE',font=font('bold',32),fill=WHITE)
    d.text((119,61),'UPDATER',font=font('bold',32),fill=CYAN)
    d.text((121,101),'A safer path from timetable to Google Calendar',font=font('regular',15),fill=MUTED)
    rect(d,(438,33,515,61),14,(12,31,57,255),(*CYAN,150),1)
    d.text((454,40),'v2.1.0',font=font('mono_bold',11),fill=CYAN)
    d.text((120,126),'EXTRACT ACCURATELY     ·     REVIEW AMBIGUITY     ·     PROTECT EXISTING EVENTS',font=font('mono_bold',9),fill=(114,154,192))
    # Right header promise, no fake live status
    rect(d,(852,34,1162,94),15,(10,22,42,232),(54,87,131,180),1)
    d.ellipse((870,51,880,61),fill=GREEN)
    d.text((893,46),'SAFETY-FIRST WORKFLOW',font=font('mono_bold',12),fill=WHITE)
    d.text((893,68),'Preview  /  Reconcile  /  Verify',font=font('regular',12),fill=MUTED)
    # Periodic header sweep
    center=42+1116*((1-math.cos(2*math.pi*t))/2)
    g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
    gd.line((max(42,center-70),151,min(1158,center+70),151),fill=(*CYAN,180),width=2)
    g=g.filter(ImageFilter.GaussianBlur(7)); im.alpha_composite(g); d=ImageDraw.Draw(im)
    d.line((40,151,1160,151),fill=(36,55,85,230),width=1)
    d.line((max(40,center-40),151,min(1160,center+40),151),fill=(*CYAN,170),width=1)
    # Readable workflow cards
    margin=36; gap=16; cw=(W-2*margin-3*gap)//4; top=173; bottom=333
    stages=[
      ('01','INGEST',CYAN,'PDF  ·  Images  ·  DOCX','HTML  ·  Markdown  ·  TXT','Source-aware extraction'),
      ('02','VALIDATE',VIOLET,'Dates  ·  Times  ·  Zones','Recurrence  ·  Ambiguity','Never guess missing details'),
      ('03','RECONCILE',TEAL,'Preview changes first','Detect duplicates & conflicts','No silent event deletion'),
      ('04','SAFE DISPATCH',BLUE,'Authorized host connector','Preserve unrelated fields','Read back before state commit'),
    ]
    xs=[]
    for i,(num,title,col,line1,line2,guard) in enumerate(stages):
        x=margin+i*(cw+gap); x2=x+cw; xs.append((x,x2)); pulse=(.5+.5*math.sin(2*math.pi*(t-i*.25)))
        rect(d,(x,top,x2,bottom),14,(10,20,40,244),(*col,int(100+65*pulse)),1)
        rect(d,(x+1,top+1,x2-1,top+4),2,(*col,int(150+80*pulse)))
        d.text((x+16,top+16),f'STAGE {num}',font=font('mono_bold',10),fill=col)
        d.text((x+16,top+38),title,font=font('bold',17),fill=WHITE)
        d.line((x+16,top+65,x2-16,top+65),fill=(36,56,86,255),width=1)
        bx=x+17; by=top+82
        rect(d,(bx,by,bx+38,by+38),10,(14,31,54,255),(*col,150),1)
        if i==0:
            rect(d,(bx+12,by+6,bx+26,by+31),3,(*col,235))
            for yy in (by+13,by+18,by+23): d.line((bx+16,yy,bx+23,yy),fill=(8,20,39,255),width=1)
        elif i==1:
            d.ellipse((bx+9,by+9,bx+29,by+29),outline=(*col,255),width=2)
            d.line((bx+19,by+12,bx+19,by+20,bx+25,by+23),fill=(*col,255),width=2)
        elif i==2:
            d.arc((bx+8,by+8,bx+30,by+30),30,300,fill=(*col,255),width=2)
            d.polygon(((bx+27,by+8),(bx+31,by+17),(bx+22,by+15)),fill=(*col,255))
        else:
            pts=[(bx+19,by+5),(bx+29,by+10),(bx+27,by+25),(bx+19,by+32),(bx+11,by+25),(bx+9,by+10)]
            d.polygon(pts,fill=(13,42,54,255),outline=(*col,255))
            d.line((bx+13,by+19,bx+18,by+24,bx+26,by+14),fill=(*col,255),width=2)
        d.text((bx+50,by+3),line1,font=font('bold',11),fill=(223,234,247))
        d.text((bx+50,by+21),line2,font=font('regular',10),fill=MUTED)
        rect(d,(x+14,top+130,x2-14,top+149),9,(12,29,44,255),(*col,90),1)
        d.ellipse((x+23,top+136,x+30,top+143),fill=col)
        d.text((x+38,top+134),guard,font=font('bold',9),fill=WHITE)
        a=int(110+145*pulse)
        d.ellipse((x2-25,top+18,x2-17,top+26),fill=(*col,a))
    # Periodic connector beads
    for i in range(3):
        x1=xs[i][1]; x2=xs[i+1][0]; yy=253
        d.line((x1,yy,x2,yy),fill=(50,79,116,255),width=2)
        p=(1-math.cos(2*math.pi*(t*0.75+i*0.19)))/2; bx=x1+(x2-x1)*p
        glow_circle(im,(bx,yy),stages[i][2],radius=5,blur=5,alpha=140)
        d=ImageDraw.Draw(im); d.ellipse((bx-2,yy-2,bx+2,yy+2),fill=(244,252,255,255))
    # Bottom process strip
    d=ImageDraw.Draw(im)
    d.line((66,365,1134,365),fill=(36,55,85,255),width=1)
    nav=[('01','INPUT'),('02','EXTRACT'),('03','VALIDATE'),('04','PREVIEW'),('05','RECONCILE'),('06','VERIFY')]
    nx=[78,284,490,696,902,1108]
    for i,((n,label),x) in enumerate(zip(nav,nx)):
        col=stages[min(i//2,3)][2]
        d.ellipse((x-5,360,x+5,370),fill=(9,19,37,255),outline=(*col,230),width=1)
        d.text((x+12,355),n,font=font('mono_bold',9),fill=col)
        d.text((x+35,355),label,font=font('mono_bold',9),fill=MUTED)
    # Runner oscillates on a closed path to avoid a jump at loop boundary
    rx=600-534*math.cos(2*math.pi*t)
    glow_circle(im,(rx,365),CYAN,radius=6,blur=7,alpha=130)
    d=ImageDraw.Draw(im); d.ellipse((rx-2,363,rx+2,367),fill=(244,252,255,255))
    return im.convert('RGB')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-gif',default='assets/schedule-updater-intro.gif')
    ap.add_argument('--output-preview',default='assets/schedule-updater-preview.png')
    ap.add_argument('--fps',type=int,default=FPS); ap.add_argument('--frames',type=int,default=FRAMES)
    args=ap.parse_args()
    if not 1<=args.fps<=24 or not 12<=args.frames<=240: ap.error('fps must be 1–24 and frames 12–240')
    gif=Path(args.output_gif); png=Path(args.output_preview)
    gif.parent.mkdir(parents=True,exist_ok=True); png.parent.mkdir(parents=True,exist_ok=True)
    render(.25).save(png,optimize=True)
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg: raise SystemExit('FFmpeg is required to generate the animated GIF')
    with tempfile.TemporaryDirectory(prefix='schedule-updater-hero-') as td:
        td=Path(td)
        for i in range(args.frames): render(i/args.frames).save(td/f'frame_{i:03d}.png',optimize=True)
        cmd=[ffmpeg,'-v','error','-y','-framerate',str(args.fps),'-i',str(td/'frame_%03d.png'),'-filter_complex','[0:v] split [a][b]; [a] palettegen=max_colors=96:stats_mode=diff [p]; [b][p] paletteuse=dither=none','-loop','0',str(gif)]
        res=subprocess.run(cmd,capture_output=True,text=True)
        if res.returncode: raise RuntimeError(res.stderr)
    print(f'GIF bytes={gif.stat().st_size}; PNG bytes={png.stat().st_size}; {W}x{H}; {args.frames} frames; {args.fps} fps; {args.frames/args.fps:.3f}s')
if __name__=='__main__': main()
