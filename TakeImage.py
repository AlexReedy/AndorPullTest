from andorLib import *
from datetime import datetime

init_configs = {'handle': int(100),
                'serial': 26265,
                'dims': [2088, 2048],
                'read_mode': 4,
                'acq_mode': 1,
                'roi': [1, 1, 1, 2088, 1, 2048],
                'ad_channel': 0,
                'output_amp': 0,
                'shutter': [0, 0, 0, 0],
                'set_temp': -90,
                'fan_mode': 0,
                'cooler_mode': 1,
                'image_flip_states': [0, 0],
                'baseline_clamp_state': 0,
                'im_rot_state': 0,
                'frame_transfer_mode': 0,
                'k_cycle_time': 0.0,
                'photon_counting_state': 0,
                'vs_amplitude': 0,
                'vss_idx': 1,
                'pre_amp_gain_idx': 0,
                }

# Loads the Andor SDK and andorLib library
andor = Andor()
andor.loadLibrary()

# Gets Number of Cameras in System
n_cams = andor.GetAvailableCameras()

# Initializes the Camera
andor.Initialize()

# Retrieves Detector Dimensions from the Camera and Sets the config dict with the x,y values
dims = andor.GetDetector()
init_configs['dims'][0] = dims[0]
init_configs['dims'][1] = dims[1]

# Gets the pixel dimensions
pixel_size = andor.GetPixelSize()

# Sets Read Mode
andor.SetReadMode(mode=init_configs['read_mode'])

# Sets ACQ Mode
andor.SetAcquisitionMode(mode=init_configs['acq_mode'])

# Sets Frame Transfer Mode
andor.SetFrameTransferMode(mode=init_configs['frame_transfer_mode'])

# Sets Kinetic Cycle Time
andor.SetKineticCycleTime(KinCycTime=init_configs['k_cycle_time'])

# Sets Photon Counting Mode
andor.SetPhotonCounting(state=init_configs['photon_counting_state'])

# Sets Baseline Clamp Mode
andor.SetBaselineClamp(state=init_configs['baseline_clamp_state'])

# Sets Vertical Clock Voltage Amplitude
andor.SetVSAmplitude(state=init_configs['vs_amplitude'])

# Sets AD Channel
andor.SetADChannel(channel=init_configs['ad_channel'])

# Gets the AD Channel Bit Depth
ad_bit_depth = andor.GetBitDepth(init_configs['ad_channel'])

# Sets Image Flipping States for X,Y Axis
andor.SetImageFlip(iHFlip=init_configs['image_flip_states'][0],
                   iVFlip=init_configs['image_flip_states'][1])

# Sets Image Rotation Mode
andor.SetImageRotate(iRotate=init_configs['im_rot_state'])

# Sets Shutter Configuration
andor.SetShutter(typ=0,
                 mode=0,
                 closingtime=0,
                 openingtime=0
                 )

# Sets the Image ROI
andor.SetImage(hbin=init_configs['roi'][0],
               vbin=init_configs['roi'][1],
               hstart=init_configs['roi'][2],
               hend=init_configs['roi'][3],
               vstart=init_configs['roi'][4],
               vend=init_configs['roi'][5]
               )

# Sets Vertical Shift Speed
andor.SetVSSpeed(index=init_configs['vss_idx'])

# Sets Pre Amp Gain

# Sets the Fan Mode
andor.SetFanMode(mode=init_configs['fan_mode'])

# Sets the Cooling Mode
andor.SetCoolerMode(mode=init_configs['cooler_mode'])





