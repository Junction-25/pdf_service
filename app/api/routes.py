import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import List

from app.models import Property, Contact
from app.services import generate_comparison_pdf, generate_quote_pdf, generate_personalized_recommendation_pdf
from app.core.config import settings

router = APIRouter()

# --- DATA LOADING ---
# In a real app, this would be a database connection. For the hackathon, we load from JSON.
try:
    with open(settings.PROPERTIES_FILE, 'r', encoding='utf-8') as f:
        PROPERTIES_DB = {p['id']: Property(**p) for p in json.load(f)}
    with open(settings.CONTACTS_FILE, 'r', encoding='utf-8') as f:
        CONTACTS_DB = {c['id']: Contact(**c) for c in json.load(f)}
except FileNotFoundError:
    print(f"ERROR: Make sure '{settings.PROPERTIES_FILE}' and '{settings.CONTACTS_FILE}' exist.")
    PROPERTIES_DB, CONTACTS_DB = {}, {}


@router.get("/compare", tags=["PDF Generation"])
def compare_properties(
    property_id_1: int = Query(..., description="ID of the first property to compare."),
    property_id_2: int = Query(..., description="ID of the second property to compare.")
):
    """
    Generates a side-by-side PDF comparison of two properties with AI-powered analysis.
    """
    p1 = PROPERTIES_DB.get(property_id_1)
    p2 = PROPERTIES_DB.get(property_id_2)

    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="One or both property IDs not found.")

    pdf_bytes = generate_comparison_pdf(p1, p2)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=comparison_{property_id_1}_vs_{property_id_2}.pdf"}
    )


@router.get("/quote", tags=["PDF Generation"])
def generate_quote(
    property_id: int = Query(..., description="ID of the property to generate a quote for."),
    contact_id: int = Query(..., description="ID of the contact requesting the quote.")
):
    """
    Generates a personalized quote PDF for a specific property and contact.
    """
    property_obj = PROPERTIES_DB.get(property_id)
    contact_obj = CONTACTS_DB.get(contact_id)

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property ID not found.")
    if not contact_obj:
        raise HTTPException(status_code=404, detail="Contact ID not found.")

    pdf_bytes = generate_quote_pdf(property_obj, contact_obj)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=quote_{property_id}_for_{contact_id}.pdf"}
    )


@router.get("/recommend", tags=["PDF Generation"])
def get_personalized_recommendation(
    property_ids: str = Query(..., description="Comma-separated list of property IDs to compare (2-3 properties, e.g., '1,2,3')."),
    contact_id: int = Query(..., description="ID of the contact to generate recommendations for.")
):
    """
    Generates a personalized PDF recommendation comparing multiple properties against a contact's preferences.
    """
    # Parse property IDs
    try:
        property_id_list = [int(pid.strip()) for pid in property_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property IDs format. Use comma-separated integers (e.g., '1,2,3').")
    
    # Validate number of properties
    if len(property_id_list) < 2:
        raise HTTPException(status_code=400, detail="At least 2 properties are required for comparison.")
    if len(property_id_list) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 properties allowed for comparison.")
    
    # Fetch properties and contact
    properties = []
    missing_properties = []
    
    for prop_id in property_id_list:
        prop = PROPERTIES_DB.get(prop_id)
        if prop:
            properties.append(prop)
        else:
            missing_properties.append(prop_id)
    
    if missing_properties:
        raise HTTPException(status_code=404, detail=f"Properties not found: {missing_properties}")
    
    contact = CONTACTS_DB.get(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact ID not found.")

    # Generate personalized recommendation PDF
    pdf_bytes = generate_personalized_recommendation_pdf(properties, contact)
    
    property_ids_str = "_".join(str(p.id) for p in properties)
    filename = f"recommendation_{contact.name.replace(' ', '_')}_{property_ids_str}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/properties", tags=["Data Access"])
def list_properties(limit: int = Query(10, description="Maximum number of properties to return.")):
    """
    Returns a list of available properties.
    """
    properties_list = list(PROPERTIES_DB.values())[:limit]
    return {"properties": properties_list}


@router.get("/contacts", tags=["Data Access"])
def list_contacts(limit: int = Query(10, description="Maximum number of contacts to return.")):
    """
    Returns a list of available contacts.
    """
    contacts_list = list(CONTACTS_DB.values())[:limit]
    return {"contacts": contacts_list}


@router.get("/properties/{property_id}", tags=["Data Access"])
def get_property(property_id: int):
    """
    Returns details of a specific property.
    """
    property_obj = PROPERTIES_DB.get(property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found.")
    return property_obj


@router.get("/contacts/{contact_id}", tags=["Data Access"])
def get_contact(contact_id: int):
    """
    Returns details of a specific contact.
    """
    contact_obj = CONTACTS_DB.get(contact_id)
    if not contact_obj:
        raise HTTPException(status_code=404, detail="Contact not found.")
    return contact_obj 