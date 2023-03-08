from time import sleep
from sys import stdout
from uldaq import (get_daq_device_inventory, DaqDevice, AInScanFlag, ScanStatus,
                   ScanOption, create_float_buffer, InterfaceType, AiInputMode)


def measurement_DT9837(x, fs, deviceID=0, inputRangeID=0, outputRangeID=0, log=True):
    daq_device = None
    ai_device = None
    status = ScanStatus.IDLE

    samples_per_channel = len(x)

    try:
        # Get descriptors for all of the available DAQ devices.
        devices = get_daq_device_inventory(InterfaceType.USB)

        # Create the DAQ device from the descriptor at the specified index.
        daq_device = DaqDevice(devices[deviceID])
        daq_device.connect(connection_code=0)

        # Get the AiDevice object and verify that it is valid.
        ai_device = daq_device.get_ai_device()
        ao_device = daq_device.get_ao_device()

        # Verify the specified device supports hardware pacing for analog input.
        ai_info = ai_device.get_info()
        ao_info = ao_device.get_info()

        input_mode = AiInputMode.SINGLE_ENDED

        # Get a list of supported ranges and validate the range index.
        ai_range = ai_info.get_ranges(input_mode)[inputRangeID]
        ao_range = ao_info.get_ranges()[outputRangeID]

        # Allocate a buffer to receive the data.
        in_buffer = create_float_buffer(4, samples_per_channel)
        out_buffer = create_float_buffer(1, samples_per_channel)

        # Populate buffer data
        for i in range(len(x)):
            out_buffer[i] = x[i]

        # Start the acquisition.
        ai_device.a_in_scan(0, 3, input_mode,
                            ai_range, samples_per_channel,
                            fs, ScanOption.DEFAULTIO, AInScanFlag.DEFAULT, in_buffer)
        ao_device.a_out_scan(0, 0,
                             ao_range, samples_per_channel,
                             fs, ScanOption.DEFAULTIO,
                             AInScanFlag.DEFAULT, out_buffer)

        try:
            while True:
                try:
                    # Get the status of the background operation
                    status, transfer_status = ai_device.get_scan_status()
                    if (status != ScanStatus.RUNNING):
                        break

                    # reset cursor
                    if log:
                        stdout.write('\033[1;1H')
                        print('Acquired samples = ',
                              transfer_status.current_scan_count)

                    sleep(0.1)

                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass

    except RuntimeError as error:
        print('\n', error)

    finally:
        if daq_device:
            # Stop the acquisition if it is still running.
            if status == ScanStatus.RUNNING:
                ai_device.scan_stop()
            if daq_device.is_connected():
                daq_device.disconnect()
            daq_device.release()

        return in_buffer


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    fs = 48e3  # sample rate [Hz]

    # sine signal excitation
    f0 = 1000  # frequency [Hz]
    T = 0.1  # time duration [s]
    A = 0.5  # amplitude [V]

    t = np.arange(0, T, 1/fs)
    x = np.sin(2*np.pi*f0*t)

    temp_buffer = measurement_DT9837(A*x, fs)
    in0 = np.array(temp_buffer[0::4])  # signal from input 0
    in1 = np.array(temp_buffer[1::4])  # signal from input 1
    in2 = np.array(temp_buffer[2::4])  # signal from input 2
    in3 = np.array(temp_buffer[3::4])  # signal from input 3

    fig, ax = plt.subplots()
    ax.plot(in0)
    plt.show()
