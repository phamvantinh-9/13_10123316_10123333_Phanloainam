
        raise HTTPException(status_code=503, detail=f"Cannot connect to AI Service: {str(e)}")