import os
import sys
import time
import cv2
import numpy as np
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageEventHandler(FileSystemEventHandler):
    def __init__(self, folder_with_pics, display_duration):
        super().__init__()
        self.folder_with_pics = folder_with_pics
        self.display_duration = display_duration
        self.pics = []
        self.current_index = 0
        self.new_images = []
        self.new_file_pth = None

    def start_slideshow(self):
        self.pics = self.get_image_files()
        self.current_index = 0

        # Display the images as a slideshow
        while True:
            if len(self.pics) == 0:
                print("No pics present")
                time.sleep(1)
                continue

            while len(self.new_images) > 0:
                print("Displaying new image")
                self.display_new_image(self.new_images.pop())

            self.display_image(self.pics[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.pics)

    def get_image_files(self):
        pics = []
        # Iterate over all files in the directory
        for filename in os.listdir(self.folder_with_pics):
            file_path = os.path.join(self.folder_with_pics, filename)
            # Check if the file is an image based on its extension
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                pics.append(file_path)
        return pics

    def display_image(self, pic):
        abs_pic_path = os.path.abspath(pic)
        print("Path: " + abs_pic_path)

        image = cv2.imread(abs_pic_path)
        frame_delay = self.display_duration * 1000

        self.render_image_with_fade_in(image, frame_delay)

    def display_new_image(self, pic):
        abs_pic_path = os.path.abspath(pic)
        print(abs_pic_path)

        image = cv2.imread(abs_pic_path)
        # Add the text to the image
        text = "New image"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        color = (128, 0, 128)  # Purple color (RGB values)
        thickness = 2

        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = int((image.shape[1] - text_size[0]) / 2)  # Centered horizontally
        text_y = int((image.shape[0] - text_size[1]) - 10)  # Centered vertically

        cv2.putText(image, text, (text_x, text_y), font, font_scale, color, thickness)

        # Display the image
        self.render_image_with_fade_in(image, self.display_duration * 1000 * 2)
            
    def render_image_with_fade_in(self, image, frame_delay):
        # Create a blank canvas with the same size and data type as the image
        canvas = np.zeros_like(image, dtype=np.float32)

        # Define the duration for each fade step in milliseconds
        fade_duration = 500  # 0.5 seconds

        # Calculate the number of steps for fade-in and fade-out
        num_steps = fade_duration // 10  # Assuming 10ms delay between steps

        # Perform fade-in
        for alpha in np.linspace(0, 255, num_steps):
            alpha = int(alpha)
            alpha_blend = cv2.addWeighted(image, alpha / 255.0, canvas.astype(image.dtype), 1 - alpha / 255.0, 0)
            cv2.imshow("Fullscreen Image", alpha_blend)
            cv2.waitKey(10)  # 10ms delay between steps
        # Wait for the display duration without any fading
        k = cv2.waitKey(frame_delay)

        if k == 27:
            sys.exit()

        # Perform fade-out
        for alpha in np.linspace(255, 0, num_steps):
            alpha = int(alpha)
            alpha_blend = cv2.addWeighted(image, alpha / 255.0, canvas.astype(image.dtype), 1 - alpha / 255.0, 0)
            cv2.imshow("Fullscreen Image", alpha_blend)
            cv2.waitKey(10)  # 10ms delay between steps

    def on_created(self, event):
        if event.is_directory:
            return

        # Check if the created file is an image
        if any(event.src_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            new_file = event.src_path
            # Check if the new file is not already in the list
            if new_file not in self.pics:
                self.pics.append(new_file)
                self.new_images.append(new_file)
                print("New file added", new_file)
                time.sleep(0.5)


def main():
    # Check if no path or display duration
    if len(sys.argv) < 3:
        print("Provide path to the directory containing image files and display duration.")
        sys.exit(1)

    folder_with_pics = sys.argv[1]  # First argument should be the path to the folder
    display_duration = int(sys.argv[2])  # Second argument should be the display duration in seconds

    event_handler = ImageEventHandler(folder_with_pics, display_duration)
    observer = Observer()
    observer.schedule(event_handler, folder_with_pics, recursive=False)
    observer.start()

    # cv2.namedWindow("Fullscreen Image", cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty("Fullscreen Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    cv2.namedWindow("Fullscreen Image")
    # cv2.setWindowProperty("Fullscreen Image")

    try:
        event_handler.start_slideshow()
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


main()