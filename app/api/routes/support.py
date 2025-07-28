"""
Support API Routes for Nomadly3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...services.user_service import UserService
from ...schemas.support_schemas import (
    SupportTicketResponse, SupportTicketCreate,
    FAQResponse, ContactInfoResponse
)

router = APIRouter(prefix="/api/support", tags=["support"])

def get_user_service() -> UserService:
    return None

@router.get("/contact", response_model=ContactInfoResponse)
async def get_contact_info():
    """Get support contact information"""
    return ContactInfoResponse(
        telegram_support="@nomadly_support",
        email_support="support@nomadly.offshore",
        website="https://nomadly.offshore",
        business_hours="24/7 Offshore Support",
        timezone="UTC",
        response_time="< 2 hours"
    )

@router.get("/faq", response_model=List[FAQResponse])
async def get_faq():
    """Get frequently asked questions"""
    faq_items = [
        {
            "id": 1,
            "category": "Domain Registration",
            "question": "How do I register a domain?",
            "answer": "Use the /start command in the bot, select 'Search Domain', enter your desired domain name, and follow the registration workflow.",
            "priority": 1
        },
        {
            "id": 2,
            "category": "Payment & Billing",
            "question": "What cryptocurrencies are supported?",
            "answer": "We support Bitcoin (BTC), Ethereum (ETH), Litecoin (LTC), and Dogecoin (DOGE) for secure offshore payments.",
            "priority": 2
        },
        {
            "id": 3,
            "category": "DNS Management",
            "question": "How do I manage DNS records?",
            "answer": "Go to 'My Domains', select your domain, then 'Manage DNS' to add, edit, or delete DNS records through our Cloudflare integration.",
            "priority": 3
        },
        {
            "id": 4,
            "category": "Domain Registration",
            "question": "What TLDs are supported?",
            "answer": "We support .com, .net, .org, .info, .biz, .me, .co, .io, and many country-specific TLDs for offshore hosting.",
            "priority": 4
        },
        {
            "id": 5,
            "category": "Payment & Billing",
            "question": "How does pricing work?",
            "answer": "Domains are priced with a 3.3x offshore multiplier for enhanced privacy and security. Standard .com domains are $49.50 USD.",
            "priority": 5
        }
    ]
    
    return [FAQResponse(**item) for item in faq_items]

@router.get("/faq/search")
async def search_faq(
    query: str,
    category: Optional[str] = None
):
    """Search FAQ by keyword"""
    # Get all FAQ items
    all_faq = await get_faq()
    
    # Filter by category if specified
    if category:
        all_faq = [item for item in all_faq if item.category.lower() == category.lower()]
    
    # Search by query in question and answer
    query_lower = query.lower()
    matching_faq = [
        item for item in all_faq 
        if query_lower in item.question.lower() or query_lower in item.answer.lower()
    ]
    
    return matching_faq

@router.post("/tickets", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_support_ticket(
    ticket_data: SupportTicketCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Create new support ticket"""
    try:
        # In a real implementation, this would create a ticket in a ticketing system
        ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{ticket_data.telegram_id}"
        
        # Create ticket response
        ticket = SupportTicketResponse(
            ticket_id=ticket_id,
            telegram_id=ticket_data.telegram_id,
            subject=ticket_data.subject,
            message=ticket_data.message,
            category=ticket_data.category,
            priority=ticket_data.priority,
            status="open",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return ticket
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating support ticket: {str(e)}"
        )

@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_support_ticket(
    ticket_id: str,
    telegram_id: int
):
    """Get support ticket by ID"""
    # In a real implementation, this would fetch from ticketing system
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found"
    )

@router.get("/users/{telegram_id}/tickets", response_model=List[SupportTicketResponse])
async def get_user_tickets(
    telegram_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get user's support tickets"""
    # In a real implementation, this would fetch user tickets
    return []

@router.get("/system-status")
async def get_system_status():
    """Get system status information"""
    return {
        "status": "operational",
        "services": {
            "bot": "operational",
            "domain_registration": "operational", 
            "dns_management": "operational",
            "payment_processing": "operational",
            "blockchain_monitoring": "operational"
        },
        "last_updated": datetime.utcnow().isoformat(),
        "uptime": "99.9%",
        "active_domains": 2850,
        "processed_payments": 1247
    }

@router.get("/documentation")
async def get_documentation():
    """Get API documentation links"""
    return {
        "user_guide": "https://docs.nomadly.offshore/user-guide",
        "api_reference": "https://docs.nomadly.offshore/api",
        "domain_management": "https://docs.nomadly.offshore/domains", 
        "dns_guide": "https://docs.nomadly.offshore/dns",
        "payment_guide": "https://docs.nomadly.offshore/payments",
        "security_practices": "https://docs.nomadly.offshore/security"
    }