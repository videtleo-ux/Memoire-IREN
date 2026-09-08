# -*- coding: utf-8 -*-
"""Exporte chaque slide en PNG via PowerPoint, pour contrôle visuel."""
import os, sys, glob
import win32com.client

ICI = os.path.dirname(os.path.abspath(__file__))
PPTX = os.path.join(os.path.dirname(os.path.dirname(ICI)), "Soutenance.pptx")
OUT = os.path.join(ICI, "apercu")
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*.png")):
    os.remove(f)
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(PPTX, WithWindow=False)
pres.Export(OUT, "PNG", 1600, 900)
pres.Close()
app.Quit()
print(sorted(os.listdir(OUT)))
