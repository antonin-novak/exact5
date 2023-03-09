# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from functions.measurement_DT9837 import measurement_DT9837
from functions.SynchSweptSine import SynchSweptSine


''' --------- Parameters --------- '''
fs = 48000                  # sample rate [Hz]
f1 = 20                     # start frequency [Hz]
f2 = 20e3                   # end frequency [Hz]
T = 8                       # time length of the swept-sine [s]
len_IR = 2**13              # length of the extracted impulse responses
N = 3                       # number of higher harmonics to be extracted


''' --------- SWEPT-SINE signal definition --------- '''
sss = SynchSweptSine(f1=f1, f2=f2, T=T, fs=fs)
# note that 'sss' is an object. To see the available methods check the class defined in './functions/SynchSweptSine.py'
x = np.concatenate((sss.signal, np.zeros(int(0.5*fs))))


''' --------- Measurement --------- '''
in_buffer = measurement_DT9837(x, fs)
u = np.array(in_buffer[0::4])
i = -np.array(in_buffer[1::4])

# Plot the recorded signal
fig, ax = plt.subplots()
ax.plot(i)
ax.set(title='Recorder signals')

''' --------- Extract spectra from swept-sine --------- '''
hi = sss.getIR(i)     # impulse response of channel 2

# estimate the latency of the sound card from the first (direct) channel
LATENCY = 0

Hs = sss.separate_IR(hi, N, n_samples=len_IR, latency=LATENCY)
f_axis = np.fft.rfftfreq(len_IR, 1/fs)


''' --------- Plot Spectra --------- '''
fig, ax = plt.subplots()
ax.semilogx(f_axis, 20*np.log10(np.abs(Hs.T)))
ax.set(xlim=(10, 10e3), ylim=(-80, 20))
ax.set(title='Higher Harmonic Frequency Responses')
ax.set(xlabel='Frequency [Hz]', ylabel='Magnitude [dB re 1 V]')
plt.show()

""" SAVE the result to a numpy zip (.npz) file  """
np.savez('HHFRF.npz', f_axis=f_axis, Hs=Hs)
