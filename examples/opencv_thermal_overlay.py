import time
import cv2
import numpy as np
import board
import busio
import adafruit_mlx90640
from smbus2 import SMBus
from picamera2 import Picamera2

alpha_val = 50

def on_trackbar(val):
    global alpha_val
    alpha_val = val

def create_hot_colorbar(min_temp, max_temp, height=240, width=40):
    gradient = np.linspace(255, 0, height, dtype=np.uint8).reshape((height, 1))
    # Use COLORMAP_HOT for a red-dominant style
    colorbar = cv2.applyColorMap(gradient, cv2.COLORMAP_HOT)
    colorbar = cv2.resize(colorbar, (width, height), interpolation=cv2.INTER_NEAREST)

    ticks = 6
    step = (max_temp - min_temp) / (ticks - 1) if ticks > 1 else 1
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i in range(ticks):
        t = min_temp + i * step
        label = f"{t:.1f}"
        frac = (max_temp - t) / (max_temp - min_temp + 1e-6)
        y = int(frac * (height - 1))
        cv2.line(colorbar, (0, y), (width // 3, y), (0,0,0), 1)
        cv2.putText(colorbar, label, (8, y+4), font, 0.5, (255,255,255), 1)
    return colorbar

def main():
    cv2.namedWindow("Thermal Overlay", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Thermal Overlay", 800, 600)
    cv2.createTrackbar("Blend (0=Cam, 100=Thermal)", "Thermal Overlay", alpha_val, 100, on_trackbar)

    picam2 = Picamera2()
    cfg = picam2.create_preview_configuration(
        main={"size": (320, 240), "format": "BGR888"}
    )
    picam2.configure(cfg)
    picam2.start()

    i2c_bus = SMBus(1)
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
    frame_mlx = [0.0] * 768

    while True:
        # Capture camera frame
        frame_cam = picam2.capture_array()
        if frame_cam.shape[2] == 4:
            frame_cam = frame_cam[:, :, :3]
        frame_cam = cv2.flip(frame_cam, 1)

        # Read from MLX90640
        try:
            mlx.getFrame(frame_mlx)
        except ValueError:
            continue

        thermal_2d = np.reshape(frame_mlx, (24, 32)).astype(np.float32)
        thermal_8 = cv2.normalize(thermal_2d, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        thermal_8 = cv2.medianBlur(thermal_8, 3)
        thermal_color = cv2.applyColorMap(thermal_8, cv2.COLORMAP_HOT)
        thermal_color = cv2.flip(thermal_color, 1)

        # Resize thermal to match camera
        h, w = frame_cam.shape[:2]
        thermal_resized = cv2.resize(thermal_color, (w, h), interpolation=cv2.INTER_CUBIC)

        # Blend
        alpha = alpha_val / 100.0
        blended = cv2.addWeighted(thermal_resized, alpha, frame_cam, 1.0 - alpha, 0)

        # Grab temperature range
        max_temp = float(np.max(thermal_2d))
        min_temp = float(np.min(thermal_2d))
        temp_str = f"{max_temp:.1f}C"

        # Draw bounding box for "face"
        x1, y1, x2, y2 = 80, 50, 240, 170
        cv2.rectangle(blended, (x1, y1), (x2, y2), (0, 0, 0), 2)

        # Banner
        header_h = 25
        box_color = (60, 60, 60)
        text_color = (255, 255, 255)
        cv2.rectangle(blended, (x1, y1 - header_h), (x2, y1), box_color, -1)
        cv2.putText(blended, "ID", (x1 + 8, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        # Temperature on the box
        w_temp = 80
        cv2.rectangle(blended, (x2 - w_temp, y1 - header_h), (x2, y1), box_color, -1)
        cv2.putText(blended, temp_str, (x2 - w_temp + 4, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

        # Create color bar
        color_bar = create_hot_colorbar(min_temp, max_temp, height=h, width=40)
        final_display = np.hstack((blended, color_bar))

        # Show
        disp = cv2.cvtColor(final_display, cv2.COLOR_BGR2RGB)
        cv2.imshow("Thermal Overlay", disp)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

