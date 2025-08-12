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
1.  Install Python Stuff 
   - Make sure you have
        * Python 3.7 or newer
        * These packages:
          ```bash
          pip install awscrt awsiot

3. Prepare your AWS IoT certificates (download from the website):
   - Device certificate (.cert.pem)  
   - Private key (.private.key)  
   - Root CA certificate (.crt)

4. The main program is under `venv -> publish.py` 

5. Edit the Python script to update:
   - `ENDPOINT` — your AWS IoT endpoint  
   - Paths to cert/key files (`PATH_TO_CERT`, `PATH_TO_KEY`, `PATH_TO_ROOT`)
   - `THING_NAME` - Must match your AWS IoT Thing name

6. Run the script with Python 3:
   ```bash
   source venv/bin/activate
   cd venv
   python3 publish.py

7. The script will start sending data and respond to shadow delta updates automatically.
8. Press `Ctrl + C` to stop the program.

## Logic Behind the Code
1. Connects to AWS IoT using your certificates
2. Checks every 100 seconds for new "desired" values (like if you set a new target temperature in AWS)
3. Publishes fake sensor data (with small random changes)
4. Sends alerts if values go beyond the tolerance value

## 📚 AWS IoT Configuration Manual
For detailed steps on setting up your AWS IoT Thing, certificates, policies, and permissions, please check the manual [here](https://docs.google.com/document/d/1ds6ZI0OCf_oUa0Dnds8dPZbTZ8mBRjQzIsZubWbZmvQ/edit?tab=t.0):
