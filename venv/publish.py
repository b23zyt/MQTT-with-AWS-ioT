import time
import json
import random
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

# THING informaation
ENDPOINT = "aqu7583chrlrw-ats.iot.us-east-2.amazonaws.com"
CLIENT_ID = "my_shadow_device"
PATH_TO_CERT = "../my_device.cert.pem"
PATH_TO_KEY = "../my_device.private.key"
PATH_TO_ROOT = "../root-CA.crt"
THING_NAME = "my_device"
COUNT = 1

"""
Here are the acceptable data ranges:
BMI270 IMU
Accel: ±4g → −39.24 to +39.24 m/s²
Gyro: ±500°/s → −500 to +500 deg/s
ILPS22QS pressure sensor
260 to 1260 hPa, typical range ~970 to 1050 hPa
FSR
Expected voltage range ~0.5V to 3.3V when pressed (depends on divider config)
"""

desired_temperature = None
desired_humidity = None
desired_accel_x = None
desired_accel_y = None
desired_accel_z = None
desired_gyro_x = None
desired_gyro_y = None
desired_gyro_z = None
desired_pressure = None
desired_voltage = None

temperature_tolerance = 3.0
humidity_tolerance = 10.0
accel_tolerance = 2.0
gyro_tolerance = 2.0
voltage_tolerance = 1.9
pressure_tolerance = 500

event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=PATH_TO_CERT,
    pri_key_filepath=PATH_TO_KEY,
    client_bootstrap=client_bootstrap,
    ca_filepath=PATH_TO_ROOT,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=100 
)

print("Connecting to AWS IoT Core...")
connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected!")

# delta callback
def on_delta_received(topic, payload, **kfwargs):
    global desired_temperature, desired_humidity, desired_accel_x, desired_accel_y, desired_accel_z, desired_gyro_x, desired_gyro_y, desired_gyro_z, desired_pressure, desired_voltage

    message = json.loads(payload)
    print("\n Received delta message:")
    print(json.dumps(message, indent=2))

    if "state" in message:
        delta = message["state"]
        desired_temperature = delta.get("temperature", desired_temperature)
        desired_humidity = delta.get("humidity", desired_humidity)
        desired_accel = delta.get("accel", {})
        desired_accel_x = desired_accel.get("x", desired_accel_x)
        desired_accel_y = desired_accel.get("y", desired_accel_y)
        desired_accel_z = desired_accel.get("z", desired_accel_z)
        
        desired_gyro = delta.get("gyro", {})
        desired_gyro_x = desired_gyro.get("x", desired_gyro_x)
        desired_gyro_y = desired_gyro.get("y", desired_gyro_y)
        desired_gyro_z = desired_gyro.get("z", desired_gyro_z)
        desired_pressure = delta.get("pressure", desired_pressure)
        desired_voltage = delta.get("voltage", desired_voltage)

        print(f"""
Updated desired_temperature: {desired_temperature}, desired_humidity: {desired_humidity},"
desired_accel: x={desired_accel_x}, y={desired_accel_y}, z={desired_accel_z},"
desired_gyro: x={desired_gyro_x}, y={desired_gyro_y}, z={desired_gyro_z},"
desired_pressure: {desired_pressure}, desired_voltage: {desired_voltage}"
        """)
        # Simulation: After receiving the instruction, the device responds and then reports the new status
        # report_state(desired_state) send the delta (desired message back to the cloud)

