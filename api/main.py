from fastapi import FastAPI

def main():
    print("Hello from api!")

if __name__ == "__main__":
    main()

app = FastAPI()

@app.get("/health")

def health():
    return {"status": "ok"}