from pathlib import Path
exec(Path(__file__).with_name('diagnostic_media.py').read_text(encoding='utf8').split('# Exact source frame indices')[0])
for view in ['teaching','overhead','side_oblique']:
    sheet=Image.new('RGB',(1440,750),'#eeeade');draw=ImageDraw.Draw(sheet)
    for col,idx in enumerate([223,229,233]):
        for row,(label,folder) in enumerate([('R1',C1),('R2',C2)]):
            im=frame(folder,view,idx);x=col*480;y=row*375;sheet.paste(im.crop((610,95,1090,445)),(x,y+25));draw.text((x+4,y+3),f'{label} {view} t={idx/60:.3f}s',font=font,fill='black')
    sheet.save(P/f'late_overlap_{view}.jpg',quality=97)
