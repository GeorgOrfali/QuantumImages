import tkinter as tk
import GUI as g

if __name__ == "__main__":
    root = tk.Tk()
    width = 1920
    height = 1280
    root.geometry(f"{width}x{height}")
    root.title("Quantum Image Simulation")
    g.GUI(root).pack(fill="both", expand=True)
    root.mainloop()
