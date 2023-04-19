import sys
sys.path.insert(0,'C:\\baecon')

import baecon as bc
import os

def main():
    args = bc.utils.arg_parser()
    
    meas_config = bc.utils.load_config(args.config_file)
    
    meas_settings = bc.make_measurement_settings(meas_config)
    
    if not args.engine== 'None':
        engine = bc.utils.load_module_from_path(args.engine)
        
        data = engine.perform_measurement(meas_settings)
    else:
        #run using the default engine
        data = bc.perform_measurement(meas_settings)

    save_file = args.output_file
    file_format = os.path.splitext(save_file)[-1]
    bc.utils.save_baecon_data(data, save_file, format=file_format)    
    return
    
if __name__ == '__main__':
    main()