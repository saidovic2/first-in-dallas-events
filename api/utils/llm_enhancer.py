"""
LLM Description Enhancer for Event SEO (EEAT)
Generates unique, valuable descriptions that add context beyond the original source
"""
import httpx
import os

async def enhance_event_description(event_data: dict, api_key: str = None) -> str:
    """
    Use LLM to create an enhanced, unique description for an event
    
    Strategy:
    1. Add local context (Dallas-specific insights)
    2. Include "What to Expect" section
    3. Add practical tips (parking, best time to arrive, etc.)
    4. Include similar events or recommendations
    
    This creates unique value that the original source doesn't provide,
    helping with EEAT (Experience, Expertise, Authoritativeness, Trust)
    
    Args:
        event_data: Dict with keys: title, description, venue, city, category, price_tier
        api_key: OpenAI API key (optional, reads from env if not provided)
    
    Returns:
        Enhanced description as HTML
    """
    
    # Get API key from parameter or environment
    openai_key = api_key or os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        # If no API key, return original description with basic enhancements
        return _fallback_enhancement(event_data)
    
    # Build the prompt with SEO focus - conservative approach
    original_desc = event_data.get('description', '')
    venue = event_data.get('venue', 'TBA')
    city = event_data.get('city', 'Dallas')
    
    prompt = f"""You are a Dallas events expert and local insider writing for "First in Dallas" - the trusted guide to Dallas-Fort Worth events.

EVENT INFORMATION:
Title: {event_data['title']}
Original Description: {original_desc}
Venue: {venue}
Location: {city}
Category: {event_data.get('category', 'Event')}
Price: {event_data.get('price_tier', 'Paid')}

YOUR MISSION: Write a compelling, SEO-optimized event description that demonstrates LOCAL EXPERTISE and provides REAL VALUE beyond the basic event info.

E-E-A-T REQUIREMENTS (Experience, Expertise, Authoritativeness, Trust):

✅ EXPERIENCE: Write as a Dallas local who knows the scene
✅ EXPERTISE: Show deep knowledge of Dallas venues, neighborhoods, and event types  
✅ AUTHORITATIVENESS: Position First in Dallas as the go-to Dallas events authority
✅ TRUSTWORTHINESS: Give practical, helpful tips that show you care about attendees

CONTENT STRUCTURE:

<p>[Opening paragraph - Rewrite the event description in an engaging way that captures the essence. Make it compelling and conversational while keeping all key facts. 2-3 sentences.]</p>

<h3>What to Expect</h3>
<p>[Describe the experience in detail based on the event type. For comedy shows: typical show format, duration, atmosphere. For music: genre details, crowd vibe, venue acoustics. For festivals: activities, food options, layout. For sports: game dynamics, fan experience. Be specific to the EVENT TYPE. 3-4 sentences.]</p>

<h3>Venue & Location Insights</h3>
<p>[Provide Dallas-specific venue context. For Dallas Comedy Club: mention it's on Elm St in Deep Ellum. For It'll Do Club: note it's a popular electronic music venue in Deep Ellum. For Arboretum: mention 66-acre gardens. For downtown venues: reference nearby landmarks (e.g., "near Reunion Tower"). Include neighborhood vibe. 2-3 sentences.]</p>

<h3>Getting There & Parking</h3>
<p>[Practical Dallas transit advice. Deep Ellum: Street parking fills up, recommend arriving early or using Pearl/Arts District DART station. Downtown: Mention DART light rail stations. Uptown: Note valet options. North Dallas: Plenty of free parking typically available. Generic tip: Arrive 30-45 minutes early for popular events. 2-3 sentences.]</p>

<h3>Insider Tips</h3>
<p>[Local recommendations. For comedy/music venues: "Grab dinner nearby before the show" or "Deep Ellum has great bars for pre/post-event drinks." For festivals: "Bring sunscreen and stay hydrated - Dallas summers are hot!" For family events: "Kid-friendly and stroller accessible." Show you KNOW Dallas. 2-3 sentences.]</p>

SEO BEST PRACTICES:
- Naturally use: "Dallas events", "{venue}", "{city}", event type keywords
- Write for humans first, search engines second
- Use conversational, helpful tone
- Total length: 350-450 words (substantive content)
- Include specific Dallas neighborhoods, landmarks, transit options

TONE: Friendly local expert sharing insider knowledge. Professional but conversational.

Output ONLY clean HTML with <p> and <h3> tags. No markdown, no title/h1, no extra formatting."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "You are a Dallas events expert and local insider. Write helpful, detailed content that demonstrates real local knowledge and expertise. Be specific about Dallas venues, neighborhoods, and practical tips."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,  # Higher for more creative, engaging content
                    "max_tokens": 1200  # Longer content for E-E-A-T
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced = result["choices"][0]["message"]["content"]
                
                # Clean up any markdown artifacts
                enhanced = enhanced.strip()
                # Remove code block markers if present
                if enhanced.startswith("```html"):
                    enhanced = enhanced[7:]
                if enhanced.startswith("```"):
                    enhanced = enhanced[3:]
                if enhanced.endswith("```"):
                    enhanced = enhanced[:-3]
                
                # Remove any stray ** or `` at the start
                enhanced = enhanced.lstrip("*`")
                
                # Force black color on all text elements to ensure visibility
                import re
                # Add inline color to all <p> tags
                enhanced = re.sub(r'<p>', r'<p style="color: #000000 !important;">', enhanced)
                # Add inline color to all <h3> tags
                enhanced = re.sub(r'<h3>', r'<h3 style="color: #000000 !important;">', enhanced)
                # Add inline color to all <h2> tags if present
                enhanced = re.sub(r'<h2>', r'<h2 style="color: #000000 !important;">', enhanced)
                
                return enhanced.strip()
            else:
                print(f"OpenAI API error: {response.status_code}")
                return _fallback_enhancement(event_data)
                
    except Exception as e:
        print(f"LLM enhancement failed: {e}")
        return _fallback_enhancement(event_data)


def _fallback_enhancement(event_data: dict) -> str:
    """
    Fallback enhancement when LLM is not available
    Adds basic structured content to improve upon the original description
    """
    original_desc = event_data.get('description', '')
    venue = event_data.get('venue', 'the venue')
    city = event_data.get('city', 'Dallas')
    category = event_data.get('category', 'event')
    
    enhanced = f"<p>{original_desc}</p>"
    
    # Add venue context
    if venue and venue != 'TBA':
        enhanced += f"\n<p><strong>Location Highlights:</strong> This event takes place at {venue} in {city}. "
        
        # Add venue-specific tips (you can expand this with a database of venues)
        if "arboretum" in venue.lower():
            enhanced += "The Dallas Arboretum offers free parking and beautiful gardens to explore before or after the event.</p>"
        elif "museum" in venue.lower():
            enhanced += "Consider arriving early to explore other exhibits at the museum.</p>"
        elif "downtown" in venue.lower() or "dallas" in venue.lower():
            enhanced += "Street parking can be limited - we recommend using nearby parking garages or public transit.</p>"
        else:
            enhanced += "</p>"
    
    # Add category-specific context
    category_tips = {
        "Music": "Arrive early for the best seats and to enjoy the venue's atmosphere.",
        "Sports": "Check the weather forecast and dress accordingly for outdoor events.",
        "Family & Kids": "Perfect for families! Remember to bring snacks and entertainment for waiting times.",
        "Arts & Theatre": "Some venues have a dress code - check ahead to ensure you're appropriately dressed.",
        "Food & Dining": "Make reservations in advance as popular events tend to sell out quickly."
    }
    
    if category in category_tips:
        enhanced += f"\n<p><strong>Tip:</strong> {category_tips[category]}</p>"
    
    return enhanced
