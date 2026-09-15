import pyaudio
import wave
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
import toolkit
import os


original_wave_file_name = "../original_audio.wav"
downsampled_wave_file_name = "../downsampled_audio.wav"
audio_format = '3gp'
bitrate="46k"
bitrate="128k"
compressed_file_name = os.path.join(toolkit.root_path, f"compressed_audio_{bitrate}.{audio_format}")

def record():
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second
    seconds = 3
    filename = original_wave_file_name

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


def down_sample_wave():
    # Retrieve the data from the wav file
    data, samplerate = sf.read(original_wave_file_name)
    print("Sample rate : {} Hz".format(samplerate))

    n = len(data) #the length of the arrays contained in data
    # Working with stereo audio, there are two channels in the audio data.
    # Let's retrieve each channel seperately:
    ch1 = np.array([data[i][0] for i in range(n)]) #channel 1
    ch2 = np.array([data[i][1] for i in range(n)]) #channel 2

    ch1_Fourier = np.fft.fft(ch1)  # performing Fast Fourier Transform
    abs_ch1_Fourier = np.absolute(ch1_Fourier[:n // 2])  # the spectrum
    # plt.plot(np.linspace(0, samplerate / 2, n // 2), abs_ch1_Fourier)
    # plt.ylabel('Spectrum')
    # plt.xlabel('$f$ (Hz)')
    # plt.show()

    eps = 1e-5
    # Boolean array where each value indicates whether we keep the corresponding frequency
    frequenciesToRemove = (1 - eps) * np.sum(abs_ch1_Fourier) < np.cumsum(abs_ch1_Fourier)
    # The frequency for which we cut the spectrum
    f0 = (len(frequenciesToRemove) - np.sum(frequenciesToRemove)) * (samplerate / 2) / (n / 2)
    print("f0 : {} Hz".format(int(f0)))
    # Displaying the spectrum with a vertical line for f0
    # plt.axvline(f0, color='r')
    # plt.plot(np.linspace(0, samplerate / 2, n // 2), abs_ch1_Fourier)
    # plt.ylabel('Spectrum')
    # plt.xlabel('$f$ (Hz)')
    # plt.show()



    # Then we define the downsampling factor
    down_sample_parameter = int(samplerate / f0)
    print("Downsampling factor : {}".format(down_sample_parameter))
    new_data = data[::down_sample_parameter, :]  # getting the downsampled data
    # Writing the new data into a wav file
    sf.write(downsampled_wave_file_name, new_data, int(samplerate / down_sample_parameter), 'PCM_16')

    sdf=4


def export_mp3():
    sound = AudioSegment.from_file(original_wave_file_name, format="wav")

    file_handle = sound.export(compressed_file_name,
                               format=audio_format,
                               bitrate = bitrate
                               )



if __name__ == '__main__':
    # record()
    # down_sample_wave()
    export_mp3()
