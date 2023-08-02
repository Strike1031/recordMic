import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import filedialog

class AudioRecorder:
    def __init__(self, loopback=False):
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 2
        self.fs = 44100
        self.filename = "output.wav"
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.is_recording = False
        self.loopback = loopback
        self.mic_input_device_index = None
        self.speaker_input_device_index = None

    def get_input_device_indexes(self):
        device_count = self.p.get_device_count()
        for i in range(device_count):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                if device_info['name'].lower().find('microphone') != -1:
                    self.mic_input_device_index = device_info['index']
                elif device_info['name'].lower().find('speakers') != -1:
                    self.speaker_input_device_index = device_info['index']

    def start_recording(self):
        self.get_input_device_indexes()
        if self.loopback:
            input_device_index = self.speaker_input_device_index
        else:
            input_device_index = self.mic_input_device_index

        self.stream = self.p.open(format=self.sample_format,
                                  channels=self.channels,
                                  rate=self.fs,
                                  frames_per_buffer=self.chunk,
                                  input=True,
                                  input_device_index=input_device_index)
        self.is_recording = True
        self.frames = []

        while self.is_recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def stop_recording(self):
        self.is_recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(self.frames))

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Audio Recorder")

        self.mic_recorder = AudioRecorder()
        self.speaker_recorder = AudioRecorder(loopback=True)

        self.label_mic = tk.Label(master, text="Mic Save path:")
        self.label_mic.pack()

        self.entry_mic = tk.Entry(master)
        self.entry_mic.pack(pady=10)
        self.entry_mic.insert(0, "mic_output.wav")

        self.label_speaker = tk.Label(master, text="Speaker Save path:")
        self.label_speaker.pack()

        self.entry_speaker = tk.Entry(master)
        self.entry_speaker.pack(pady=10)
        self.entry_speaker.insert(0, "speaker_output.wav")

        self.start_button = tk.Button(master, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Recording", command=self.stop_recording)
        self.stop_button.pack(pady=10)

        self.close_button = tk.Button(master, text="Close", command=master.quit)
        self.close_button.pack(pady=20)

    def start_recording(self):
        self.mic_recorder.filename = self.entry_mic.get()
        self.mic_thread = threading.Thread(target=self.mic_recorder.start_recording)
        self.mic_thread.start()

        self.speaker_recorder.filename = self.entry_speaker.get()
        self.speaker_thread = threading.Thread(target=self.speaker_recorder.start_recording)
        self.speaker_thread.start()

    def stop_recording(self):
        self.mic_recorder.stop_recording()
        self.mic_thread.join()

        self.speaker_recorder.stop_recording()
        self.speaker_thread.join()

root = tk.Tk()
gui = GUI(root)
root.mainloop()