# input of this function is a state ({"", ""}), JSON
def report_state(state):
    "expecting no response"
    print("\n Reporting desired state to shadow...")    
    payload = {
        "state": {
            "reported": state,
            # "desired": None
        }
    }
    mqtt_connection.publish(
        topic=f"$aws/things/{THING_NAME}/shadow/update",
        payload=json.dumps(payload),
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    
# Inputs of this function are integers
def report_device_data(temperature, humidity, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, pressure, voltage):
    """publish data to 	$aws/things/{THING_NAME}/shadow/update"""
    
    global COUNT
    #packet to data in JSON
    payload = {
        "state": {
            "reported": {
                "temperature": temperature,
                "humidity": humidity,
                "accel": {
                    "x": accel_x,
                    "y": accel_y,
                    "z": accel_z
                },
                "gyro": {
                    "x": gyro_x,
                    "y": gyro_y,
                    "z": gyro_z
                },
                "pressure": pressure,
                "voltage": voltage,
                "timestamp": int(time.time())  # timestamp
            }
        }
    }
    print(f"\n Publish the {COUNT}th state to shadow...")
    COUNT = COUNT + 1
    mqtt_connection.publish(
        topic=f"$aws/things/{THING_NAME}/shadow/update",
        payload=json.dumps(payload),
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print(f" Published\n")
    print(json.dumps(payload, indent=2))

def check_and_report_data(temp, humidity, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, pressure, voltage):
    alert = {}
    if desired_temperature is not None:
        if abs(temp - desired_temperature) > temperature_tolerance:
            alert["temperature"] = f"Temperature out of range: {(temp-desired_temperature):.2f}°C"

    if desired_humidity is not None:
        if abs(humidity - desired_humidity) > humidity_tolerance:
            alert["humidity"] = f"Humidity out of range: {(humidity - desired_humidity):.2f}g/cm3"

    if desired_accel_x is not None:
        if abs(accel_x - desired_accel_x) > accel_tolerance:
            alert["accel_x"] = f"Accel X out of range: {(accel_x - desired_accel_x):.2f} m/s²"
    if desired_accel_y is not None:
        if abs(accel_y - desired_accel_y) > accel_tolerance:
            alert["accel_y"] = f"Accel Y out of range: {(accel_y - desired_accel_y):.2f} m/s²"
    if desired_accel_z is not None:
        if abs(accel_z - desired_accel_z) > accel_tolerance:
            alert["accel_z"] = f"Accel Z out of range: {(accel_z - desired_accel_z):.2f} m/s²"

    if desired_gyro_x is not None:
        if abs(gyro_x - desired_gyro_x) > gyro_tolerance:
            alert["gyro_x"] = f"Gyro X out of range: {(gyro_x - desired_gyro_x):.2f} deg/s"
    if desired_gyro_y is not None:
        if abs(gyro_y - desired_gyro_y) > gyro_tolerance:
            alert["gyro_y"] = f"Gyro Y out of range: {(gyro_y - desired_gyro_y):.2f} deg/s"
    if desired_gyro_z is not None:
        if abs(gyro_z - desired_gyro_z) > gyro_tolerance:
            alert["gyro_z"] = f"Gyro Z out of range: {(gyro_z - desired_gyro_z):.2f} deg/s"

    if desired_pressure is not None:
        if abs(pressure - desired_pressure) > pressure_tolerance:
            alert["pressure"] = f"Pressure out of range: {(pressure - desired_pressure):.2f} hPa"

    if desired_voltage is not None:
        if abs(voltage - desired_voltage) > voltage_tolerance:
            alert["voltage"] = f"Voltage out of range: {(voltage - desired_voltage):.2f} V"

    

    if alert:
        mqtt_connection.publish(
            topic=f"$aws/things/{THING_NAME}/alerts",
            payload=json.dumps({
                "timestamp": int(time.time()),
                "alerts": alert
            }),
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print("🚨 Alert published:\n", json.dumps(alert, indent=2))


# subscribe shadow delta topic (trigger the callback function whenever published != desired)
mqtt_connection.subscribe(
    topic=f"$aws/things/{THING_NAME}/shadow/update/delta",
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_delta_received
)

# First test
# only send the delta message that the data that is different from desired
initial_temperature = 22
initial_humidity = 50
initial_accel_x = 3
initial_accel_y = 3
initial_accel_z = 3
initial_gyro_x = 3
initial_gyro_y = 3
initial_gyro_z = 3
initial_pressure = 300
initial_voltage = 2.0
initial_state = {
    "temperature": initial_temperature, 
    "humidity": initial_humidity,
    "accel": {
        "x": initial_accel_x,
        "y": initial_accel_y,
        "z": initial_accel_z
    },
    "gyro": {
        "x": initial_gyro_x,
        "y": initial_gyro_y,
        "z": initial_gyro_z
    },
    "pressure": initial_pressure,
    "voltage": initial_voltage,
} 
print(f"\n Initial state being reported:\n")
print(json.dumps(initial_state, indent=2))

report_device_data(initial_temperature, initial_humidity, initial_accel_x, initial_accel_y, initial_accel_z, initial_gyro_x, initial_gyro_y, initial_gyro_z, initial_pressure, initial_voltage)
time.sleep(1)
check_and_report_data(initial_temperature, initial_humidity, initial_accel_x, initial_accel_y, initial_accel_z, initial_gyro_x, initial_gyro_y, initial_gyro_z, initial_pressure, initial_voltage)
#report_state(initial_state)

print("\n Ready and waiting for shadow delta updates...")
try:
    while True:
        time.sleep(100)
        temp = 25 + random.uniform(-2, 2)  # random termperature
        humidity = 60 + random.uniform(-5, 5)  # random humidity
        accel_x = 0 + random.uniform(-5, 5)
        accel_y = 0 + random.uniform(-5, 5)
        accel_z = 0 + random.uniform(-5, 5)
        gyro_x = 0 + random.uniform(-5, 5)
        gyro_y = 0 + random.uniform(-5, 5)
        gyro_z = 0 + random.uniform(-5, 5)
        pressure = 760 + 0 + random.uniform(-800, 800)
        voltage = 1.4 + 0 + random.uniform(-2, 2)
        report_device_data(temp, humidity, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, pressure, voltage) 
        time.sleep(1)
        check_and_report_data(temp, humidity, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, pressure, voltage)


except KeyboardInterrupt:
    print("\nDisconnecting...")
    mqtt_connection.disconnect().result()
    print("Disconnected.")


# Shadow Delta for the sensors: 
# {
#   "state": {
#     "desired": {
#       "accel": {
#         "x": 0,
#         "y": 0,
#         "z": 0,
#       },
#       "gyro":{
#         "x": 0,
#         "y": 0,
#         "z": 0,
#       },
#       "pressure": 760,
#       "voltage": 1.4,
#     },
#   }
# }