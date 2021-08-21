import winsound, time
from PyQt5.QtCore import QObject

from utils.constants import SOUND_FILE_NAME


class SoundAlarm(QObject):
    def __init__(self, sounding_time):
        super().__init__()
        if sounding_time == 0:
            self._sounding_time = None
        elif sounding_time < 0:
            self._sounding_time = 0
        else:
            self._sounding_time = sounding_time

    def start_alarm(self):
        if self._sounding_time is not None:
            start_time = time.time()
            diff_time = 0
            while diff_time < self._sounding_time:
                winsound.PlaySound(SOUND_FILE_NAME, winsound.SND_FILENAME)
                diff_time = time.time() - start_time
                time.sleep(0.15)
            winsound.PlaySound(None, winsound.SND_FILENAME | winsound.SND_PURGE)
        else:
            winsound.PlaySound(SOUND_FILE_NAME, winsound.SND_FILENAME)

    def stop_alarm(self):
        self._sounding_time = 0
        winsound.PlaySound(None, winsound.SND_FILENAME | winsound.SND_PURGE)


if __name__ == "__main__":
    obj = SoundAlarm(10)
    obj.start_alarm()
    import base64

    # file = open(SOUND_Q_FILE_NAME, "rb")
    # sound = base64.b64encode(file.read())
    # print(sound)
    # file.close()
    pass


