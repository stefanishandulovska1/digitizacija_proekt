import pydicom
img = pydicom.dcmread("echo_output.dcm")
print("Class:", img.SOPClassUID)
print("Instance:", img.SOPInstanceUID)
