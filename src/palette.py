PALETTE = {
    "Red": "#E53935", "Orange": "#FB8C00", "Yellow": "#FDD835",
    "Light green": "#7CB342", "Dark green": "#2E7D32",
    "Light blue": "#4FC3F7", "Dark blue": "#1E5AA8", "Purple": "#8E24AA",
    "Pink": "#F48FB1", "Brown": "#8D5524", "Grey": "#9E9E9E", "Black": "#212121",
}
ORDER = list(PALETTE)


def rgb(name):
    h = PALETTE[name].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
