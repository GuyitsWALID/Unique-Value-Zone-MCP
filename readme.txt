# UVZ (Unique Value Zone) MCP Server

A Model Context Protocol (MCP) server for research and digital product creation.

## Features

- **identify_industry_niches** - Analyze industries and find niches
- **drill_uvz** - Deep dive into Unique Value Zones
- **research_uvz_topic** - Gather research from web sources
- **validate_uvz_demand** - Check market demand
- **generate_ebook_outline** - Create digital product outlines
- **expand_chapter** - Expand chapters into sections
- **generate_chapter_content** - Generate full chapter content
- **competitive_analysis** - Analyze competitors
- **generate_marketing_copy** - Create marketing materials

## Prerequisites

- Docker Desktop with MCP Toolkit
- Gemini API key (free at https://makersuite.google.com/app/apikey)

## Setup

1. Build: `docker build -t uvz-mcp-server .`
2. Set API key: `docker mcp secret set GEMINI_API_KEY="your-key"`
3. Add to custom catalog (see installation guide)
4. Configure Claude Desktop
5. Restart Claude

## Usage Examples

- "Find niches in the fitness industry"
- "What's the UVZ for home workouts for busy parents?"
- "Research content marketing strategies"
- "Generate an ebook outline about sustainable gardening"
- "Create a landing page for my course"

## Cost

- Free web search (DuckDuckGo)
- Gemini free tier: 60 req/min, 1500 req/day
- Estimated monthly cost: $0-5

## Support

Check logs: `docker logs [container-name]`
