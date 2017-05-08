import subprocess
from time import sleep, time
import signal

start = time()
class Video(object):
    def __init__(self, output_file, xPos=None, yPos=None, width=None, height=None):
        self.output_file = output_file
        self.width = width
        self.height = height
        recording_args = [str(i) for i in ['recordmydesktop',
            "-x", xPos,
            "-y", yPos,
            "--height", height,
            "--width", width,
            "-o", '{}.ogv'.format(self.output_file),
            "--no-sound",
            #"--full-shots",
            "--no-cursor"
        ]]

        self.process = subprocess.Popen(recording_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.process.send_signal(signal.SIGSTOP)

    def start(self):
        self.process.send_signal(signal.SIGCONT)

    def pause(self):
        self.process.send_signal(signal.SIGSTOP)

    def resume(self):
        self.process.send_signal(signal.SIGCONT)

    def _make_thumb(self):
        command = [
            'ffmpeg',
            '-ss', '0.0',
            '-i', '{}.mp4'.format(self.output_file),
            '-t', '1',
            '-s', '{}x{}'.format(int(self.width/10), int(self.height/10)),
            '-f', 'image2', '{}.png'.format(self.output_file),
            '-loglevel', 'fatal',
        ]
        subprocess.Popen(command)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        self.process.send_signal(signal.SIGINT)
        self.process.communicate()
        command = [
            'ffmpeg',
            '-i', '{}.ogv'.format(self.output_file),
            '-c:v', 'libx264',
            '-loglevel', 'fatal',
            '{}.mp4'.format(self.output_file)
        ]
        process = subprocess.Popen(command)#, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        self._make_thumb()
