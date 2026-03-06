import json
import os

base = os.path.dirname(__file__)
path = os.path.join(base, "sample-data.json")

with open(path) as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print("{:<50} {:<20} {:<8} {:<6}".format("DN", "Description", "Speed", "MTU"))
print("-" * 80)

for item in data["imdata"]:
    attrs = item["l1PhysIf"]["attributes"]

    dn = attrs.get("dn", "")
    descr = attrs.get("descr", "")
    speed = attrs.get("speed", "")
    mtu = attrs.get("mtu", "")

    print("{:<50} {:<20} {:<8} {:<6}".format(dn, descr, speed, mtu))