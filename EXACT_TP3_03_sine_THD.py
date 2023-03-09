# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from functions.measurement_DT9837 import measurement_DT9837


''' --------- Parameters --------- '''
fs = 48000                  # sample rate [Hz]

''' --------- SINE signal definition --------- '''
f0 = 300                    # frequency [Hz]
T = 2                       # time duration [s]
t = np.arange(0, T, 1/fs)   # time axis
x = np.sin(2*np.pi*f0*t)    # signal definition


''' --------- Measurement --------- '''
in_buffer = measurement_DT9837(x, fs)
i = np.array(in_buffer[1::4])[-fs:]

# Plot the recorded signal
fig, ax = plt.subplots()
ax.plot(i)
ax.set(title='Recorder signals')

''' --------- Calculate the FFT --------- '''
I = np.fft.rfft(i)/len(i)*2
f_axis = np.fft.rfftfreq(len(i), 1/fs)

''' --------- Plot Spectra --------- '''

# load the data from HHFRF measurement
data = np.load('HHFRF.npz')
f_axis2 = data['f_axis']
Hs = data['Hs']

fig, ax = plt.subplots()
ax.semilogx(f_axis2, 20*np.log10(np.abs(Hs.T)))
ax.semilogx(f_axis, 20*np.log10(np.abs(I)))
ax.set(xlim=(10, 10e3), ylim=(-80, 20))
ax.set(title='Higher Harmonic Frequency Responses')
ax.set(xlabel='Frequency [Hz]', ylabel='Magnitude [dB re 1 V]')
plt.show()
