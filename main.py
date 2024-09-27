import tkinter as tk
import ttkbootstrap as ttk
from Simulation import GuiClassic, GuiModern


def classicGui():
    root = tk.Tk()
    width = 1280
    height = 720
    root.geometry(f"{width}x{height}")
    root.title("Quantum Image Simulation")
    GuiClassic.GUI(root).pack(fill="both", expand=True)
    root.mainloop()


def modernGui():
    root = ttk.Window(title="Quantum Distribution Simulation", themename="vapor", size=[1920, 1080])
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=30)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=20)
    GuiModern.GuiModern(root)
    root.mainloop()


if __name__ == "__main__":
    #classicGui()
    modernGui()