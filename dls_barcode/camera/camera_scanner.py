import cv2

import winsound
import time
import multiprocessing

from util import Image
from scan import Scanner

from .overlay import Overlay

Q_LIMIT = 1
SCANNED_TAG = "Already Scanned"
NO_PUCK_TIME = 5
NO_PUCK_TAG = "No Puck Detected"
EXIT_KEY = 'q'

# Maximum frame rate to sample at (rate will be further limited by speed at which frames can be processed)
MAX_SAMPLE_RATE = 10.0
INTERVAL = 1.0 / MAX_SAMPLE_RATE


class CameraScanner:
    """ Manages the continuous scanning mode which takes a live feed from an attached camera and
    periodically scans the images for plates and barcodes. Multiple partial images are combined
    together until enough barcodes are scanned to make a full plate.

    Two separate processes are spawned, one to handle capturing and displaying images from the camera,
    and the other to handle processing (scanning) of those images.
    """
    def __init__(self, result_queue):
        """ The task queue is used to store a queue of captured frames to be processed; the overlay
        queue stores Overlay objects which are drawn on to the image displayed to the user to highlight
        certain features; and the result queue is used to pass on the results of successful scans to
        the object that created the ContinuousScan.
        """
        self.task_queue = multiprocessing.Queue()
        self.overlay_queue = multiprocessing.Queue()
        self.kill_queue = multiprocessing.Queue()
        self.result_queue = result_queue

    def stream_camera(self, config):
        """ Spawn the processes that will continuously capture and process images from the camera.
        """
        capture_args = (self.task_queue, self.overlay_queue, self.kill_queue, config)
        scanner_args = (self.task_queue, self.overlay_queue, self.result_queue, config)

        capture_pool = multiprocessing.Process(target=_capture_worker, args=capture_args)
        scanner_pool = multiprocessing.Process(target=_scanner_worker, args=scanner_args)

        capture_pool.start()
        scanner_pool.start()

    def kill(self):
        self.kill_queue.put(None)
        self.task_queue.put(None)


def _capture_worker(task_queue, overlay_queue, kill_queue, config):
    """ Function used as the main loop of a worker process. Continuously captures images from
    the camera and puts them on a queue to be processed. The images are displayed (as video)
    to the user with appropriate highlights (taken from the overlay queue) which indicate the
    position of scanned and unscanned barcodes.
    """
    # Initialize the camera
    cap = cv2.VideoCapture(config.camera_number.value())
    read_ok, _ = cap.read()
    if not read_ok:
        cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width.value())
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height.value())

    # Store the latest image overlay which highlights the puck
    latest_overlay = Overlay(None, config)
    last_time = time.time()

    while kill_queue.empty():
        # Capture the next frame from the camera
        read_ok, frame = cap.read()

        # Add the frame to the task queue to be processed
        if task_queue.qsize() < Q_LIMIT and (time.time() - last_time >= INTERVAL):
            # Make a copy of image so the overlay doesn't overwrite it
            task_queue.put(frame.copy())
            last_time = time.time()

        # Get the latest overlay
        while not overlay_queue.empty():
            latest_overlay = overlay_queue.get(False)

        # Draw the overlay on the frame
        latest_overlay.draw_on_image(frame)

        # Display the frame on the screen
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow('Barcode Scanner', small)

        # Exit scanning mode if the exit key is pressed
        if cv2.waitKey(1) & 0xFF == ord(EXIT_KEY):
            break

    # Clean up camera and kill the worker threads
    task_queue.put(None)
    cap.release()
    cv2.destroyAllWindows()


def _scanner_worker(task_queue, overlay_queue, result_queue, options):
    """ Function used as the main loop of a worker process. Scan images for barcodes,
    combining partial scans until a full puck is reached.

    Keep the record of the last scan which was at least partially successful (aligned geometry
    and some barcodes scanned). For each new frame, we can attempt to merge the results with
    this previous plates so that we don't have to re-read any of the previously captured barcodes
    (because this is a relatively expensive operation).
    """
    last_plate = None
    last_full_plate = None
    last_plate_time = time.time()

    frame_number = 0
    barcode_counter = 0
    plate_frame_number = 0

    scanner = Scanner(options)

    while True:
        # Get next image from queue (terminate if a queue contains a 'None' sentinel)
        frame = task_queue.get(True)
        if frame is None:
            break

        frame_number += 1
        frame_start_time = time.time()

        # Make grayscale version of image
        cv_image = Image(None, frame)
        gray_image = cv_image.to_grayscale()

        # If we have an existing partial plate, merge the new plate with it and only try to read the
        # barcodes which haven't already been read. This significantly increases efficiency because
        # barcode read is expensive.
        plate = scanner.scan_next_frame(gray_image)
        diagnostic = scanner.get_frame_diagnostic()

        if last_plate and plate.id == last_plate.id:
            plate_frame_number += 1
        else:
            plate_frame_number = 1

        # If the plate is aligned, display overlay results ( + sound + save results)
        if diagnostic.is_aligned:
            # Record the time so we can see how long its been since we last saw a plate
            last_plate_time = time.time()

            # If the plate matches the last successfully scanned plate, ignore it
            if last_full_plate and last_full_plate.has_slots_in_common(plate):
                overlay_queue.put(Overlay(None, options, SCANNED_TAG))

            # If the plate has the required number of barcodes, store it
            elif plate.is_full_valid():
                result_queue.put((plate, cv_image))
                last_full_plate = plate

            # If there were any barcodes in the frame, make a beep sound
            elif diagnostic.has_barcodes:
                if options.scan_beep.value():
                    frequency = int(10000 * ((plate.num_slots - plate.num_valid_barcodes()) / plate.num_slots)) + 37
                    winsound.Beep(frequency, 200)
                overlay = Overlay(plate, options)
                overlay_queue.put(overlay)

                if plate == last_plate and plate.num_valid_barcodes() > barcode_counter:
                    result_queue.put((plate, cv_image))

            last_plate = plate
            barcode_counter = plate.num_valid_barcodes()

        else:
            # Display a message if we haven't detected a puck for a while
            time_since_plate = time.time() - last_plate_time
            if time_since_plate > NO_PUCK_TIME:
                overlay = Overlay(None, options, NO_PUCK_TAG)
                overlay_queue.put(overlay)

        # Diagnostics
        if options.console_frame.value():
            frame_end_time = time.time()
            print('-'*30)
            print("Frame number: {} (Plate frame: {})".format(frame_number, plate_frame_number))
            print("Frame Duration: {0:.3f} secs".format(frame_end_time - frame_start_time))