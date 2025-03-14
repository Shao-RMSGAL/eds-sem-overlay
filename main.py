from PIL import Image, ImageTk
from tkinter import filedialog, PhotoImage
import tkinter as tk
import cv2
import csv
import pandas as pd
import numpy as np


class ScrollableFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.setup_scrolling()
        self.create_widgets()

    def setup_scrolling(self):
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)

        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Add the frame to the canvas
        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # Configure scrolling with mouse wheel
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        # These bindings allow scrolling with the mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Enter>", self._bound_to_mousewheel)
        self.canvas.bind("<Leave>", self._unbound_to_mousewheel)

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_widgets(self):

        # Create widgets
        cr_button = tk.Button(self.scrollable_frame)
        cr_button["text"] = "Select CR Image"
        cr_button["command"] = self.select_cr_image
        cr_button.pack(side="top")

        sem_button = tk.Button(self.scrollable_frame)
        sem_button["text"] = "Select SEM Image"
        sem_button["command"] = self.select_sem_image
        sem_button.pack(side="top")

        overlay_button = tk.Button(self.scrollable_frame)
        overlay_button["text"] = "Generate Overlay"
        overlay_button["command"] = self.generate_overlay
        overlay_button.pack(side="top")

        self.threshold_frame = tk.Frame(self.scrollable_frame)
        self.threshold_frame.pack(side="top")

        cr_threshold_label = tk.Label(self.threshold_frame)
        cr_threshold_label["text"] = "CR Threshold:"
        cr_threshold_label.pack(side="left")
        cr_threshold_slider = tk.Scale(
            self.threshold_frame, from_=0, to=255, orient="horizontal",
            command=self.update_cr_threshold)
        cr_threshold_slider.set(15)
        cr_threshold_slider.pack(side="left")
        sem_threshold_label = tk.Label(self.threshold_frame)
        sem_threshold_label["text"] = "SEM Threshold:"
        sem_threshold_label.pack(side="left")
        sem_threshold_slider = tk.Scale(
            self.threshold_frame, from_=0, to=255, orient="horizontal",
            command=self.update_sem_threshold)
        sem_threshold_slider.set(15)
        sem_threshold_slider.pack(side="left")

        self.margin_frame = tk.Frame(self.scrollable_frame)
        self.margin_frame.pack(side="top")
        margin_left_label = tk.Label(self.margin_frame)
        margin_left_label["text"] = "Left Margin:"
        margin_left_label.pack(side="left")
        self.margin_left_entry = tk.Entry(self.margin_frame)
        self.margin_left_entry.insert(0, "0")
        self.margin_left_entry.pack(side="left")
        margin_top_label = tk.Label(self.margin_frame)
        margin_top_label["text"] = "Top Margin:"
        margin_top_label.pack(side="left")
        self.margin_top_entry = tk.Entry(self.margin_frame)
        self.margin_top_entry.insert(0, "22")
        self.margin_top_entry.pack(side="left")
        margin_right_label = tk.Label(self.margin_frame)
        margin_right_label["text"] = "Right Margin:"
        margin_right_label.pack(side="left")
        self.margin_right_entry = tk.Entry(self.margin_frame)
        self.margin_right_entry.insert(0, "0")
        self.margin_right_entry.pack(side="left")
        margin_bottom_label = tk.Label(self.margin_frame)
        margin_bottom_label = tk.Label(self.margin_frame)
        margin_bottom_label["text"] = "Bottom Margin:"
        margin_bottom_label.pack(side="left")
        self.margin_bottom_entry = tk.Entry(self.margin_frame)
        self.margin_bottom_entry.insert(0, "21")
        self.margin_bottom_entry.pack(side="left")

        image_frame = tk.Frame(self.scrollable_frame)
        image_frame.pack(side="top")

        self.cr_image_label = tk.Label(image_frame)
        self.cr_image_label.pack(side="left")

        self.sem_image_label = tk.Label(image_frame)
        self.sem_image_label.pack(side="left")

        self.overlay_image_label = tk.Label(self.scrollable_frame)
        self.overlay_image_label.pack(side="top")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta/120)), "units")

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def select_cr_image(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.cr_image = cv2.imread(filepath)
            self.display_cr_image()

    def select_sem_image(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.sem_image = cv2.imread(filepath)
            self.display_sem_image()

    def display_cr_image(self):
        if hasattr(self, 'cr_image'):
            image = self.trim_image(self.cr_image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.cr_image_label.config(image=image)
            self.cr_image_label.image = image

    def display_sem_image(self):
        if hasattr(self, 'sem_image'):
            image = self.trim_image(self.sem_image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.sem_image_label.config(image=image)
            self.sem_image_label.image = image

    def trim_image(self, image):
        if image is not None:
            margin_left = int(self.margin_left_entry.get())
            margin_top = int(self.margin_top_entry.get())
            margin_right = int(self.margin_right_entry.get())
            margin_bottom = int(self.margin_bottom_entry.get())
            return image[margin_top:image.shape[0]-margin_bottom, margin_left:image.shape[1]-margin_right]
        return None

    def update_cr_threshold(self, value):
        self.cr_threshold = int(value)

    def update_sem_threshold(self, value):
        self.sem_threshold = int(value)

    def generate_overlay(self):
        if hasattr(self, 'cr_image') and hasattr(self, 'sem_image'):
            if self.cr_image.shape == self.sem_image.shape:
                cr_image = self.trim_image(self.cr_image)
                sem_image = self.trim_image(self.sem_image)
                cr_gray = cv2.cvtColor(cr_image, cv2.COLOR_BGR2GRAY)
                sem_gray = cv2.cvtColor(sem_image, cv2.COLOR_BGR2GRAY)
                _, cr_thresholded = cv2.threshold(
                    cr_gray, self.cr_threshold, 255, cv2.THRESH_BINARY)
                _, sem_thresholded = cv2.threshold(
                    sem_gray, self.sem_threshold, 255, cv2.THRESH_BINARY)
                overlay = cv2.bitwise_not(cv2.bitwise_and(
                    cr_thresholded, sem_thresholded))

                cv2.imwrite("output/overlay.png", overlay)
                cv2.imwrite("output/sem_gray.png", sem_gray)
                cv2.imwrite("output/cr_gray.png", cr_gray)
                cv2.imwrite("output/sem_thresholded.png", sem_thresholded)
                cv2.imwrite("output/cr_thresholded.png", cr_thresholded)

                # Convert to numpy array if not already
                overlay_array = np.array(overlay)

                # Count white pixels (value 255) in each row
                white_pixels_per_row = np.sum(overlay_array == 255, axis=1)

                # Create DataFrame and save to CSV
                row_data = pd.DataFrame({
                    'row': range(len(white_pixels_per_row)),
                    'void pixels': white_pixels_per_row
                })
                row_data.to_csv('output/voids.csv', index=False)

                # Continue with original display logic
                overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2RGB)
                overlay = Image.fromarray(overlay)
                overlay_im = ImageTk.PhotoImage(overlay)
                self.overlay_image_label.config(image=overlay_im)
                self.overlay_image_label.image = overlay_im


if __name__ == "__main__":
    root = tk.Tk()
    root.title("SEM EDS Overlay")
    root.iconphoto(False, PhotoImage(file='TAMU.png'))
    root.geometry("1200x900")

    # Create the scrollable frame
    frame = ScrollableFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()
