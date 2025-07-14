import os
import re
import csv
import json
from pathlib import Path
from slugify import slugify
from schemas.main_schemas import GeneratedPost


from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pyairtable import Api

# Path to the output CSV file
OUTPUT_FILE_PATH = Path("generated_posts.csv")


def write_to_airtable(post_data: dict):
    """Create a new record in Airtable with the provided post data."""
    try:
        api_key = os.getenv("AIRTABLE_API_KEY")
        base_id = os.getenv("AIRTABLE_BASE_ID")
        table_id = os.getenv("AIRTABLE_TABLE_ID")

        api = Api(api_key)
        table = api.table(base_id, table_id)

        # Prepare the fields to create in Airtable
        fields_to_create = {
            "Title": post_data.get("title", "No Title"),
            "Slug": post_data.get("slug", ""),
            "Description": post_data.get("description", ""),
            "Content": post_data.get("content", ""),
            "SEO Title": post_data.get("seo", {}).get("title", ""),
            "SEO Description": post_data.get("seo", {}).get("description", ""),
            "FAQ": json.dumps(post_data.get("faq", []), indent=2)
        }

        table.create(fields_to_create)
        print(f"Successfully created Airtable record for: {post_data.get('title')}")

    except Exception as e:
        print(
            f"ERROR: Failed to write to Airtable. Please check your API key, Base ID, Table ID, and Field Names. Details: {e}")



def generate_toc_from_content(content: str) -> str:
    """ЗLooking for H2 headings in the content and generating a Table of Contents."""
    headings = re.findall(r"^##\s+(.*)", content, re.MULTILINE)
    toc_lines = [f"- [{title.strip()}](#{slugify(title.strip())})" for title in headings]
    return "\n".join(toc_lines)


def write_to_csv(post_data: dict):
    """Add new data to the CSV file."""
    file_exists = OUTPUT_FILE_PATH.is_file()
    flat_data = {
        "title": post_data.get("title"), "slug": post_data.get("slug"), "description": post_data.get("description"),
        "seo_title": post_data.get("seo", {}).get("title"),
        "seo_description": post_data.get("seo", {}).get("description"),
        "faq": " | ".join([f"Q: {item['title']} A: {item['description']}" for item in post_data.get("faq", [])]),
        "table_of_contents": post_data.get("tableOfContents"), "content_markdown": post_data.get("content"),
    }
    fieldnames = list(flat_data.keys())
    try:
        with open(OUTPUT_FILE_PATH, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(flat_data)
        print(f"Successfully wrote post '{flat_data['title']}' to {OUTPUT_FILE_PATH}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")


async def generate_blog_post_service(topic: str, style: str) -> dict:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    parser = PydanticOutputParser(pydantic_object=GeneratedPost)

    prompt_template = """
    You are an expert copywriter and SEO specialist. Your task is to generate a complete, high-quality blog post.
    Instructions:
    1.  The post must be about the topic: "{topic}".
    2.  The writing style must be: "{style}".
    3.  The main content should be in Markdown format. Use H2 (##) for main sections.
    4.  Generate all components as requested in the format instructions below.
    {format_instructions}
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["topic", "style"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    generated_post = await chain.ainvoke({"topic": topic, "style": style})

    response_data = generated_post.model_dump()
    response_data['slug'] = slugify(generated_post.title)
    response_data['tableOfContents'] = generate_toc_from_content(generated_post.content)

    # 1. Always write to CSV
    write_to_csv(response_data)

    # 2. Optionally write to Airtable if credentials are set
    if os.getenv("AIRTABLE_API_KEY") and os.getenv("AIRTABLE_BASE_ID") and os.getenv("AIRTABLE_TABLE_ID"):
        print("Airtable credentials found. Attempting to save the record...")
        write_to_airtable(response_data)
    else:
        print("Airtable credentials not found. Skipping Airtable integration.")

    return response_data