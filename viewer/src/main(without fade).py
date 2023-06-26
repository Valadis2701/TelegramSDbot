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
            
    def render_image_with_fade_in(test, image, frame_delay):
        # Create a window to display the image
        cv2.namedWindow("Fullscreen Image", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Fullscreen Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Get the dimensions of the monitor
        monitor_width, monitor_height = (
            cv2.getWindowImageRect("Fullscreen Image")[2:4]
        )

        # Get the dimensions of the image
        image_height, image_width, _ = image.shape

        # Calculate the scaling factor for width and height
        scale_factor = min(
            monitor_width / image_width, monitor_height / image_height
        )

        # Calculate the scaled dimensions of the image
        scaled_width = int(image_width * scale_factor)
        scaled_height = int(image_height * scale_factor)

        # Calculate the position to center the image on the monitor
        x_offset = (monitor_width - scaled_width) // 2
        y_offset = (monitor_height - scaled_height) // 2

        # Resize the image while preserving aspect ratio
        resized_image = cv2.resize(image, (scaled_width, scaled_height))

        # Create a blank canvas with the size of the monitor
        canvas = np.zeros((monitor_height, monitor_width, 3), dtype=np.uint8)

        # Place the resized image onto the canvas at the specified position
        canvas[
            y_offset : y_offset + scaled_height, x_offset : x_offset + scaled_width
        ] = resized_image

        # Define the duration for each fade step in milliseconds
        fade_duration = 500  # 0.5 seconds

        # Calculate the number of steps for fade-in and fade-out
        num_steps = fade_duration // 10  # Assuming 10ms delay between steps

        # Perform fade-in
        for alpha in np.linspace(0, 1, num_steps):
            alpha_blend = cv2.addWeighted(
                canvas, alpha, resized_image, 1 - alpha, 0
            )
            cv2.imshow("Fullscreen Image", alpha_blend)
            if cv2.waitKey(10) == 27:  # If ESC key is pressed
                break

        # Wait for the display duration without any fading
        k = cv2.waitKey(frame_delay)

        if k == 27:
            cv2.destroyAllWindows()
            return

        # Perform fade-out
        for alpha in np.linspace(1, 0, num_steps):
            alpha_blend = cv2.addWeighted(
                canvas, alpha, resized_image, 1 - alpha, 0
            )
            cv2.imshow("Fullscreen Image", alpha_blend)
            if cv2.waitKey(10) == 27:  # If ESC key is pressed
                break

        cv2.destroyAllWindows()

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

    cv2.namedWindow("Fullscreen Image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Fullscreen Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
 

    cv2.namedWindow("Fullscreen Image")
    # cv2.setWindowProperty("Fullscreen Image")

    try:
        event_handler.start_slideshow()
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


main()