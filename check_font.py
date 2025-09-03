from fontTools.ttLib import TTFont
import os

paths = [
r"C:\realfootballsim\static\fonts\mulish\mulish-400-regular.woff2",
r"C:\realfootballsim\static\fonts\mulish\mulish-400.woff2",
]

for p in paths:
    f = TTFont(p)
    os2 = f["OS/2"]
    name = f["name"]
    family    = name.getDebugName(1)
    subfamily = name.getDebugName(2)
    full      = name.getDebugName(4)
    ps        = name.getDebugName(6)
    print("==", os.path.basename(p))
    print("  usWeightClass:", os2.usWeightClass)   # ожидаем 400 для Regular
    print("  family:", family)
    print("  subfamily:", subfamily)               # ожидаем "Regular", не "ExtraLight"
    print("  PostScript:", ps)
