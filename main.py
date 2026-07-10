if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("app.main:app", port=5000, host="0.0.0.0")