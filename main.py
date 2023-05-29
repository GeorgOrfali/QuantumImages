import tkinter as tk
import GUI as g

if __name__ == "__main__":
    root = tk.Tk()
    width = 1280
    height = 720
    root.geometry(f"{width}x{height}")
    root.title("Quantum Image Simulation")
    g.GUI(root).pack(fill="both", expand=True)
    root.mainloop()
