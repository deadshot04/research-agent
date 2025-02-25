from crewai import Task
from config.settings import Config
import datetime
from pathlib import Path
from utils.docx_formatter import populate_template
import logging  
import re
import requests
import os

logger = logging.getLogger(__name__)

def report_generation_task(agent, topic=None):
    """Create a task for generating a research report."""
    topic = topic or Config.REPORT_CONFIG["default_topic"]
    output_dir = Path("output").absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_docx = output_dir / f"report_{timestamp}.docx"
    output_pdf = output_dir / f"report_{timestamp}.pdf"
    articles_pdf = fetch_articles_pdf(topic)
    related_links = fetch_related_links(topic)

    task = Task(
        description=f"Generate a comprehensive research report on '{topic}' including sections: {Config.REPORT_CONFIG['sections']}",
        expected_output=f"Comprehensive research content with proper headings, sections, related links, and article PDFs",
        agent=agent
    )
    
    task.output_docx = str(output_docx)
    task.output_pdf = str(output_pdf)
    task.articles_pdf = articles_pdf
    task.related_links = related_links
    task.async_execution = False  
    
    def process_result(result):
        format_report_docx(result, task.output_docx)
        format_report_pdf(result, task.output_pdf)
        
        logger.info(f"Related links for topic '{topic}':")
        for link in related_links:
            logger.info(link)
        
        return {
            "docx": task.output_docx,
            "pdf": task.output_pdf,
            "articles_pdf": articles_pdf,
            "related_links": related_links
        }
    
    task.callback = process_result
    return task

def fetch_related_links(topic, num_links=5):
    """Fetch related links for the given topic using Google Search."""
    try:
        return [url for url in search(topic, num_results=num_links)]
    except Exception as e:
        logger.error(f"Error fetching related links: {e}")
        return []

def fetch_articles_pdf(topic, num_articles=3):
    """Fetch PDF articles related to the given topic."""
    pdf_links = []
    try:
        search_results = search(f"{topic} filetype:pdf", num_results=num_articles)
        for url in search_results:
            if url.endswith(".pdf"):
                pdf_links.append(url)
    except Exception as e:
        logger.error(f"Error fetching article PDFs: {e}")
    
    return pdf_links

def split_response_into_dict(response):
    sections = re.split(r'\n\n\*\*([^*]+)\*\*\n\n', response)
    response_dict = {}
    
    if sections[0].strip():
        response_dict["Title"] = sections[0].strip()
    
    for i in range(1, len(sections), 2):
        heading = sections[i].strip()
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""
        response_dict[heading] = content
    
    return response_dict