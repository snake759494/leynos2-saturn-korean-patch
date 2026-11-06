import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import build
STEPS=['dialog','story','mission','help','backup','bkspr','setting','ending','demo','end1','setspr']
im=build.cdimg.Image(build.ORIG); ents=im.dir_entries()
for st in (sys.argv[1:] or STEPS): getattr(build,'build_'+st)(im,ents)
im.save(build.OUT)
