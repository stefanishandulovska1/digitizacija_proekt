from pydicom.dataset import Dataset, FileDataset
import pydicom
import numpy as np
from PIL import Image
import datetime


image = Image.open("echocardiography.jpg").convert("L")
pixel_array = np.array(image)


file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = pydicom.uid.UltrasoundImageStorage
file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
file_meta.ImplementationClassUID = pydicom.uid.generate_uid()


ds = FileDataset("echo_output.dcm", {},
                 file_meta=file_meta,
                 preamble=b"\0" * 128)


ds.PatientName = "Test^Patient"
ds.PatientID = "12345"
ds.Modality = "US"
ds.StudyInstanceUID = pydicom.uid.generate_uid()
ds.SeriesInstanceUID = pydicom.uid.generate_uid()
ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
ds.SOPClassUID = file_meta.MediaStorageSOPClassUID

ds.StudyDate = datetime.datetime.now().strftime('%Y%m%d')
ds.StudyTime = datetime.datetime.now().strftime('%H%M%S')


ds.Rows, ds.Columns = pixel_array.shape
ds.SamplesPerPixel = 1
ds.PhotometricInterpretation = "MONOCHROME2"
ds.PixelRepresentation = 0
ds.HighBit = 7
ds.BitsStored = 8
ds.BitsAllocated = 8

ds.PixelData = pixel_array.tobytes()


ds.is_little_endian = True
ds.is_implicit_VR = False


ds.save_as("echo_output.dcm", write_like_original=False)

