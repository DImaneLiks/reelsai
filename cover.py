# -*- coding: utf-8 -*-
"""Обложка «Сен-Жермен» -> ../История 05 - обложка.png"""
import os, sys, importlib.util
from PIL import ImageDraw
sys.path.insert(0, "/Users/dmitrijpostnov/Documents/reels/ep1_build")
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v_render", os.path.join(HERE, "render.py"))
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
T = 1.0
im, d = V.new((30, 22, 20))
V.glow(im, 540, 900, 700, 0.95, (150, 110, 60))
V.sgbust(im, 540, 900, 230, T, glow=0.6, look=0.0)
im = V.grade(im, 0)
d = ImageDraw.Draw(im, "RGBA")
V.tag(d, "ТАЙНЫ ИСТОРИИ · XVIII ВЕК")
V.text_c(d, (540, 250), "ОН НЕ СТАРЕЛ", V.F(108, 9), V.WHITE, stroke=9, sfill=(12, 10, 10))
V.text_c(d, (540, 375), "50 ЛЕТ", V.F(130, 9), V.RED, stroke=10, sfill=(12, 10, 10))
V.text_c(d, (540, 1700), "СЕН-ЖЕРМЕН", V.F(120, 9), V.YEL, stroke=10, sfill=(12, 10, 10))
im.save(os.path.join(os.path.dirname(HERE), "История 05 - обложка.png"))
print("ok")
