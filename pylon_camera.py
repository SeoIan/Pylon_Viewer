"""
파일명: pylon_camera.py
작성자: Ian
작성일: 2026-01-08
설명: 
    - @Korean       > Basler 카메라 제어
    
의존성:
    - PyPylon 
    - numpy         > PyPylon 의존 라이브러리
    - threading     > Event Handle 

버전 기록:
    v1.0 (2026-01-08) : 초기 버전 작성
"""

from pypylon import pylon
from pypylon import genicam
import threading

class ImageEventHandler(pylon.ImageEventHandler):
    _image : pylon.PylonImage = None
    _handle : threading.Event = None

    def __init__(self, image, handle):
        super().__init__()
        self._image = image
        self._handle = handle 

    def OnImageGrabbed(self, camera, grabResult):
        if grabResult.GrabSucceeded():
            self._image.AttachGrabResultBuffer(grabResult)
            self._handle.set()
    
    def OnImagesSkipped(self, camera, countOfSkippedImages):
        return super().OnImagesSkipped(camera, countOfSkippedImages)
    

class pylon_camera:
    __system : pylon.TlFactory = None
    _camera : pylon.InstantCamera = None
    _converter : pylon.ImageFormatConverter = None
    _width : int = 0
    _height : int = 0
    _is_open : bool = False
    _image_event_handler = None
    _image : pylon.PylonImage = None
    _converted_image : pylon.PylonImage = None
    _image_event_handle : threading.Event = None

    def __init__(self):
        self.__system = pylon.TlFactory.GetInstance()
        self._converter = pylon.ImageFormatConverter()
        self._converter.OutputPixelFormat = pylon.PixelType_RGB8packed
        self._converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        devices = self.__system.EnumerateDevices()
        if len(devices) == 0:
            raise pylon.RuntimeException("No camera present.")
        
        self._camera = None
        self._width = 0
        self._height = 0
        self._image_event_handle = threading.Event()

    def open_by_serialNumber(self, serialNumber):
        for dev_info in self.__system.EnumerateDevices():
            if dev_info.GetSerialNumber() == serialNumber:
                self._open(dev_info)
                break

        if self._camera == None:
            raise pylon.RuntimeException("No camera matched.")
        
    def open_by_IPAddress(self, ipAddress):
        for dev_info in self.__system.EnumerateDevices():
            if dev_info.GetIpAddress() == ipAddress:
                self._open(dev_info)
                break

        if self._camera == None:
            raise pylon.RuntimeException("No camera matched.")

    def _open(self, device_info):
        self._camera = pylon.InstantCamera(self.__system.CreateDevice(device_info))
        self._camera.Open()
        self._width = self._camera.Width.Value
        self._height = self._camera.Height.Value
        pixelformat = self._camera.PixelFormat.Value
        if pixelformat == "BayerRG8":
            self._image = pylon.PylonImage()
            self._image.Reset(pylon.PixelType_BayerRG8, self._width, self._height)
            self._converted_image = pylon.PylonImage()
            self._converted_image.Reset(pylon.PixelType_RGB8packed,self._width, self._height)
        elif pixelformat == "BayerGB8":
            self._image = pylon.PylonImage()
            self._image.Reset(pylon.PixelType_BayerGB8, self._width, self._height)
            self._converted_image = pylon.PylonImage()
            self._converted_image.Reset(pylon.PixelType_RGB8packed,self._width, self._height)
        elif pixelformat == "BayerGR8":
            self._image = pylon.PylonImage()
            self._image.Reset(pylon.PixelType_BayerGR8, self._width, self._height)
            self._converted_image = pylon.PylonImage()
            self._converted_image.Reset(pylon.PixelType_RGB8packed,self._width, self._height)
        elif pixelformat == "BayerGB8":
            self._image = pylon.PylonImage()
            self._image.Reset(pylon.PixelType_BayerGB8, self._width, self._height)
            self._converted_image = pylon.PylonImage()
            self._converted_image.Reset(pylon.PixelType_RGB8packed,self._width, self._height)
        elif pixelformat == "Mono8":
            self._image = pylon.PylonImage()
            self._image.Reset(pylon.PixelType_Mono8, self._width, self._height)
        elif pixelformat == "RGB8":
            self._image = pylon.PylonImage()
            self._image.Reset(pylon.PixelType_RGB8packed, self._width, self._height)
        else :
            raise pylon.RuntimeException("Not Support image format")
        self._is_open = True
        self._registerEvent()

    def close(self):
        self._deregisterEvent()
        self._camera.Close()
        self._is_open = False

    def start(self):
        self._camera.StartGrabbing(pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByInstantCamera)

    def stop(self):
        self._camera.StopGrabbing()

    def _registerEvent(self):
        if self._image_event_handler == None:
            self._image_event_handler = ImageEventHandler(self._image, self._image_event_handle)
        self._camera.RegisterImageEventHandler(self._image_event_handler, pylon.RegistrationMode_Append, pylon.Cleanup_Delete)

    def _deregisterEvent(self):
        self._camera.DeregisterImageEventHandler(self._image_event_handler)
        del self._image_event_handler

    def setValue(self, node, value):
        nodeMap = self._camera.GetNodeMap()
        node = nodeMap.GetNode(node)
        node.SetValue(value)

    def getValue(self, node):
        nodeMap = self._camera.GetNodeMap()
        node = nodeMap.GetNode(node)
        return node.GetValue()
        
    def executeCommand(self, node):
        nodeMap = self._camera.GetNodeMap()
        node = nodeMap.GetNode(node)
        node.Execute()

    def save(self, path):
        self._image.Save(pylon.ImageFileFormat_Bmp, path)

    @property
    def is_open(self):
        return self._is_open
    
    @property
    def is_grabbing(self):
        return self._camera.IsGrabbing()
    
    @property
    def grab_done(self):
        return self._image_event_handle

    @property
    def buffer(self):
        return self._image
    
    @property
    def color_buffer(self):
        self._converted_image = self._converter.Convert(self._image)
        return self._converted_image





    