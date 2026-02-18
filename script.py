from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pydicom.sequence import Sequence
import pydicom
import pandas as pd
import datetime

df = pd.read_excel("measurements_nashi.xlsx")

unit_map = {
    '122198': 'mmhg',
    '11726-7': 'm/s',
    '18015-8': 'cm',
    '18026-5': 'ml',
    '18038-0': '%',
    'default': 'cm'
}

img = pydicom.dcmread("echo_output.dcm")
print(f"📋 Study UID: {img.StudyInstanceUID}")
print(f"📋 Series UID: {img.SeriesInstanceUID}")
print(f"📋 Patient: {img.PatientName} ({img.PatientID})")


file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.88.33' # SR Measurement Report
file_meta.MediaStorageSOPInstanceUID = generate_uid()
file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

ds = FileDataset("FINAL_NACRT.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)

ds.PatientID = img.PatientID
ds.PatientName = img.PatientName
ds.PatientBirthDate = getattr(img, "PatientBirthDate", "")
ds.PatientSex = getattr(img, "PatientSex", "")

ds.StudyInstanceUID = img.StudyInstanceUID
ds.SeriesInstanceUID = generate_uid()
ds.SeriesNumber = getattr(img, "SeriesNumber", 1) + 1
ds.StudyID = getattr(img, "StudyID", "")

ds.SOPInstanceUID = generate_uid()
ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.33'
ds.Modality = "SR"
ds.InstanceNumber = 1
ds.CompletionFlag = "COMPLETE"

now = datetime.datetime.now()
ds.ContentDate = now.strftime('%Y%m%d')
ds.ContentTime = now.strftime('%H%M%S')


root = Dataset()
root.ValueType = "CONTAINER"
root.ContinuityOfContent = "SEPARATE"

root_concept = Dataset()
root_concept.CodeValue = "121071"
root_concept.CodeMeaning = "Measurement Report"
root_concept.CodingSchemeDesignator = "DCM"
root.ConceptNameCodeSequence = Sequence([root_concept])

content_items = Sequence()




for i, row in df.iterrows():
    meas = Dataset()
    meas.ValueType = "TEXT"


    concept = Dataset()
    concept.CodeValue = str(row['code'])
    concept.CodeMeaning = str(row['description'])
    concept.CodingSchemeDesignator = str(row.get('scheme', 'SRT'))
    meas.ConceptNameCodeSequence = Sequence([concept])


    meas.TextValue = f"{float(row['value']):.2f} {unit_map.get(str(row['code']), 'cm')}"


    site = Dataset()
    site.ValueType = "CODE"

    site_concept = Dataset()
    site_concept.CodeValue = str(row.get('FindingSiteCodeValue', 'T-D0300'))
    site_concept.CodeMeaning = str(row.get('FindingSiteCodeMeaning', 'Aortic Valve'))
    site_concept.CodingSchemeDesignator = str(row.get('FindingSiteCodeScheme', 'SRT'))

    site_name = Dataset()
    site_name.CodeValue = "R-42001"
    site_name.CodeMeaning = "Finding Site"
    site_name.CodingSchemeDesignator = "SRT"

    site.ConceptNameCodeSequence = Sequence([site_name])
    site.ConceptCodeSequence = Sequence([site_concept])


    show_img = Dataset()
    show_img.ValueType = "IMAGE"

    img_concept = Dataset()
    img_concept.CodeValue = "113038"
    img_concept.CodeMeaning = "Show Image"
    img_concept.CodingSchemeDesignator = "SRT"
    show_img.ConceptNameCodeSequence = Sequence([img_concept])

    ref_item = Dataset()
    ref_item.ReferencedSOPClassUID = str(img.SOPClassUID)
    ref_item.ReferencedSOPInstanceUID = str(img.SOPInstanceUID)
    ref_item.ReferencedFrameNumber = 1

    show_img.ReferencedSOPSequence = Sequence([ref_item])


    meas.ContentSequence = Sequence([site, show_img])
    content_items.append(meas)

root.ContentSequence = content_items
ds.ContentSequence = Sequence([root])
ds.is_little_endian = True
ds.is_implicit_VR = False

ds.save_as("finalno.dcm")
