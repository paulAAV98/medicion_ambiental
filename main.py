import sys
import tkinter as tk
from gui.app import AplicacionGUI


def main():
    root = tk.Tk()
    app = AplicacionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()