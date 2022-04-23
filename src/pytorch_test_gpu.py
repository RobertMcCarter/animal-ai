#!python
import torch

x = torch.empty(5, 3)
print(x)

x = torch.zeros(5, 3, dtype=torch.long)
print(x)

works = torch.cuda.is_available()
print( "Is CUDA available: ", works)

num_devices = torch.cuda.device_count()
print( "Number of devices: ", num_devices )

device_name = torch.cuda.get_device_name(0)
print( "GPU device name: ", device_name )
