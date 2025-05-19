import litellm
from pymongo import MongoClient
import json
from dotenv import load_dotenv
import os
from typing import Dict, Any

load_dotenv()

# Initialize clients
litellm_api_key= os.getenv("LITELLM_API_KEY")
litellm_base_url= os.getenv("LITELLM_BASE_URL")
azure_deployment_id = os.getenv("AZURE_DEPLOYMENT_ID")
azure_api_version = os.getenv("AZURE_API_VERSION")
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
mongo_database = os.getenv("MONGO_DATABASE")
db = mongo_client.get_database(mongo_database)
collection = db.get_collection("Recommendation")

SYSTEM_PROMPT = """
You are an expert real estate assistant that converts search queries into MongoDB filters.

Your tasks:
1. Analyze if the query has complete information for a property search
2. If incomplete, ask specific clarifying questions
3. If complete, convert to MongoDB filter JSON

Required fields for a complete search:
- Property type (flat, house, etc.) or BHK
- Location (area, city, etc.)
- Budget/price range

Rules for conversion:
1. Return JSON with "status" ("complete" or "incomplete")
2. If "incomplete", include "question" to ask for missing info
3. If "complete", include "filters" with MongoDB query
4. Use proper field names: flatType, locality, price
5. For numbers, ensure numeric values (not strings)

Example outputs:
User: "I want a flat"
{
  "status": "incomplete",
  "question": "What BHK configuration are you looking for, and in which area? Also, what's your budget range?"
}

User: "3BHK in Gachibowli under 20k"
{
  "status": "complete",
  "filters": {
    "flatType": "3BHK",
    "locality": {"$regex": "gachibowli", "$options": "i"},
    "price": {"$lte": 20000}
  }
}

User: "luxury apartments"
{
  "status": "incomplete",
  "question": "In which area are you looking for luxury apartments? What's your preferred BHK size and budget?"
}
"""

def analyze_query(query: str, conversation_history: list = []) -> Dict[str, Any]:
    """Analyze if query has complete info or needs clarification"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": query}
    ]
    
    response = litellm.completion(
        model="azure/" + azure_deployment_id,  # Use deployment name as model
        messages=messages,
        temperature=0,
        api_key=litellm_api_key,
        base_url=litellm_base_url,
    )
    
    try:
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        # print("\n[Error] Could not parse LLM response as JSON. Raw response:")
        # print(getattr(response.choices[0].message, 'content', response))
        # print("Exception:", e)
        return {"status": "error", "error": str(e), "raw_response": getattr(response.choices[0].message, 'content', response)}

def search_properties(filter_dict: Dict[str, Any]) -> list:
    """Search MongoDB with the provided filter"""
    return list(collection.find(filter_dict))

def format_results(properties: list) -> str:
    """Format properties for display"""
    if not properties:
        return "No properties found matching your criteria."
    
    result = []
    for prop in properties:
        prop_str = (
            f"Property Name : \"{prop.get('Property Name', 'N/A')}\"\n"
            f"flatType : \"{prop.get('flatType', 'N/A')}\"\n"
            f"locality : \"{prop.get('locality', 'N/A')}\"\n"
            f"Rent/Buy : \"{prop.get('Rent/Buy', 'N/A')}\"\n"
            f"Description : \"{prop.get('Description', 'N/A')}\"\n"
            f"price : {prop.get('price', 'N/A')}\n"
        )
        result.append(prop_str)
    
    return "\n".join(result)

def property_search_flow():
    """Interactive property search flow with clarification"""
    conversation_history = []
    filters = {}
    
    print("Welcome to Property Search! How can I help you?")
    # print("(Example: '3BHK in Gachibowli under 20k' or 'luxury villas in HITEC City')")
    
    while True:
        user_input = input("\nYour search query: ").strip()
        
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break
            
        # Analyze the query
        analysis = analyze_query(user_input, conversation_history)
        conversation_history.append({"role": "user", "content": user_input})

        # Handle error in LLM response
        if analysis.get("status") == "error":
            # print("\nSorry, there was an error understanding your request. The AI returned:\n")
            print(analysis.get("raw_response", "No response received."))
            # print("\nPlease try again or rephrase your query. If this keeps happening, check your LLM prompt to ensure it always returns valid JSON as specified in the instructions.")
            continue

        if analysis.get("status") == "incomplete":
            print("\n" + analysis["question"])
            conversation_history.append({"role": "assistant", "content": analysis["question"]})
            continue

        if analysis.get("status") == "complete" and "filters" in analysis:
            # We have complete filters
            filters = analysis["filters"]
            # print("Searching properties:", json.dumps(filters, indent=2))
            print("Searching properties:")

            # Execute search
            results = search_properties(filters)

            # Show results
            print("\n" + format_results(results))

            # Ask if user wants to refine search
            refine = input("\nWould you like to refine your search? (yes/no): ").lower()
            if refine in ('y', 'yes'):
                print("Please provide additional filters or modifications")
            else:
                print("Thank you for using Property Search!")
                break
        else:
            print("\nSorry, I could not process your request. Please try again.")
            continue

if __name__ == "__main__":
    property_search_flow()