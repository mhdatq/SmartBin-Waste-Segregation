import paramiko
import json
import socket
import yolov5 

def run_inference(image_path, output_path):
    # Load model
    model = yolov5.load('keremberke/yolov5m-garbage')
  
    # Set model parameters
    model.conf = 0.25  # NMS confidence threshold
    model.iou = 0.45  # NMS IoU threshold
    model.agnostic = False  # NMS class-agnostic
    model.multi_label = False  # NMS multiple labels per box
    model.max_det = 1000  # maximum number of detections per image

    # Perform inference
    results = model(image_path, size=640)

    # Parse results
    predictions = results.pred[0]
    categories = predictions[:, 5]

    # Mapping of category indices to category names
    category_names = {
        0: 'Biodegradable',
        1: 'Non-Biodegradable',
        2: 'General waste',
        3: 'Glass',
        4: 'Metal',
        5: 'Plastic'
    }

    # Create output text
    class_names = {int(category): category_names.get(int(category), f"Class {int(category)}") for category in categories}
    output_text = json.dumps(class_names, indent=4)
    
    with open(output_path, 'w') as file:
        file.write(output_text)

# SSH setup for sending back the result
hostname = '192.168.166.64'
port = 22
username = 'pi'
password = 'raspberry'

if __name__ == "__main__":
    # Paths for image and output
    local_image_path = 'C:\\Users\\mhdat\\Desktop\\EPICS\\Epics\\Input\\image.jpg'
    output_path = 'C:\\Users\\mhdat\\Desktop\\EPICS\\Epics\\Output\\prediction_output.txt'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))
    server_socket.listen(5)
    print("Server listening for connections...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address} established.")

        # Receive command from Raspberry Pi
        command = client_socket.recv(1024).decode()

        if command == "process_image":
            # Establish SSH connection to Raspberry Pi and download image
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname, port, username, password)
            scp_client = ssh_client.open_sftp()
            
            remote_image_path = '/home/pi/Desktop/GarbageDetection/PhotoOutput/image.jpg'
            scp_client.get(remote_image_path, local_image_path)
            print(f"Image downloaded from {remote_image_path} and saved to {local_image_path}")

            # Run inference
            run_inference(local_image_path, output_path)
            
            # Upload the result back to Raspberry Pi
            remote_text_path = '/home/pi/Desktop/GarbageDetection/TextInput/prediction_output.txt'
            scp_client.put(output_path, remote_text_path)
            print("Inference completed and result sent to Raspberry Pi.")
            
            # Close SCP and SSH clients
            scp_client.close()
            ssh_client.close()

            # Notify Raspberry Pi that processing is done
            client_socket.send(b"done_processing")

        else:
            print(f"Unknown command: {command}")

        client_socket.close()
 