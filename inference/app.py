from torchvision import transforms
import torch
import io
from PIL import Image
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
)
from inference.modelClass import mnistNet

model = mnistNet()
model.load_state_dict(torch.load("inference/mnist_model.pth"))
model.eval()

transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((28, 28)),
    transforms.ToTensor()
])

app = FastAPI()


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type. Only images are allowed")
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("L")
        image = transform(image).unsqueeze(0)
        with torch.no_grad():
            output = model(image)
        predicted_digit = torch.argmax(output, dim=1).item()
        return {"predicted_digit": predicted_digit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting digit: {e}")