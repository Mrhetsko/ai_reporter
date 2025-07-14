from pydantic import BaseModel, Field
from typing import List, Optional


class BlogPostRequest(BaseModel):
    topic: str
    style: Optional[str] = Field("professional and engaging", description="The writing style for the blog post.")


class FAQItem(BaseModel):
    title: str = Field(description="The question for the FAQ item")
    description: str = Field(description="The answer for the FAQ item")


class SeoData(BaseModel):
    title: str = Field(description="SEO-optimized title, around 50-60 characters")
    description: str = Field(description="SEO-optimized meta description, around 150-160 characters")


class GeneratedPost(BaseModel):
    title: str = Field(description="The main title of the blog post")
    description: str = Field(description="A short introduction for the post, 2-4 sentences")
    content: str = Field(
        description="The full blog post content in Markdown format. Use H2 (##) for main sections and include URL-friendly anchors like {#anchor-name}.")
    faq: List[FAQItem] = Field(description="A list of 3-4 frequently asked questions with their answers.")
    seo: SeoData = Field(description="SEO metadata for the blog post.")


class BlogPostResponse(GeneratedPost):
    slug: str
    tableOfContents: str
