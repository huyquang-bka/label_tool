import torch

# Model
model = torch.load('yolov5n.pt')

# Images
img = 'data/images/bus.jpg' 

# Inference
results = model(img)

# Results
results.show()