import baecon as bc
from baecon import utils
from baecon.engine import *

import queue
import threading



meas_settings = bc.Measurement_Settings()

daq_config = utils.load_config('test_daq_config.toml')
bc.add_instrument(daq_config, 
                  meas_settings.acquisition_instruments)

sg_config = utils.load_config('test_sig_gen_config.toml')
bc.add_instrument(sg_config,
                  meas_settings.scan_instruments)

scan_settings_1 = utils.load_config('test_scan.toml')
bc.add_scan(scan_settings_1, meas_settings.scan_instruments['SG1'], meas_settings)

bc.save_measurement_config(meas_settings, 'test_measurement_settings.toml')

ms_config = utils.load_config('test_measurement_settings.toml')

loaded_meas_fig = bc.make_measurement_settings(ms_config)

abort_flag = abort()
data_cue = queue.Queue()
# scans = meas_settings.scan_collection
# acq_instruments = meas_settings.acquisition_instruments
# consecutive_measurement(scans, acq_instruments, data_cue, abort_flag)

meas_data = Measurement_Data()
meas_data.data_template = bc.create_data_template(meas_settings)

m_t=threading.Thread(target=measure_thread, args=(meas_settings, data_cue, abort_flag,))

d_t=threading.Thread(target=data_thread, args=(meas_data, data_cue, abort_flag,))

m_t.start()

d_t.start()