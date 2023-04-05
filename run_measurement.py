import baecon as bc

def main():
    
    config = bc.utils.load_config()
    
    meas_settings = bc.make_measurement_settings(config)
    
    data = do_measurement(meas_settings)

    return data
    
