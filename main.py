import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas.main_schemas import BlogPostRequest, BlogPostResponse
from services import generate_blog_post_service

load_dotenv()

app = FastAPI(
    title="AI Blog Post Generator",
    description="Generates blog posts in a structured JSON format.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/generate-blog-post", response_model=BlogPostResponse, tags=["Blog Generation"])
async def create_blog_post(request: BlogPostRequest):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        result = await generate_blog_post_service(request.topic, request.style)
        return result
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse('static/index.html')