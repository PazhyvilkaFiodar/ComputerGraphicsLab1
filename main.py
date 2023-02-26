import dataclasses
import tkinter as tk
from tkinter import messagebox
from collections.abc import *
from tkinter.colorchooser import askcolor
import colorsys


def initialize_window() -> tk.Tk:
    window = tk.Tk()
    window.title("XYZ-LAB-HLS converter")
    window.geometry("600x500")
    window.resizable(False, False)
    return window


def initialize_label(window: tk.Tk, text: str, x: int, y: int, font_size: int) -> tk.Label:
    label = tk.Label(window, text=text)
    label.place(x=x, y=y)
    label.config(font=("Arial", font_size))
    return label


def initialize_entry(window: tk.Tk, x: int, y: int, width: int) -> tk.Entry:
    field = tk.Entry(window, width=width)
    field.place(x=x, y=y)
    return field


def initialize_slider(window: tk.Tk, x: int, y: int, min_value: int, max_value: int, show_value: bool = False) -> tk.Scale:
    slider = tk.Scale(window, from_=min_value, to=max_value, orient=tk.HORIZONTAL, length=120)
    slider.place(x=x, y=y)
    slider.config(showvalue=show_value)
    return slider


def initialize_button(window: tk.Tk, x: int, y: int, text: str, command: Callable[[], None]) -> tk.Button:
    button = tk.Button(window, text=text, command=command)
    button.place(x=x, y=y)
    return button


@dataclasses.dataclass
class RGBModel:
    red: int
    green: int
    blue: int


@dataclasses.dataclass
class XYZModel:
    label_x: tk.Label
    field_x: tk.Entry
    label_y: tk.Label
    field_y: tk.Entry
    label_z: tk.Label
    entry_z: tk.Entry


@dataclasses.dataclass
class LABModel:
    label_l: tk.Label
    field_l: tk.Entry
    label_a: tk.Label
    field_a: tk.Entry
    label_b: tk.Label
    entry_b: tk.Entry


@dataclasses.dataclass
class HLSModel:
    label_h: tk.Label
    field_h: tk.Entry
    label_l: tk.Label
    field_l: tk.Entry
    label_s: tk.Label
    entry_s: tk.Entry


