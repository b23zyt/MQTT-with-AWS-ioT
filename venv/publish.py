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
    message = json.loads(payload)
    print("\n Received delta message:")
    print(json.dumps(message, indent=2))

    if "state" in message:
        desired_state = message["state"]
        # Simulation: After receiving the instruction, the device responds and then reports the new status
        # report_state(desired_state) send the delta (desired message back to the cloud)

# send the inital data
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
    
# Regularly report the current sensor data of the equipment to the cloud
def report_device_data(temperature, humidity):
    """publish data to 	$aws/things/{THING_NAME}/shadow/update"""
    payload = {
        "state": {
            "reported": {
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": int(time.time())  # timestamp
            }
        }
    }

    print("\n Publish current state to shadow...")
    mqtt_connection.publish(
        topic=f"$aws/things/{THING_NAME}/shadow/update",
        payload=json.dumps(payload),
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print(f" Published: {payload}")

# subscribe shadow delta topic (trigger the callback function whenever published != desired)
mqtt_connection.subscribe(
    topic=f"$aws/things/{THING_NAME}/shadow/update/delta",
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_delta_received
)

# Test
# only send the delta message that the data that is different from desired
initial_state = {"temperature": 28, "humidity": 31} 
print(f"\n Initial state being reported: {initial_state}")
report_state(initial_state)

print("\n Ready and waiting for shadow delta updates...")
try:
    while True:
        time.sleep(10)
        temp = 25 + random.uniform(-2, 2)  # random termperature
        humidity = 60 + random.uniform(-5, 5)  # random humidity
        report_device_data(temp, humidity) 
        #time.sleep(10)  # publish random data every 10 seconds

except KeyboardInterrupt:
    print("\nDisconnecting...")
    mqtt_connection.disconnect().result()
    print("Disconnected.")
