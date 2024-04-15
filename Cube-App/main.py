import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        root.withdraw()
        show_graph_screen(file_path)

def show_graph_screen(file_path):
    graph_screen = tk.Tk()
    graph_screen.title("Graph with Sliders and Text Fields")
    frame = ttk.Frame(graph_screen)
    frame.grid(row=0, column=0, padx=10, pady=10)
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    center_frame = ttk.Frame(graph_screen)
    center_frame.grid(row=1, column=0, padx=10, pady=10)
    center_frame.columnconfigure(0, weight=1)

    def update_plot(*args):
        Zfar_value = float(Zfar_slider.get())
        Znear_value = float(Znear_slider.get())
        dX_value = float(dX_slider.get())
        dY_value = float(dY_slider.get())
        camx_value = float(camx_slider.get())
        camy_value = float(camy_slider.get())
        angle = np.radians(float(XY_slider.get()))
        K1_value = float(K1_slider.get())
        Zrange = Zfar_value - Znear_value
        dots_center = np.array([0.1, 0.1])
        cos_val = np.cos(angle)
        sin_val = np.sin(angle)
        if Zrange == 0:
            Zrange = 1
        P = np.array(
            [[cos_val, -sin_val, dX_value, 0], [sin_val, cos_val, dY_value, 0], [0, 0, -Zfar_value / Zrange, Znear_value * Zfar_value / Zrange],
             [0, 0, 1, 0]])
        Cam = np.array([[camx_value, 0, 0, 0], [0, camy_value, 0, 0], [0, 0, 1, 0]])
        dots = []
        for i in range(object.shape[0]):
            f = Cam @ P @ object[i, :]
            if f[2] == 0:
                dots.append(f)
                continue
            dots.append(f / f[2])
        dots = np.array(dots)
        r = (dots[:, :2] - dots_center) ** 2
        f1 = (r).sum(axis=1)
        f2 = (r ** 2).sum(axis=1)
        K2 = 0.0
        mask = np.expand_dims(K1_value * f1 + K2 * f2, axis=-1)
        dots_new = (dots[:, :2]) + (dots[:, :2] - dots_center) * mask
        ax.clear()
        ax.plot(dots_new[:, 0], dots_new[:, 1], '-D')
        canvas.draw()

    def apply_values():
        values = {
            XY_slider: XY_entry,
            Zfar_slider: Zfar_entry,
            Znear_slider: Znear_entry,
            dX_slider: dX_entry,
            dY_slider: dY_entry,
            camx_slider: camx_entry,
            camy_slider: camy_entry,
            K1_slider: K1_entry
        }
        for slider, entry in values.items():
            value = float(entry.get())
            slider.set(value)
        update_plot()

    def reset_values():
        entries = [XY_entry, Zfar_entry, Znear_entry, dX_entry, dY_entry, camx_entry, camy_entry, K1_entry]
        default_values = ["0.0", "-10.0", "-3.0", "-0.2", "-0.5", "1.0", "1.0", "1.0"]
        for entry, default_value in zip(entries, default_values):
            entry.delete(0, tk.END)
            entry.insert(0, default_value)
        apply_values()

    def update_from_entry(entry, slider):
        value = float(entry.get())
        slider.set(value)
        update_plot()

    def update_from_slider(slider, entry):
        value = slider.get()
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        update_plot()

    def select_all(event):
        event.widget.icursor(0)
        event.widget.select_range(0, 'end')

    def create_label_slider_entry(name, default_value, from_, to, row):
        label = ttk.Label(center_frame, text=name)
        label.grid(row=row, column=0, padx=10, pady=5)
        slider = ttk.Scale(center_frame, from_=from_, to=to, command=lambda x: update_from_slider(slider, entry))
        slider.grid(row=row, column=1, padx=10, pady=5)
        entry = ttk.Entry(center_frame)
        entry.grid(row=row, column=2, padx=10, pady=5)
        entry.insert(0, default_value)
        entry.bind("<FocusIn>", select_all)
        slider.bind("<ButtonRelease-1>", lambda event: update_from_entry(entry, slider))
        entry.bind("<Return>", lambda event: update_from_entry(entry, slider))
        return label, slider, entry

    object = []
    with open(file_path, 'r') as f:
        for s in f:
            s += ' 1'
            object.append(s.split())
        object = np.array(object).astype(float)

    row = 0
    XY_label, XY_slider, XY_entry = create_label_slider_entry(name="XY Plane Rotations:", default_value="0.0", from_=-180, to=180, row=row)
    Zfar_label, Zfar_slider, Zfar_entry = create_label_slider_entry(name="Zfar:", default_value="-10.0", from_=-10, to=10, row=row + 1)
    Znear_label, Znear_slider, Znear_entry = create_label_slider_entry("Znear:", default_value="-3.0", from_=-10, to=10, row=row + 2)
    dX_label, dX_slider, dX_entry = create_label_slider_entry("dX:", default_value="-0.2", from_=-10, to=10, row=row + 3)
    dY_label, dY_slider, dY_entry = create_label_slider_entry("dY:", default_value="-0.5", from_=-10, to=10, row=row + 4)
    camx_label, camx_slider, camx_entry = create_label_slider_entry("cam x:", default_value="1.0", from_=-10, to=10, row=row + 5)
    camy_label, camy_slider, camy_entry = create_label_slider_entry("cam y:", default_value="1.0", from_=-10, to=10, row=row + 6)
    K1_label, K1_slider, K1_entry = create_label_slider_entry("K1:", default_value="1.0", from_=-10, to=10, row=row + 7)
    apply_values()
    apply_button = ttk.Button(graph_screen, text="Apply", command=apply_values)
    apply_button.grid(row=row + 8, column=0, padx=10, pady=5)
    reset_button = ttk.Button(graph_screen, text="Reset", command=reset_values)
    reset_button.grid(row=row + 9, column=0, padx=10, pady=5)
    update_plot()
    graph_screen.mainloop()

root = tk.Tk()
root.title("File Selection")
root.geometry("400x300")

open_button = tk.Button(root, text="Open File", command=open_file_dialog)
open_button.pack(pady=(root.winfo_reqheight() - open_button.winfo_reqheight()) / 2)

root.mainloop()