def multiply_matrices(a: list[float | list[float]], b: list[float | list[float]]) -> list[float | list[float]]:
    result = [[0 for _ in range(len(b[0]))] for __ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += a[i][k] * b[k][j]

    return result


def convert_rgbn_to_rgb_coordinate(x: float) -> float:
    if x >= 0.0031308:
        return 1.055 * x ** (1 / 2.4) - 0.055

    return 12.92 * x


def convert_xyz_to_rgb(x: float, y: float, z: float) -> RGBModel:
    matrix_converter = [
        [3.2404542, -1.5371385, -0.4985314],
        [-0.9692660, 1.8760108, 0.0415560],
        [0.0556434, -0.2040259, 1.0572252]
    ]

    vector_xyz = [[x / 100], [y / 100], [z / 100]]
    red_n, green_n, blue_n = multiply_matrices(matrix_converter, vector_xyz)
    r = int(convert_rgbn_to_rgb_coordinate(red_n[0]) * 255)
    g = int(convert_rgbn_to_rgb_coordinate(green_n[0]) * 255)
    b = int(convert_rgbn_to_rgb_coordinate(blue_n[0]) * 255)
    return RGBModel(max(min(255, r), 0), max(min(255, g), 0), max(min(255, b), 0))


def convert_rgb_to_rgbn_coordinate(x: float) -> float:
    if x >= 0.04045:
        return ((x + 0.055) / 1.055) ** 2.4

    return x / 12.92


def convert_rgb_to_xyz(rgb: RGBModel) -> tuple[float, float, float]:
    matrix_converter = [
        [0.412453, 0.357580, 0.180423],
        [0.212671, 0.715160, 0.072169],
        [0.019334, 0.119193, 0.950227]
    ]

    vector_to_convert = [
        [convert_rgb_to_rgbn_coordinate(rgb.red / 255) * 100],
        [convert_rgb_to_rgbn_coordinate(rgb.green / 255) * 100],
        [convert_rgb_to_rgbn_coordinate(rgb.blue / 255) * 100]
    ]

    res = multiply_matrices(matrix_converter, vector_to_convert)
    return res[0][0], res[1][0], res[2][0]


def convert_lab_to_xyz_coordinate(x: float) -> float:
    if x ** 3 >= 0.008856:
        return x ** 3
    return (x - 16 / 116) / 7.787


def convert_lab_to_rgb(l: float, a: float, b: float) -> RGBModel:
    x_white = 95.047
    y_white = 100
    z_white = 108.833
    x = convert_lab_to_xyz_coordinate((l + 16) / 116) * x_white
    y = convert_lab_to_xyz_coordinate(a / 500 + (l + 16) / 116) * y_white
    z = convert_lab_to_xyz_coordinate((l + 16) / 116 - b / 200) * z_white
    return convert_xyz_to_rgb(x, y, z)


def convert_xyz_to_lab_coordinate(x: float) -> float:
    if x >= 0.008856:
        return x ** (1 / 3)
    return 7.787 * x + 16 / 116


def convert_rgb_to_lab(rgb: RGBModel) -> tuple[float, float, float]:
    x, y, z = convert_rgb_to_xyz(rgb)
    x_white, y_white, z_white = 95.047, 100, 108.833
    l = 116 * convert_xyz_to_lab_coordinate(y / y_white) - 16
    a = 500 * (convert_xyz_to_lab_coordinate(x / x_white) - convert_xyz_to_lab_coordinate(y / y_white))
    b = 200 * (convert_xyz_to_lab_coordinate(y / y_white) - convert_xyz_to_lab_coordinate(z / z_white))
    return l, a, b


def convert_hls_to_rgb(h: float, l: float, s: float) -> RGBModel:
    h /= 360
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return RGBModel(int(r * 255), int(g * 255), int(b * 255))


def convert_rgb_to_hls(rgb: RGBModel) -> tuple[int, float, float]:
    r, g, b = rgb.red / 255, rgb.green / 255, rgb.blue / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return int(h * 360), l, s


def convert_rgb_to_str(rgb: RGBModel) -> str:
    return "#%02x%02x%02x" % (rgb.red, rgb.green, rgb.blue)


def fill_fields_by_rgb(rgb: RGBModel, xyz: XYZModel, lab: LABModel, hls: HLSModel) -> None:
    x, y, z = convert_rgb_to_xyz(rgb)
    xyz.field_x.delete(0, tk.END)
    xyz.field_x.insert(0, f"{x: .3f}")
    xyz.field_y.delete(0, tk.END)
    xyz.field_y.insert(0, f"{y: .3f}")
    xyz.entry_z.delete(0, tk.END)
    xyz.entry_z.insert(0, f"{z: .3f}")
    l, a, b = convert_rgb_to_lab(rgb)
    lab.field_l.delete(0, tk.END)
    lab.field_l.insert(0, f"{l: .3f}")
    lab.field_a.delete(0, tk.END)
    lab.field_a.insert(0, f"{a: .3f}")
    lab.entry_b.delete(0, tk.END)
    lab.entry_b.insert(0,  f"{b: .3f}")
    h, l, s = convert_rgb_to_hls(rgb)
    hls.field_h.delete(0, tk.END)
    hls.field_h.insert(0, f"{h: .3f}")
    hls.field_l.delete(0, tk.END)
    hls.field_l.insert(0, f"{l: .3f}")
    hls.entry_s.delete(0, tk.END)
    hls.entry_s.insert(0, f"{s: .3f}")


def ask_color(rgb: RGBModel, xyz: XYZModel, lab: LABModel, hls: HLSModel, color_label: tk.Label) -> None:
    messagebox.showwarning("Warning", "It could be some troubles due to floating point numbers in convertion")
    (rgb.red, rgb.green, rgb.blue), color = askcolor(title="Choose color")
    color_label.config(bg=color)
    fill_fields_by_rgb(rgb, xyz, lab, hls)


def press_enter_on_xyz(rgb: RGBModel, xyz: XYZModel, lab: LABModel, hls: HLSModel, color_label: tk.Label) -> None:
    messagebox.showwarning("Warning", "It could be some troubles due to floating point numbers in convertion")
    try:
        x, y, z = float(xyz.field_x.get()), float(xyz.field_y.get()), float(xyz.entry_z.get())
    except RuntimeError:
        messagebox.showerror("Invalid argument", "Invalid argument")
    rgb = convert_xyz_to_rgb(x, y, z)
    color_label.config(bg=convert_rgb_to_str(rgb))
    fill_fields_by_rgb(rgb, xyz, lab, hls)


def press_enter_on_lab(rgb: RGBModel, xyz: XYZModel, lab: LABModel, hls: HLSModel, color_label: tk.Label) -> None:
    messagebox.showwarning("Warning", "It could be some troubles due to floating point numbers in convertion")
    try:
        l, a, b = float(lab.field_l.get()), float(lab.field_a.get()), float(lab.entry_b.get())
    except RuntimeError:
        messagebox.showerror("Invalid argument", "Invalid argument")
    rgb = convert_xyz_to_rgb(l, a, b)
    color_label.config(bg=convert_rgb_to_str(rgb))
    fill_fields_by_rgb(rgb, xyz, lab, hls)


def press_enter_on_hls(rgb: RGBModel, xyz: XYZModel, lab: LABModel, hls: HLSModel, color_label: tk.Label) -> None:
    messagebox.showwarning("Warning", "It could be some troubles due to floating point numbers in convertion")
    try:
        h, l, s = float(hls.field_h.get()), float(hls.field_l.get()), float(hls.entry_s.get())
    except RuntimeError:
        messagebox.showerror("Invalid argument", "Invalid argument")
    rgb = convert_xyz_to_rgb(h, l, s)
    color_label.config(bg=convert_rgb_to_str(rgb))
    fill_fields_by_rgb(rgb, xyz, lab, hls)


def main() -> None:
    window = initialize_window()
    label_xyz = initialize_label(window, "XYZ", 100, 15, 20)
    xyz = XYZModel(initialize_label(window, "X", 50, 45, 16), initialize_entry(window, 70, 45, 10), 
                   initialize_label(window, "Y", 50, 105, 16), initialize_entry(window, 70, 105, 10),
                   initialize_label(window, "Z", 50, 165, 16), initialize_entry(window, 70, 165, 10))
    color_label = initialize_label(window, "", 50, 300, 15)
    rgb = RGBModel(0, 0, 0)
    color_label.config(bg=convert_rgb_to_str(rgb), width=55, height=10)
    label_lab = initialize_label(window, "LAB", 300, 15, 20)
    lab = LABModel(initialize_label(window, "L", 250, 45, 16), initialize_entry(window, 270, 45, 10),
                   initialize_label(window, "A", 250, 105, 16), initialize_entry(window, 270, 105, 10),
                   initialize_label(window, "B", 250, 165, 16), initialize_entry(window, 270, 165, 10))
    label_hls = initialize_label(window, "HLS", 500, 15, 20)
    hls = HLSModel(initialize_label(window, "H", 450, 45, 16), initialize_entry(window, 470, 45, 10),
                   initialize_label(window, "L", 450, 105, 16), initialize_entry(window, 470, 105, 10), 
                   initialize_label(window, "S", 450, 165, 16), initialize_entry(window, 470, 165, 10))
    fill_fields_by_rgb(rgb, xyz, lab, hls)
    button_dialog = initialize_button(window, 250, 250, "Choose color", 
                                      lambda: ask_color(rgb, xyz, lab, hls, color_label))
    xyz.field_x.bind("<Return>", lambda event: press_enter_on_xyz(rgb, xyz, lab, hls, color_label))
    xyz.field_y.bind("<Return>", lambda event: press_enter_on_xyz(rgb, xyz, lab, hls, color_label))
    xyz.entry_z.bind("<Return>", lambda event: press_enter_on_xyz(rgb, xyz, lab, hls, color_label))
    lab.field_l.bind("<Return>", lambda event: press_enter_on_lab(rgb, xyz, lab, hls, color_label))
    lab.field_a.bind("<Return>", lambda event: press_enter_on_lab(rgb, xyz, lab, hls, color_label))
    lab.entry_b.bind("<Return>", lambda event: press_enter_on_lab(rgb, xyz, lab, hls, color_label))
    hls.field_h.bind("<Return>", lambda event: press_enter_on_hls(rgb, xyz, lab, hls, color_label))
    hls.field_l.bind("<Return>", lambda event: press_enter_on_hls(rgb, xyz, lab, hls, color_label))
    hls.entry_s.bind("<Return>", lambda event: press_enter_on_hls(rgb, xyz, lab, hls, color_label))
    window.mainloop()


if __name__ == '__main__':
    main()
