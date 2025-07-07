import os
import threading
import subprocess
from fastapi import FastAPI
from routes.inference import router

MODEL_DIR = "./app/trainer/t5-trained"

def run_training():
    subprocess.run("python", "app/trainer/trainer.py")

app = FastAPI()
app.include_router(router)

print("Checking if trained model is available...")
if not os.path.exists(MODEL_DIR):
    print("Trained model not available, starting trainer in another thread...")
    threading.Thread(target=run_training, daemon=True).start()
else:
    print("Trained model available.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000) 