import baecon as bc
from baecon.engine import perform_measurement

import queue
import threading


meas_settings = bc.Measurement_Settings()

daq_config = bc.utils.load_config('tests\\test_daq_config.toml')
bc.add_device(daq_config, meas_settings.acquisition_devices)

sg_config = bc.utils.load_config('tests\\test_sig_gen_config.toml')
bc.add_device(sg_config, meas_settings.scan_devices)

scan_settings_1 = bc.utils.load_config('tests\\test_scan.toml')
bc.add_scan(scan_settings_1, meas_settings.scan_devices['SG1'], meas_settings)

bc.utils.save_measurement_config(meas_settings, 'tests\\test_measurement_settings.toml')

ms_config = bc.utils.load_config('tests\\test_measurement_settings.toml')

loaded_meas_fig = bc.make_measurement_settings(ms_config)

# abort_flag = abort()
# data_cue = queue.Queue()
# # scans = meas_settings.scan_collection
# # acq_devices = meas_settings.acquisition_devices
# # consecutive_measurement(scans, acq_devices, data_cue, abort_flag)

# meas_data = Measurement_Data()
# meas_data.data_template = bc.create_data_template(meas_settings)

# m_t=threading.Thread(target=measure_thread, args=(meas_settings, data_cue, abort_flag,))

# d_t=threading.Thread(target=data_thread, args=(meas_data, data_cue, abort_flag,))

# m_t.start()

# d_t.start()

data = perform_measurement(meas_settings)
