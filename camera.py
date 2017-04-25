import subprocess
from time import sleep, time
import signal

start = time()
class Video(object):
    def __init__(self, output_file, xPos=None, yPos=None, width=None, height=None):
        recording_args = [str(i) for i in ['recordmydesktop',
            "-x", xPos,
            "-y", yPos,
            "--height", height,
            "--width", width,
            "-o", output_file,
            "--no-sound"
        ]]

        self.process = subprocess.Popen(recording_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.process.send_signal(signal.SIGSTOP)

    def start(self):
        self.process.send_signal(signal.SIGCONT)

    def pause(self):
        self.process.send_signal(signal.SIGSTOP)

    def resume(self):
        self.process.send_signal(signal.SIGCONT)

    def stop(self):
        self.process.send_signal(signal.SIGINT)
