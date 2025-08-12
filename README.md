# AWS IoT Device Shadow Demo

This is a simple Python program that connects a device to **AWS IoT Core** using MQTT and device shadows.  
It simulates sensor data (temperature, humidity, accel, gyro, pressure, voltage), reports it to AWS, and listens for desired state updates.

---

## 🚀 Features

- Secure connection to AWS IoT Core using certificates  
- Sends **simulated sensor data** to device shadow (`reported` state)  
- Listens for **desired state** changes (`delta` updates)  
- Checks data against tolerances and publishes **alerts** if out of range  

---

## 🛠️ How to Use

1. Prepare your AWS IoT certificates:
   - Device certificate (.cert.pem)  
   - Private key (.private.key)  
   - Root CA certificate (.crt)  

2. Edit the Python script to update:
   - `ENDPOINT` — your AWS IoT endpoint  
   - Paths to cert/key files (`PATH_TO_CERT`, `PATH_TO_KEY`, `PATH_TO_ROOT`)  

3. Run the script with Python 3:
   ```bash
   python your_script_name.py

4. The script will start sending data and respond to shadow delta updates automatically.
5. Press `Ctrl + C` to safely stop the program.

## 📚 AWS IoT Configuration Manual
For detailed steps on setting up your AWS IoT Thing, certificates, policies, and permissions, please check the manual [here](https://docs.google.com/document/d/1ds6ZI0OCf_oUa0Dnds8dPZbTZ8mBRjQzIsZubWbZmvQ/edit?tab=t.0):
