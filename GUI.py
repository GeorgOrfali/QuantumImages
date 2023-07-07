import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from QuantumImageTest import *


class GUI(tk.Frame):
    QimageTest = QuantumImageTest()

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.single = tk.Button(self, text="Single Test Cases", command=self.single_testCasePage)
        self.single.place(x=0, y=10)

        self.bulk = tk.Button(self, text="Bulk Test Cases", command=self.bulk_testCasePage)
        self.bulk.place(x=160, y=10)

    def bulk_testCasePage(self):
        self.bulk.destroy()
        self.single.destroy()
        normal = ("Helvetica", 16)
        widthBoxLabel = tk.Label(self, text="Width:")
        self.widthBox1 = tk.Spinbox(self, from_=2, to=1080, width=10)
        widthBoxLabel.configure(font=normal)
        widthBoxLabel.place(x=10, y=10)
        self.widthBox1.place(x=80, y=15)

        heightBoxLabel = tk.Label(self, text="Height:")
        self.heightBox1 = tk.Spinbox(self, from_=2, to=1080, width=10)
        heightBoxLabel.configure(font=normal)
        heightBoxLabel.place(x=160, y=10)
        self.heightBox1.place(x=230, y=15)

        ColorBoxLabel = tk.Label(self, text="Color:")
        self.ColorBox1 = tk.Spinbox(self, from_=2, to=24, width=10)
        ColorBoxLabel.configure(font=normal)
        ColorBoxLabel.place(x=310, y=10)
        self.ColorBox1.place(x=380, y=15)

        CasesLabel = tk.Label(self, text="Cases:")
        self.CasesBox1 = tk.Spinbox(self, from_=2, to=24, width=10)
        CasesLabel.configure(font=normal)
        CasesLabel.place(x=460, y=10)
        self.CasesBox1.place(x=530, y=15)

        self.ssSimulation = tk.Button(self, text="Start Simulation!",
                                      command=self.bulCases)
        self.ssSimulation.place(x=640, y=10)

    def bulCases(self):
        result = self.QimageTest.BulkTestCases(int(self.widthBox1.get()),
                                      int(self.heightBox1.get()),
                                      int(self.ColorBox1.get()),
                                      int(self.CasesBox1.get()))
        print(result)
    def single_testCasePage(self):
        self.bulk.destroy()
        self.single.destroy()
        normal = ("Helvetica", 16)
        array = ("Helvetica", 20, "bold")
        widthBoxLabel = tk.Label(self, text="Width:")
        self.widthBox = tk.Spinbox(self, from_=2, to=16, width=10)
        widthBoxLabel.configure(font=normal)
        widthBoxLabel.place(x=10, y=10)
        self.widthBox.place(x=80, y=15)

        heightBoxLabel = tk.Label(self, text="Height:")
        self.heightBox = tk.Spinbox(self, from_=2, to=16, width=10)
        heightBoxLabel.configure(font=normal)
        heightBoxLabel.place(x=160, y=10)
        self.heightBox.place(x=230, y=15)

        ColorBoxLabel = tk.Label(self, text="Color:")
        self.ColorBox = tk.Spinbox(self, from_=2, to=24, width=10)
        ColorBoxLabel.configure(font=normal)
        ColorBoxLabel.place(x=310, y=10)
        self.ColorBox.place(x=380, y=15)

        self.gImageButton = tk.Button(self, text="Generate Image", command=self.generateImage)
        self.gImageButton.place(x=480, y=10)

        self.sSimulation = tk.Button(self, text="Start Simulation!", command=self.startSimulation)
        self.sSimulation.place(x=640, y=10)

        OGImageLabel = tk.Label(self, text="Original Image:")
        OGImageLabel.configure(font=normal)
        OGImageLabel.place(x=10, y=60)

        self.OGImage = tk.Label(self, text=self.QimageTest.getImage())
        self.OGImage.configure(font=array)
        self.OGImage.place(x=10, y=100)

        QGImageLabel = tk.Label(self, text="Quantum Image:")
        QGImageLabel.configure(font=normal)
        QGImageLabel.place(x=400, y=60)

        self.QGImage = tk.Label(self, text="")
        self.QGImage.configure(font=array)
        self.QGImage.place(x=400, y=100)

        QKGImageLabel = tk.Label(self, text="Quantum Key Image:")
        QKGImageLabel.configure(font=normal)
        QKGImageLabel.place(x=10, y=360)

        self.QKGImage = tk.Label(self, text="")
        self.QKGImage.configure(font=array)
        self.QKGImage.place(x=10, y=400)

        EQGImageLabel = tk.Label(self, text="Encrypted Quantum Image:")
        EQGImageLabel.configure(font=normal)
        EQGImageLabel.place(x=400, y=360)

        self.EQGImage = tk.Label(self, text="")
        self.EQGImage.configure(font=array)
        self.EQGImage.place(x=400, y=400)

    def startSimulation(self):
        self.QimageTest.TestCasesWithArrayOutput()
        self.QGImage.configure(text=self.QimageTest.getQuantumImage(self.QimageTest.qImage.qImage,
                                                                    self.QimageTest.qImageArray))

        self.QKGImage.configure(text=self.QimageTest.getQuantumImage(self.QimageTest.qImage.qKeyImage,
                                                                     self.QimageTest.qKeyImageArray))

        self.EQGImage.configure(text=self.QimageTest.getQuantumImage(self.QimageTest.qImage.qImage,
                                                                     self.QimageTest.qEncryptedImageArray))

        print(self.QimageTest.qImage.circuit.draw("text"))

    def generateImage(self):
        self.QimageTest.image = self.QimageTest.generate_random_image(int(self.widthBox.get()),
                                                                      int(self.heightBox.get()),
                                                                      int(self.ColorBox.get()))
        self.OGImage.configure(text=self.QimageTest.getImage())
