"""PETG coupon: left-to-right bores 25.1/25.2/25.3/25.4; spigots 24.7/24.8/24.9/25.0 mm."""
from pathlib import Path
from build123d import *
from style import *
HERE=Path(__file__).resolve().parent
s=extrude(RectangleRounded(136,74,R_OUTER),amount=4)
for x,bore,pin in zip((-51,-17,17,51),(25.1,25.2,25.3,25.4),(24.7,24.8,24.9,25.0)):
    s-=Pos(x,-18,0)*Cylinder(bore/2,4,align=(Align.CENTER,Align.CENTER,Align.MIN))
    s+=Pos(x,18,4)*Cylinder(pin/2,5,align=(Align.CENTER,Align.CENTER,Align.MIN))
    s-=Pos(x,18,0)*Cylinder(7,9,align=(Align.CENTER,Align.CENTER,Align.MIN))
export_step(s,str(HERE/'yaw-fits-coupon.step'))
export_stl(s,str(HERE/'yaw-fits-coupon.stl'),tolerance=0.08,angular_tolerance=0.15)
