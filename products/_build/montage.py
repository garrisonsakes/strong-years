import sys, os
from common import snap
from PIL import Image
pdf=sys.argv[1]; pages=[int(x) for x in sys.argv[2].split(",")]; out=sys.argv[3]; res=int(sys.argv[4]) if len(sys.argv)>4 else 50
S='/tmp/claude-0/-home-claude/361bbfdb-b4e7-5ba8-9339-bc4d3afdbd31/scratchpad/snap'
fs=snap(pdf,pages,S,res=res)
ims=[Image.open(f) for f in fs]
w=max(i.size[0] for i in ims); h=max(i.size[1] for i in ims)
cols=3 if len(ims)>2 else len(ims); rows=(len(ims)+cols-1)//cols
m=Image.new('RGB',(w*cols,h*rows),'white')
for i,im in enumerate(ims): m.paste(im,((i%cols)*w,(i//cols)*h))
m.save(os.path.join(S,out)); print(os.path.join(S,out), m.size)
