from app.elements.configmanager import ConfiManager

cfg_mgr = ConfiManager()

cfg = cfg_mgr.read_config()

c_dict = dict()

for section in cfg:
    print("C", section)
    print("CDFG", cfg[section])
    for key in cfg[section]:
        value = cfg[section][key]
        print("FINAL", key, cfg[section][key])
        c_dict[key] = value

print(cfg["API"]["key"])
cfg["API"]["key"] = "lel"

print(cfg["API"]["key"])

print("######")
print("cdict", c_dict)