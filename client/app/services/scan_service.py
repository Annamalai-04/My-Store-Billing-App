import os
import time
import cv2
import zxingcpp


class BarcodeScanner:
    """
    DroidCam barcode scanner.

    Important:
    - There is NO hardcoded product/barcode here.
    - A barcode is accepted only from the current camera frames.
    - The first frames are discarded so an old buffered frame from
      the virtual camera cannot immediately trigger a scan.
    - The same barcode must be detected in multiple changing frames.
    """

    def __init__(self):
        self.camera_index = int(
            os.getenv("MYSTOREAPP_CAMERA_INDEX", "1")
        )

    def scan_from_phone(self):
        # BillOutPage calls this method.
        return self.scan_from_camera(self.camera_index)

    def scan_from_camera(
        self,
        camera_index=None,
        window_title="MyStoreApp Barcode Scanner"
    ):
        if camera_index is None:
            camera_index = self.camera_index

        cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        if not cam.isOpened():
            cam.release()
            cam = cv2.VideoCapture(camera_index)

        if not cam.isOpened():
            raise RuntimeError(
                f"Could not open camera index {camera_index}. "
                "Make sure DroidCam is connected."
            )

        cam.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"MJPG")
        )
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cam.set(cv2.CAP_PROP_FPS, 30)

        try:
            # Give DroidCam time to start and discard buffered frames.
            warmup_start = time.monotonic()
            warmup_seconds = 1.5

            last_frame = None
            stable_barcode = None
            stable_count = 0

            while True:
                ok, frame = cam.read()

                if not ok or frame is None:
                    continue

                # Show the current camera frame.
                cv2.putText(
                    frame,
                    "DroidCam | Show barcode | ESC = cancel",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

                cv2.imshow(window_title, frame)

                # ESC = cancel.
                if cv2.waitKey(1) & 0xFF == 27:
                    return None

                # -------------------------------------------------
                # WARM-UP
                # Ignore all barcode results during the first
                # 1.5 seconds. This prevents a stale first frame
                # from immediately closing the scanner.
                # -------------------------------------------------
                if time.monotonic() - warmup_start < warmup_seconds:
                    last_frame = frame.copy()
                    continue

                # -------------------------------------------------
                # Make sure the camera is actually producing
                # changing frames.
                # If the virtual camera is stuck on one old frame,
                # don't accept a barcode from it.
                # -------------------------------------------------
                frame_changed = True

                if last_frame is not None:
                    small_current = cv2.resize(
                        frame,
                        (160, 90)
                    )
                    small_previous = cv2.resize(
                        last_frame,
                        (160, 90)
                    )

                    difference = cv2.absdiff(
                        small_current,
                        small_previous
                    )

                    # Mean pixel change.
                    frame_change_value = float(
                        difference.mean()
                    )

                    # Very small changes can be camera noise.
                    frame_changed = frame_change_value > 1.0

                last_frame = frame.copy()

                if not frame_changed:
                    continue

                # -------------------------------------------------
                # Decode barcode from CURRENT frame.
                # -------------------------------------------------
                results = zxingcpp.read_barcodes(frame)

                if not results:
                    stable_barcode = None
                    stable_count = 0
                    continue

                barcode = results[0].text

                if not barcode:
                    continue

                # -------------------------------------------------
                # Require the SAME barcode in 3 changing frames.
                # This prevents a single stale/bad frame from
                # immediately returning a result.
                # -------------------------------------------------
                if barcode == stable_barcode:
                    stable_count += 1
                else:
                    stable_barcode = barcode
                    stable_count = 1

                if stable_count >= 3:
                    print(
                        f"Barcode confirmed from live camera: {barcode}"
                    )
                    return barcode

        finally:
            cam.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)
