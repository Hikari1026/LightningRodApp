import logging
import threading
import iotronic_lightningrod.lightningrod as lightningrod

class LightningRodFactory():
    def __init__(self) -> None:
        self.restart_schedule_active = False
        self.lr_thread = None
        self.lr_thread_event = None
        self.should_run = False

    def start_lr(self):
        if self.lr_thread is None or not self.lr_thread.is_alive():
            self.lr = lightningrod.LightningRod()
            self.lr_thread_event = threading.Event()
            self.lr_thread = threading.Thread(target=self.lr.start, args=[self.lr_thread_event], daemon=True, name="LR-start")
            self.should_run = True
            self.lr_thread.start()
            self._lr_mon = threading.Thread(target=self._monitor_task, name="lr_mon", daemon=True)
            self._lr_mon.start()
            logging.info("LightningRodFactory: LR started")
        else:
            logging.info("LightningRodFactory: LR is already running")

    def _monitor_task(self):
        # The monitor will wait until LR main thread ends and restarts it
        logging.info("Monitor task: Monitor thread started")
        while True:
            self.lr_thread.join()
            if self.should_run:
                self.lr_thread_event.clear()
                self.lr_thread = threading.Thread(target=self.lr.start, args=[self.lr_thread_event], daemon=True, name="LR-start")
                self.lr_thread.start()
                logging.info("Monitor task: LR restarted")
            else:
                return

    def stop_lr(self):
        if self.lr_thread is not None and self.lr_thread.is_alive():
            self.should_run = False
            self.lr_thread_event.set()
            self.lr_thread.join()
            logging.info("LightningRodFactory: LR stopped")
        else:
            logging.info("LightningRodFactory: LR is not running")

    def is_lr_running(self):
        return (self.lr_thread is not None and self.lr_thread.is_alive())
