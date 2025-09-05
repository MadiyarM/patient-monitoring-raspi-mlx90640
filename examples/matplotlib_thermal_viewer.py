import time
import board
import busio
import numpy as np
import adafruit_mlx90640
import matplotlib.pyplot as plt
from collections import deque

def initialize_sensor():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    # Adjust refresh rate as desired (0.5Hz, 1Hz, 2Hz, 4Hz, 8Hz, 16Hz, 32Hz, 64Hz)
    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ
    return mlx

def setup_plot():
    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 7))

    # Initialize the display with zeros
    therm1 = ax.imshow(
        np.zeros((24, 32)),
        vmin=0,
        vmax=60,
        cmap="inferno",
        interpolation="bilinear"
    )

    # Add colorbar
    cbar = fig.colorbar(therm1)
    cbar.set_label("Temperature (°C)", fontsize=14)

    # Title
    plt.title("Madiyar Thermal Image")

    # --- Remove any inversion of Y-axis ---
    # If you previously had: ax.invert_yaxis(), remove it to fix upside-down view.

    return fig, ax, therm1

def update_display(fig, ax, therm1, data_array):
    """
    Update the matplotlib imshow with the new data array.
    data_array is 24 x 32 with temperature values.
    """

    # If needed, flip left-right. Remove/adjust if it still looks upside-down or mirrored.
    flipped = np.fliplr(data_array)  

    therm1.set_data(flipped)

    # Determine min/max so the color scale matches the data
    min_temp = np.min(flipped)
    max_temp = np.max(flipped)
    therm1.set_clim(vmin=min_temp, vmax=max_temp)

    # Clear old patches & texts so they don’t accumulate
    for patch in ax.patches:
        patch.remove()
    for txt in ax.texts:
        txt.remove()

    # --- Smaller bounding box with black borders only ---
    # Coordinates in the 24(height) x 32(width) space:
    x1, y1 = 10, 8
    x2, y2 = 22, 16  # This is a rectangle 12 wide, 8 high

    rect = plt.Rectangle(
        (x1, y1),
        x2 - x1,
        y2 - y1,
        fill=False,
        edgecolor="black",
        linewidth=2
    )
    ax.add_patch(rect)

    # Place name in white text near top-left of the box
    ax.text(
        x1 + 0.5,
        y2 - 0.5,
        "Madiyar",
        color="white",
        fontsize=9,
        fontweight="bold",
        verticalalignment="top"
    )

    # Place temperature in white text near top-right of the box
    temp_str = f"{max_temp:.1f}C"
    ax.text(
        x2 - 0.5,
        y2 - 0.5,
        temp_str,
        color="white",
        fontsize=9,
        fontweight="bold",
        horizontalalignment="right",
        verticalalignment="top"
    )

    # Redraw the figure
    ax.draw_artist(ax.patch)
    ax.draw_artist(therm1)
    fig.canvas.draw()
    fig.canvas.flush_events()

def main():
    mlx = initialize_sensor()
    fig, ax, therm1 = setup_plot()

    # MLX90640 returns 24 x 32 = 768 values
    frame = np.zeros((24 * 32,), dtype=float)
    filtered_frame = np.zeros((24, 32), dtype=float)

    # Smoothing factor
    alpha = 0.2

    # Keep a deque of recent frame times for FPS estimate
    recent_times = deque(maxlen=20)

    print("Starting thermal display. Close plot window or press Ctrl + C to exit.")

    max_retry = 5
    while True:
        try:
            retry_count = 0
            while retry_count < max_retry:
                try:
                    # Acquire a new frame from the MLX90640
                    mlx.getFrame(frame)
                    # Reshape to 24 x 32
                    current_data = np.reshape(frame, (24, 32))

                    # Apply smoothing
                    filtered_frame = alpha * current_data + (1.0 - alpha) * filtered_frame

                    # Update the display with the new data
                    update_display(fig, ax, therm1, filtered_frame)

                    # Estimate FPS
                    now = time.monotonic()
                    recent_times.append(now)
                    if len(recent_times) > 1:
                        fps = (len(recent_times) - 1) / (recent_times[-1] - recent_times[0])
                        print(f"Approx. FPS: {fps:0.1f}")
                    else:
                        print("Measuring FPS...")

                    plt.pause(0.001)
                    break

                except ValueError:
                    # Sensor not ready, keep retrying
                    retry_count += 1

                except RuntimeError as e:
                    retry_count += 1
                    if retry_count >= max_retry:
                        print(f"Failed after {max_retry} retries with error: {e}")
                        break

        except KeyboardInterrupt:
            print("Exiting via Ctrl+C.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    plt.ioff()
    plt.close()
    print("Done.")

if __name__ == "__main__":
    main()
