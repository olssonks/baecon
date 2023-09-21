from pypylon import pylon
from pypylon import genicam
import cv2
import numpy as np

import sys

from baecon import Device


class Basler(Device):
    def __init__(self, configuration: dict):
        camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())

        camera.Open()

        match configuration:

            case acq_continuous:
                %rename(AcquireContinuousConfiguration) Pylon::CAcquireContinuousConfiguration;
                %rename(InstantCamera) Pylon::CInstantCamera;
                %include <pylon/AcquireContinuousConfiguration.h>
            
            case acq_single:
                %rename(InstantCamera) Pylon::CInstantCamera;
                %rename(AcquireSingleFrameConfiguration) Pylon::CAcquireSingleFrameConfiguration;
                %include <pylon/AcquireSingleFrameConfiguration.h>

            case action_trigger:
                %rename(ActionTriggerConfiguration) Pylon::CActionTriggerConfiguration;
                %rename(InstantCamera) Pylon::CInstantCamera;

                // SWIG does not understand code like this: 'const T var_name(init_value);'
                // But it does understand: 'const T var_name = init_value;'
                // In the case of 'const uint32_t AllGroupMask(0xffffffff);' we transform the
                // former to the latter with this macro:
                #define AllGroupMask(x) AllGroupMask=x

               
                %ignore ActionParameter;


                %include <pylon/gige/ActionTriggerConfiguration.h>

            case _:
                #default case



        

        return

    # Writing and Reading will be device specfic as connect types and command are all different
    def grabOne(self, parameter, value):
        """Add functionally to change the `parameter` to `value` on the
            instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """

        # enable all chunks
        camera.ChunkModeActive = True

        for cf in camera.ChunkSelector.Symbolics:
            camera.ChunkSelector = cf
            camera.ChunkEnable = True

        result = camera.GrabOne(100)
        print("Mean Gray value:", numpy.mean(result.Array[0:20, 0]))

        def ChunksOnResult(result):
            ret = ""
            for f in camera.ChunkSelector.Symbolics:
              try:
                  if genicam.IsAvailable(getattr(result, "Chunk" + f)):
                     ret += f + ","
              except AttributeError as e:
                    # some cameras have chunkselectors which never occur in the video stream
                    print(e)
        return ret


        print(ChunksOnResult(result))

        return
    
    def opencv(self, parameter, value):

        # Grabing Continusely (video) with minimal delay
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
        converter = pylon.ImageFormatConverter()

        # converting to opencv bgr format
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                # Access the image data
                image = converter.Convert(grabResult)
                img = image.GetArray()
                cv2.namedWindow('title', cv2.WINDOW_NORMAL)
                cv2.imshow('title', img)
                k = cv2.waitKey(1)
                if k == 27:
                    break
            grabResult.Release()
            
        # Releasing the resource    
        camera.StopGrabbing()

        cv2.destroyAllWindows()    

        return 

    def read(self, parameter, value):
        """Add functionally to read the value of `parameter` from the instrument.

        Args:
            parameter (_type_): _description_
            value (_type_): _description_
        """
        return
