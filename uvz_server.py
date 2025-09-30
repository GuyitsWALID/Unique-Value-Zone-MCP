#!/usr/bin/env python3
"""UVZ (Unique Value Zone) MCP Server - Research and Digital Product Creation"""
import os
import sys
import logging
import json
import re
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP
import google.generativeai as genai
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream=sys.stderr)
logger = logging.getLogger("uvz-server")
mcp = FastMCP("uvz")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    logger.warning("GEMINI_API_KEY not set")
    model = None

def sanitize_input(text):
    return re.sub(r'[^\w\s\-,.]', '', text)

async def web_search_free(query):
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=15, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for result in soup.find_all('div', class_='result', limit=10):
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                if title_elem:
                    results.append({'title': title_elem.get_text(strip=True), 'link': title_elem.get('href', ''), 'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ""})
            return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return json.dumps([])

async def gemini_analyze(prompt):
    if not model:
        return "Error: Gemini API key not configured"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def identify_industry_niches(industry="", depth="3"):
    """Analyze an industry and identify potential niches with UVZ opportunities using AI analysis."""
    if not industry.strip():
        return "Error: Industry name is required"
    if not model:
        return "Error: Gemini API key not configured"
    industry_clean = sanitize_input(industry)
    try:
        depth_int = int(depth) if depth.strip() else 3
        prompt = f"Analyze the {industry_clean} industry and identify {depth_int} highly specific niches. For each provide: 1. Niche Name 2. Market Size 3. Unique Value Zone (UVZ) 4. Target Audience 5. Differentiation 6. Monetization Potential. Format as structured markdown."
        analysis = await gemini_analyze(prompt)
        return f"Industry Analysis: {industry_clean}\n\n{analysis}\n\nNext Steps: Use drill_uvz to go deeper"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def drill_uvz(niche="", focus_area=""):
    """Drill down into a specific niche to identify the Unique Value Zone with laser precision."""
    if not niche.strip():
        return "Error: Niche description is required"
    if not model:
        return "Error: Gemini API key not configured"
    niche_clean = sanitize_input(niche)
    focus_clean = sanitize_input(focus_area) if focus_area.strip() else "general opportunities"
    try:
        prompt = f"Deep UVZ analysis for niche: {niche_clean}, focus: {focus_clean}. Provide: Problem Statement, Target Avatar, Current Solutions, The Gap, Value Proposition, Validation Signals, Competition Level, Monetization Pathways, Quick Win Strategy. Be extremely specific."
        analysis = await gemini_analyze(prompt)
        return f"UVZ Deep Dive: {niche_clean}\n\n{analysis}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def research_uvz_topic(topic="", sources="10"):
    """Research a UVZ topic using free web search and AI analysis to gather insights."""
    if not topic.strip():
        return "Error: Topic is required"
    topic_clean = sanitize_input(topic)
    try:
        num_sources = int(sources) if sources.strip() else 10
        search_results = await web_search_free(f"{topic_clean} guide tutorial best practices")
        results_data = json.loads(search_results)
        if not results_data:
            return f"No search results found for: {topic_clean}"
        sources_text = "\n\n".join([f"{i+1}. {r['title']}\n{r['snippet']}\n{r['link']}" for i, r in enumerate(results_data[:num_sources])])
        if model:
            analysis_prompt = f"Based on these search results about '{topic_clean}', provide: Key Insights, Common Themes, Best Practices, Knowledge Gaps, Content Opportunities.\n\n{sources_text}"
            ai_analysis = await gemini_analyze(analysis_prompt)
            return f"Research Report: {topic_clean}\n\nAI Analysis:\n{ai_analysis}\n\nSources:\n{sources_text}"
        return f"Research Results: {topic_clean}\n\nSources:\n{sources_text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def validate_uvz_demand(uvz_description=""):
    """Validate market demand for a UVZ by analyzing search trends discussions and market signals."""
    if not uvz_description.strip():
        return "Error: UVZ description is required"
    uvz_clean = sanitize_input(uvz_description)
    try:
        all_results = []
        for query in [f"{uvz_clean} problems", f"{uvz_clean} solutions needed", f"how to {uvz_clean}"]:
            results = await web_search_free(query)
            all_results.extend(json.loads(results)[:3])
        if not all_results:
            return f"Limited demand signals found for: {uvz_clean}"
        findings = "\n\n".join([f"{i+1}. {r['title']}\n{r['snippet']}" for i, r in enumerate(all_results)])
        if model:
            validation_prompt = f"Analyze market signals for: {uvz_clean}\n\n{findings}\n\nProvide: Demand Level, Market Signals, Competition Analysis, Opportunity Score (1-10), Red Flags, Green Lights, Recommended Action (Go/No-Go)."
            validation = await gemini_analyze(validation_prompt)
            return f"Demand Validation: {uvz_clean}\n\n{validation}\n\nRaw Signals:\n{findings}"
        return f"Market Signals: {uvz_clean}\n\n{findings}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_ebook_outline(topic="", audience="", length="50"):
    """Generate a comprehensive ebook outline for a digital product based on UVZ research."""
    if not topic.strip():
        return "Error: Topic is required"
    if not model:
        return "Error: Gemini API key not configured"
    topic_clean = sanitize_input(topic)
    audience_clean = sanitize_input(audience) if audience.strip() else "general audience"
    try:
        page_count = int(length) if length.strip() else 50
        prompt = f"Create comprehensive ebook outline for: Topic: {topic_clean}, Audience: {audience_clean}, Length: ~{page_count} pages. Include: Title, Subtitle, Target Reader, Chapter Structure (10+ chapters with objectives, sections, estimated pages), Unique Selling Points, Key Takeaways, Marketing Hooks."
        outline = await gemini_analyze(prompt)
        return f"Ebook Outline Generated\n\n{outline}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def expand_chapter(chapter_title="", key_points=""):
    """Expand a chapter from an ebook outline into detailed sections with talking points."""
    if not chapter_title.strip():
        return "Error: Chapter title is required"
    if not model:
        return "Error: Gemini API key not configured"
    chapter_clean = sanitize_input(chapter_title)
    points_clean = key_points if key_points.strip() else "Cover the main aspects"
    try:
        prompt = f"Expand chapter: {chapter_clean}. Key points: {points_clean}. Provide: Opening Hook, Introduction, Main Sections (3-7 with key concepts, talking points, examples, mistakes to avoid, action steps), Chapter Summary, Transition. Include estimated word count and supporting elements needed."
        expansion = await gemini_analyze(prompt)
        return f"Chapter Expansion: {chapter_clean}\n\n{expansion}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_chapter_content(chapter_title="", outline="", tone="professional"):
    """Generate full written content for a chapter based on the expanded outline."""
    if not chapter_title.strip() or not outline.strip():
        return "Error: Chapter title and outline required"
    if not model:
        return "Error: Gemini API key not configured"
    chapter_clean = sanitize_input(chapter_title)
    tone_clean = sanitize_input(tone)
    try:
        prompt = f"Write full chapter in {tone_clean} tone: {chapter_clean}\n\nOutline:\n{outline}\n\nRequirements: engaging prose, examples, subheadings, bullet points for lists, actionable takeaways, 2000-3000 words."
        content = await gemini_analyze(prompt)
        word_count = len(content.split())
        return f"Chapter Content: {chapter_clean}\n\n{content}\n\nStats: ~{word_count} words, {tone_clean} tone"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def competitive_analysis(uvz="", competitors="5"):
    """Analyze competitors in a UVZ space to identify differentiation opportunities."""
    if not uvz.strip():
        return "Error: UVZ description is required"
    uvz_clean = sanitize_input(uvz)
    try:
        num_competitors = int(competitors) if competitors.strip() else 5
        search_results = await web_search_free(f"{uvz_clean} courses guides products solutions")
        results_data = json.loads(search_results)
        if not results_data:
            return f"No competitors found for: {uvz_clean}"
        competitors_text = "\n\n".join([f"{i+1}. {r['title']}\n{r['snippet']}\n{r['link']}" for i, r in enumerate(results_data[:num_competitors])])
        if model:
            analysis_prompt = f"Analyze competitors for: {uvz_clean}\n\n{competitors_text}\n\nProvide: Market Saturation, Competitor Strengths, Weaknesses, Market Gaps, Differentiation Strategy, Positioning, Pricing Insights, Content Strategy."
            analysis = await gemini_analyze(analysis_prompt)
            return f"Competitive Analysis: {uvz_clean}\n\n{analysis}\n\nCompetitors:\n{competitors_text}"
        return f"Competitors: {uvz_clean}\n\n{competitors_text}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def generate_marketing_copy(product_title="", uvz="", copy_type="landing_page"):
    """Generate marketing copy for a digital product including landing page email sequences or social posts."""
    if not product_title.strip() or not uvz.strip():
        return "Error: Product title and UVZ required"
    if not model:
        return "Error: Gemini API key not configured"
    title_clean = sanitize_input(product_title)
    uvz_clean = sanitize_input(uvz)
    copy_type_clean = sanitize_input(copy_type)
    try:
        if copy_type_clean == "landing_page":
            prompt = f"Create high-converting landing page for: {title_clean}, UVZ: {uvz_clean}. Include: Hero (headline, subheadline, CTA), Problem, Solution, Benefits, Social Proof, Features, Guarantee, Final CTA, FAQ."
        elif copy_type_clean == "email_sequence":
            prompt = f"Create 5-email sequence for: {title_clean}, UVZ: {uvz_clean}. Each email: subject, preview, body (300-500 words), CTA. Emails: 1-Welcome, 2-Story+Problem, 3-Solution, 4-Social Proof, 5-Urgency."
        elif copy_type_clean == "social_posts":
            prompt = f"Create 10 social posts for: {title_clean}, UVZ: {uvz_clean}. Include 3 educational, 3 engagement, 2 promotional, 2 testimonial posts. Each: platform, text, hashtags, visual description."
        else:
            return "Error: Unknown copy type. Use: landing_page, email_sequence, or social_posts"
        copy_content = await gemini_analyze(prompt)
        return f"Marketing Copy: {copy_type_clean}\n\nProduct: {title_clean}\n\n{copy_content}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting UVZ MCP server...")
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set")
    else:
        logger.info("Gemini API configured")
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
