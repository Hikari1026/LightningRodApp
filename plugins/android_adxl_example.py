from iotronic_lightningrod.modules.plugins import Plugin

from oslo_log import log as logging
LOG = logging.getLogger(__name__)

# User imports
import threading

from java.lang import Runnable
from java import jclass, dynamic_proxy, Override, jvoid, jint
from android.hardware import SensorEventListener, Sensor, SensorEvent

class PythonSensorEventListener(dynamic_proxy(SensorEventListener)):
    def __init__(self, event):
        super().__init__()
        self.event = event
        self.accel_results = None

    @Override(jvoid, [SensorEvent])
    def onSensorChanged (self, sensorEvent):
        self.accel_results = {
            "Sensor_name" : sensorEvent.sensor.getName(),
            "Accuracy" : sensorEvent.accuracy,
            "Timestamp" : sensorEvent.timestamp,
            "Distance" : sensorEvent.values[0]
        }
        self.event.set()

    @Override(jvoid, [Sensor, jint])
    def onAccuracyChanged(self, sensor, i):
        pass
        

class PythonSensorManager():
    def __init__(self):
        # Get context from main activity
        self.activity = self.context = jclass(
            "org.beeware.android.MainActivity"
        ).singletonThis
        self.sensor_manager = self.context.getSystemService(self.context.SENSOR_SERVICE)
        self.proximity_sensor = self.sensor_manager.getDefaultSensor(Sensor.TYPE_PROXIMITY)

    def start(self):
        self.event = threading.Event()
        self.listener = PythonSensorEventListener(self.event)

        def run_on_ui_thread(manager, listener, proximity_sensor):
            class R(dynamic_proxy(Runnable)):
                def run(self):
                    manager.registerListener(listener, proximity_sensor, 2 * 1000 * 1000)
            self.activity.runOnUiThread(R())
        
        if (self.proximity_sensor is None):
            print("Proximity sensor not available")
        else:
            run_on_ui_thread(self.sensor_manager, self.listener, self.proximity_sensor)
            self.event.wait(10)
            self.sensor_manager.unregisterListener(self.listener)

        return self.listener.accel_results


class Worker(Plugin.Plugin):

    def __init__(self, uuid, name, q_result, params=None):
        super(Worker, self).__init__(uuid, name, q_result, params)
        self.accel = PythonSensorManager()

    def run(self):
        LOG.info("Running plugin " + self.name)
        result = self.accel.start()
        LOG.info("Plugin " + self.name + " process completed!")
        LOG.info(f"Retrieved result: {result}")
        self.q_result.put(str(result))