import os
from openai import OpenAI
from app.models import Property, Contact

# Initialize OpenAI client with OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def generate_comparison_summary(property1: Property, property2: Property) -> str:
    """
    Generate an AI-powered comparison summary between two properties.
    
    Args:
        property1: First property to compare
        property2: Second property to compare
        
    Returns:
        A detailed comparison summary as a string
    """
    
    # Create a detailed prompt for the LLM
    prompt = f"""
You are a professional real estate agent helping clients compare properties. 
Analyze these two properties and provide a comprehensive comparison summary.

Property 1 (ID: {property1.id}):
- Address: {property1.address}
- Price: {property1.price:,.0f} DZD
- Area: {property1.area_sqm} m²
- Type: {property1.property_type}
- Rooms: {property1.number_of_rooms}
- Description: {property1.description or "No description available"}

Property 2 (ID: {property2.id}):
- Address: {property2.address}
- Price: {property2.price:,.0f} DZD
- Area: {property2.area_sqm} m²
- Type: {property2.property_type}
- Rooms: {property2.number_of_rooms}
- Description: {property2.description or "No description available"}

Please provide:
1. A brief overview highlighting the key differences
2. Value analysis (price per square meter comparison)
3. Pros and cons of each property
4. A recommendation based on different buyer profiles (e.g., families, investors, first-time buyers)

Keep the summary professional, concise, and helpful for decision-making. Limit to 300-400 words.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional real estate agent with expertise in property analysis and client advisory."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Fallback summary if LLM fails
        price_diff = abs(property1.price - property2.price)
        area_diff = abs(property1.area_sqm - property2.area_sqm)
        
        fallback_summary = f"""
**Comparison Summary**

Property #{property1.id} vs Property #{property2.id}:

**Price Difference:** {price_diff:,.0f} DZD
**Area Difference:** {area_diff} m²

Property #{property1.id} offers {property1.area_sqm} m² at {property1.price/property1.area_sqm:,.0f} DZD/m².
Property #{property2.id} offers {property2.area_sqm} m² at {property2.price/property2.area_sqm:,.0f} DZD/m².

Both properties are located in different areas and offer unique advantages. 
Consider your budget, space requirements, and location preferences when making your decision.

*Note: AI summary temporarily unavailable. Please consult with your agent for detailed analysis.*
"""
        return fallback_summary.strip()

def test_llm_connection() -> bool:
    """
    Test if the LLM service is available and working.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, this is a test message."}],
            max_tokens=10
        )
        return True
    except Exception:
        return False 

def generate_personalized_recommendation(properties: list[Property], contact: Contact) -> str:
    """
    Generate an AI-powered personalized recommendation for multiple properties based on contact preferences.
    
    Args:
        properties: List of properties to compare (2-3 properties)
        contact: Contact with preferences to match against
        
    Returns:
        A detailed personalized recommendation as a string
    """
    
    # Build property details for the prompt
    property_details = []
    for i, prop in enumerate(properties, 1):
        property_details.append(f"""
Property {i} (ID: {prop.id}):
- Address: {prop.address}
- Price: {prop.price:,.0f} DZD
- Area: {prop.area_sqm} m²
- Type: {prop.property_type}
- Rooms: {prop.number_of_rooms}
- Description: {prop.description or "No description available"}
""")
    
    # Build contact preferences
    preferred_locations_str = ", ".join([f"{loc.name} ({loc.lat}, {loc.lon})" for loc in contact.preferred_locations])
    property_types_str = ", ".join(contact.property_types)
    
    # Create a detailed prompt for the LLM
    prompt = f"""
You are a professional real estate agent helping a client choose between multiple properties. 
Analyze these properties against the client's specific preferences and provide a personalized recommendation.

CLIENT PROFILE:
- Name: {contact.name}
- Budget Range: {contact.min_budget:,.0f} - {contact.max_budget:,.0f} DZD
- Preferred Area: {contact.min_area_sqm} - {contact.max_area_sqm} m²
- Minimum Rooms: {contact.min_rooms}
- Preferred Property Types: {property_types_str}
- Preferred Locations: {preferred_locations_str}

PROPERTIES TO COMPARE:
{"".join(property_details)}

Please provide:
1. **Preference Match Analysis**: How well each property matches the client's stated preferences (budget, area, rooms, type, location)
2. **Ranking & Recommendation**: Rank the properties from best to worst match with clear reasoning
3. **Pros and Cons**: For each property, highlight what the client would love and what might be concerns
4. **Final Recommendation**: Your top recommendation with specific reasons why it's the best fit for this client
5. **Alternative Considerations**: If the top choice has limitations, suggest what the client should consider

Keep the analysis professional, data-driven, and focused on the client's specific needs. Limit to 400-500 words.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional real estate agent with expertise in matching client preferences to suitable properties. You provide data-driven, personalized recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Fallback recommendation if LLM fails
        fallback_summary = f"""
**Personalized Property Recommendation for {contact.name}**

**Budget Analysis:**
"""
        
        for i, prop in enumerate(properties, 1):
            budget_fit = "✓" if contact.min_budget <= prop.price <= contact.max_budget else "✗"
            area_fit = "✓" if contact.min_area_sqm <= prop.area_sqm <= contact.max_area_sqm else "✗"
            rooms_fit = "✓" if prop.number_of_rooms >= contact.min_rooms else "✗"
            type_fit = "✓" if prop.property_type in contact.property_types else "✗"
            
            fallback_summary += f"""
Property {i}: Budget {budget_fit} | Area {budget_fit} | Rooms {rooms_fit} | Type {type_fit}
- Price: {prop.price:,.0f} DZD (Budget: {contact.min_budget:,.0f} - {contact.max_budget:,.0f} DZD)
- Area: {prop.area_sqm} m² (Preferred: {contact.min_area_sqm} - {contact.max_area_sqm} m²)
"""
        
        fallback_summary += f"""

*Note: AI analysis temporarily unavailable. Please consult with your agent for detailed personalized recommendations.*
"""
        return fallback_summary.strip() 