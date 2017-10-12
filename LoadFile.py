import os,sys
from PIL import Image
import numpy as np
from .ExtendType import *
from .GraphWindow import Graph

def load(name):
    try:
        if os.path.isfile(name):
            path,ext=os.path.splitext(name)
            return dic[ext](name)
    except Exception:
        sys.stderr.write('Error: Cannot load.\n')

def save(name,nameAs):
    data=load(name)
    data.Save(nameAs)

def __loadNpz(name):
    nam,ext=os.path.splitext(os.path.basename(name))
    return Wave(name)

def __loadStr(name):
    nam,ext=os.path.splitext(os.path.basename(name))
    return String(name)

def __loadVal(name):
    nam,ext=os.path.splitext(os.path.basename(name))
    return Variable(name)

def __loadDic(name):
    nam,ext=os.path.splitext(os.path.basename(name))
    return Dict(name)

def __loadGraph(name):
    nam,ext=os.path.splitext(os.path.basename(name))
    return Graph(name)

def __loadImage(name):
    im=Image.open(name)
    w=Wave()
    w.data=np.array(im)
    return w

def addFileLoader(type, func):
    dic[type]=func

def __loadPxt(name):
    import igor.packed, igor.igorpy
    nam,ext=os.path.splitext(os.path.basename(name))
    (rec,data)=igor.packed.load(name)
    wav=igor.igorpy.Wave(data['root'][nam.encode('utf-8')])
    w=Wave()
    w.data=wav.data
    w.x=wav.axis[0]
    w.note=wav.notes.decode()
    if w.data.ndim>=2:
        w.y=wav.axis[1]
    if w.data.ndim>=3:
        w.z=wav.axis[2]
    return w

dic=dict(zip(['.npz','.str','.val','.dic','.pxt','.grf','.tif','.jpg','.png'],[__loadNpz,__loadStr,__loadVal,__loadDic,__loadPxt,__loadGraph,__loadImage,__loadImage,__loadImage]))
