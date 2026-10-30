"""Write STLs for the fit-test coupons (they are not in the assembly, so `export` skips them) and add them to
the top of print_list.csv: they print first."""
import csv
from pathlib import Path

from build123d import export_stl, import_step

V1 = Path(__file__).parent
P = V1 / "printed"
COUPONS = ("coupon-fits", "coupon-yaw")
for n in COUPONS:
    export_stl(import_step(str(P / f"{n}.step")), str(P / f"{n}.stl"), tolerance=0.01, angular_tolerance=0.1)
    print("wrote", P / f"{n}.stl")

pl = V1 / "print_list.csv"
rows = list(csv.reader(pl.open()))
head, body = rows[0], [r for r in rows[1:] if r and r[0] not in COUPONS]
grams = {"coupon-fits": "45", "coupon-yaw": "60"}          # rough, from the coupon volumes
new = [[n, "1", "PLA (same as the parts)", "as modelled", "20%", grams[n], f"printed/{n}.stl"] for n in COUPONS]
with pl.open("w", newline="") as f:
    csv.writer(f).writerows([head] + new + body)
print("print_list.csv: coupons added first")
