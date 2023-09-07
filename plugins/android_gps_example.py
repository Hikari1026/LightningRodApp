# This is a special plugin you should only use it with the Lightning rod Android app

from iotronic_lightningrod.modules.plugins import Plugin

from oslo_log import log as logging
LOG = logging.getLogger(__name__)

# User imports
import threading

# This are special imports for the Android app; they will serve as a Python-Java bridge since beeware does not currently offers a direct API access
# for more informations on how to perform direct API access a knowledge of the Android SDK and basics of Java language are highly recommended
# Chaquopy is the internal Python-Java bridge. The documentation can be found here: https://chaquo.com/chaquopy/doc/current/index.html

from java import jclass
from java.lang import Runnable, SecurityException
from java import dynamic_proxy, Override, jvoid
from android.location import LocationManager, LocationListener, Location

# When accessing sensible data (like peripherals) keep in mind that the Lightning rod app should already contain the proper permissions in the AndroidManifest.xml
# furthermore manual consent may be required at least on first usage
# The manifest file can be found (using the intended app and devtools) at "lightningrodapp/build/lightningrodapp/android/gradle/app/src/main/AndroidManifest.xml"

# For this plugin you will need to add the following permissions
# <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
# <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

class PythonLocationListener(dynamic_proxy(LocationListener)):
    def __init__(self, event):
        super().__init__()
        self.event = event
        self.coords = []

    @Override(jvoid, [Location])
    def onLocationChanged(self, location):
        # location is an ArrayList of Location so it must be iterated like this
        for i in range(location.size()):
            l = location.get(i)
            self.coords.append((l.getLatitude(), l.getLongitude()))
        self.event.set()


class GPSWrapper:
    def __init__(self) -> None:
        self.activity = self.context = jclass(
            "org.beeware.android.MainActivity"
        ).singletonThis
        self.location_manager = self.context.getSystemService(self.context.LOCATION_SERVICE)

    def start(self):
        # Check if permissions were granted
        self.permissions = [
            jclass("android.Manifest$permission").ACCESS_COARSE_LOCATION,
            jclass("android.Manifest$permission").ACCESS_FINE_LOCATION,
        ]
        permissions_granted = all(
            self.activity.checkSelfPermission(permission) == jclass(
                "android.content.pm.PackageManager"
            ).PERMISSION_GRANTED for permission in self.permissions
        )
        if not permissions_granted:
            self.activity.requestPermissions(self.permissions, 101)
        
        # The GPS listener callback will be fired from Android directly in the main thread
        # some time in the future. I'll use events to set up sync between threads
        self.event = threading.Event()
        self.listener = PythonLocationListener(self.event)

        # The plugin will be executed in a thread different from the MainThread so i need to create a
        # Java runner that will perform this action in the Android UiThread
        def run_on_ui_thread(manager, listener):
            class R(dynamic_proxy(Runnable)):
                def run(self):
                    try:
                        manager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 10, 1, listener)
                    except SecurityException:
                        LOG.info("Could not perform the requested operation")
                        LOG.info("Make sure you've given the required authorizations to the app")
                    
            self.activity.runOnUiThread(R())
        run_on_ui_thread(self.location_manager, self.listener)

        
        # Wait for the MainThread to return the coords
        flag = self.event.wait(10)

        # Cleanup just in case
        self.location_manager.removeUpdates(self.listener)

        if flag:
            # This plugin uses requestLocationUpdates so it will return a list of coordinates if the phone is moving during the plugin execution
            return self.listener.coords
        else:
            return None


class Worker(Plugin.Plugin):

    def __init__(self, uuid, name, q_result, params=None):
        super(Worker, self).__init__(uuid, name, q_result, params)
        self.gps = GPSWrapper()

    def run(self):
        LOG.info("Running plugin " + self.name)
        coordinates = self.gps.start()
        LOG.info("Plugin " + self.name + " process completed!")
        LOG.info(f"Retrieved coordinates: {coordinates}")
        self.q_result.put(str(coordinates))