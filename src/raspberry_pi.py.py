import os
import time
import picamera
import RPi.GPIO as GPIO

def capture_image(save_dir, filename):
    # Ensure the directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Initialize the PiCamera
    with picamera.PiCamera() as camera:
        # Adjust camera settings if needed
        # camera.resolution = (1920, 1080)  # Set resolution
        # camera.rotation = 180             # Set rotation

        # Capture an image
        camera.start_preview()
        # Add a delay to allow the camera to adjust to light levels
        time.sleep(2)
        camera.capture(os.path.join(save_dir, filename))
        camera.stop_preview()

# Main function
def main():
    save_directory = "/home/pi/Desktop/GarbageDetection/PhotoOutput"
    filename = "image.jpg"  # Change filename as needed
    capture_image(save_directory, filename)
    print(f"Image captured and saved to {os.path.join(save_directory, filename)}")

if __name__ == "__main__":
    main()

print("Waiting for 20 seconds to simulate model processing time...")
time.sleep(20)

def read_text_file(directory, filename):
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"The file {filename} does not exist in the directory {directory}.")
        return None

directory = '/home/pi/Desktop/GarbageDetection/TextInput' 
filename = 'prediction_output.txt'  
file_content = read_text_file(directory, filename)

if file_content is not None:
    print(file_content)

# GPIO setup
GPIO.setmode(GPIO.BOARD)
servo_pin = 11  # Define the GPIO pin for the servo

# Setup servo pin
GPIO.setup(servo_pin, GPIO.OUT)

# Initialize PWM for the servo
servo = GPIO.PWM(servo_pin, 50)
servo.start(0)

def move_servo_to_position(position):
    duty = position / 18 + 2  # Convert position (0-180 degrees) to duty cycle (2-12)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Allow time for the servo to move

try:
    if file_content == "0: Biodegradable":
        # Move servo to the right (e.g., 90 degrees)
        move_servo_to_position(90)
    else:
        # Move servo to the left (e.g., 0 degrees)
        move_servo_to_position(0)
except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    # Stop PWM and cleanup GPIO
    servo.stop()
    GPIO.cleanup()
