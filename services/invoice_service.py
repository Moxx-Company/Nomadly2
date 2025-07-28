"""
Invoice Service for Phase 6
PDF invoice generation system for professional service billing
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class InvoiceService:
    """Professional PDF invoice generation service for Nomadly platform"""

    def __init__(self):
        self.invoice_dir = "invoices"
        self.company_info = {
            "name": "Nomadly",
            "address": "Offshore Digital Services",
            "email": "support@nomadly.com",
            "website": "https://t.me/NomadlyHQ",
        }

        # Create invoice directory if it doesn't exist
        os.makedirs(self.invoice_dir, exist_ok=True)

        # Check if ReportLab is available
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors

            self.reportlab_available = True
            logger.info("Invoice service initialized with ReportLab support")
        except ImportError:
            self.reportlab_available = False
            logger.warning("ReportLab not available - using HTML invoice generation")

    def generate_invoice_number(self, invoice_id: int) -> str:
        """Generate unique invoice number in format NOM-2025-001234"""
        year = datetime.now().year
        sequence = f"{invoice_id:06d}"
        return f"NOM-{year}-{sequence}"

    def create_invoice(
        self, invoice_data: Dict[str, Any], output_path: str = None
    ) -> Optional[str]:
        """Create PDF invoice and return file path"""

        if self.reportlab_available:
            return self._create_pdf_invoice(invoice_data, output_path)
        else:
            return self._create_html_invoice(invoice_data, output_path)

    def _create_pdf_invoice(
        self, invoice_data: Dict[str, Any], output_path: str = None
    ) -> Optional[str]:
        """Create PDF invoice using ReportLab"""

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import (
                SimpleDocTemplate,
                Table,
                TableStyle,
                Paragraph,
                Spacer,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors

            # Generate file path
            if not output_path:
                invoice_number = invoice_data.get("invoice_number", "INVOICE")
                output_path = os.path.join(self.invoice_dir, f"{invoice_number}.pdf")

            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Center alignment
            )

            story.append(Paragraph("INVOICE", title_style))
            story.append(Spacer(1, 20))

            # Company header
            company_info = [
                ["", "Invoice #:", invoice_data.get("invoice_number", "N/A")],
                [
                    self.company_info["name"],
                    "Date:",
                    invoice_data.get("created_at", datetime.now().strftime("%Y-%m-%d")),
                ],
                [
                    self.company_info["address"],
                    "Due Date:",
                    invoice_data.get("due_date", "Immediate"),
                ],
                [self.company_info["email"], "", ""],
                [self.company_info["website"], "", ""],
            ]

            header_table = Table(company_info, colWidths=[3 * inch, 1 * inch, 2 * inch])
            header_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 12),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )

            story.append(header_table)
            story.append(Spacer(1, 30))

            # Customer information
            customer_info = [
                ["Bill To:", ""],
                [invoice_data.get("customer_email", "N/A"), ""],
                [f"Order ID: {invoice_data.get('order_id', 'N/A')}", ""],
            ]

            customer_table = Table(customer_info, colWidths=[3 * inch, 3 * inch])
            customer_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 12),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )

            story.append(customer_table)
            story.append(Spacer(1, 30))

            # Service details
            service_data = [["Description", "Amount"]]

            service_description = self._format_service_description(invoice_data)
            amount = f"${invoice_data.get('amount', 0.00):.2f}"

            service_data.append([service_description, amount])

            # Add payment method
            payment_method = invoice_data.get("payment_method", "N/A").upper()
            if payment_method != "BALANCE":
                service_data.append([f"Payment Method: {payment_method}", ""])

            service_table = Table(service_data, colWidths=[4 * inch, 2 * inch])
            service_table.setStyle(
                TableStyle(
                    [
                        # Header
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        # Body
                        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(service_table)
            story.append(Spacer(1, 30))

            # Total
            total_data = [
                ["", "Total:", f"${invoice_data.get('amount', 0.00):.2f}"],
                ["", "Status:", invoice_data.get("status", "Paid").title()],
            ]

            total_table = Table(
                total_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch]
            )
            total_table.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                        ("FONTNAME", (1, 0), (-1, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (1, 0), (-1, -1), 14),
                        ("TOPPADDING", (1, 0), (-1, -1), 6),
                    ]
                )
            )

            story.append(total_table)
            story.append(Spacer(1, 40))

            # Footer
            footer_text = (
                "Thank you for choosing Nomadly! For support, contact @nomadlysupport"
            )
            footer_style = ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=10,
                alignment=1,
                textColor=colors.grey,
            )

            story.append(Paragraph(footer_text, footer_style))

            # Build PDF
            doc.build(story)

            logger.info(f"PDF invoice created: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"PDF invoice creation failed: {e}")
            return None

    def _create_html_invoice(
        self, invoice_data: Dict[str, Any], output_path: str = None
    ) -> Optional[str]:
        """Create HTML invoice as fallback when ReportLab is not available"""

        try:
            # Generate file path
            if not output_path:
                invoice_number = invoice_data.get("invoice_number", "INVOICE")
                output_path = os.path.join(self.invoice_dir, f"{invoice_number}.html")

            service_description = self._format_service_description(invoice_data)
            amount = f"${invoice_data.get('amount', 0.00):.2f}"
            payment_method = invoice_data.get("payment_method", "N/A").upper()

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Invoice {invoice_data.get('invoice_number', 'N/A')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    .invoice-header {{ text-align: center; margin-bottom: 30px; }}
                    .invoice-title {{ font-size: 28px; font-weight: bold; color: #2c5aa0; }}
                    .company-info {{ float: left; width: 50%; }}
                    .invoice-info {{ float: right; width: 50%; text-align: right; }}
                    .clear {{ clear: both; }}
                    .customer-info {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }}
                    .service-table {{ width: 100%; border-collapse: collapse; margin: 30px 0; }}
                    .service-table th, .service-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    .service-table th {{ background: #f8f9fa; font-weight: bold; }}
                    .total-section {{ text-align: right; margin: 30px 0; font-size: 18px; }}
                    .footer {{ text-align: center; margin-top: 50px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="invoice-header">
                    <div class="invoice-title">INVOICE</div>
                </div>
                
                <div class="company-info">
                    <strong>{self.company_info['name']}</strong><br>
                    {self.company_info['address']}<br>
                    {self.company_info['email']}<br>
                    {self.company_info['website']}
                </div>
                
                <div class="invoice-info">
                    <strong>Invoice #:</strong> {invoice_data.get('invoice_number', 'N/A')}<br>
                    <strong>Date:</strong> {invoice_data.get('created_at', datetime.now().strftime('%Y-%m-%d'))}<br>
                    <strong>Due Date:</strong> {invoice_data.get('due_date', 'Immediate')}
                </div>
                
                <div class="clear"></div>
                
                <div class="customer-info">
                    <strong>Bill To:</strong><br>
                    {invoice_data.get('customer_email', 'N/A')}<br>
                    Order ID: {invoice_data.get('order_id', 'N/A')}
                </div>
                
                <table class="service-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{service_description}</td>
                            <td>{amount}</td>
                        </tr>
                        {"<tr><td>Payment Method: " + payment_method + "</td><td></td></tr>" if payment_method != 'BALANCE' else ''}
                    </tbody>
                </table>
                
                <div class="total-section">
                    <strong>Total: {amount}</strong><br>
                    <strong>Status: {invoice_data.get('status', 'Paid').title()}</strong>
                </div>
                
                <div class="footer">
                    Thank you for choosing Nomadly! For support, contact @nomadlysupport
                </div>
            </body>
            </html>
            """

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTML invoice created: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"HTML invoice creation failed: {e}")
            return None

    def _format_service_description(self, invoice_data: Dict[str, Any]) -> str:
        """Format service description for invoice"""

        service_type = invoice_data.get("service_type", "Service")
        service_description = invoice_data.get("service_description", "")

        descriptions = {
            "hosting": f"cPanel Hosting Service - {service_description}",
            "domain": f"Domain Registration - {service_description}",
            "url_shortener": f"URL Shortener Service - {service_description}",
            "balance_deposit": "Account Balance Deposit",
        }

        return descriptions.get(
            service_type, service_description or "Professional Service"
        )

    def get_invoice_path(self, invoice_number: str, format_type: str = "pdf") -> str:
        """Get full path for invoice file"""
        filename = f"{invoice_number}.{format_type}"
        return os.path.join(self.invoice_dir, filename)

    def invoice_exists(self, invoice_number: str) -> bool:
        """Check if invoice file exists"""
        pdf_path = self.get_invoice_path(invoice_number, "pdf")
        html_path = self.get_invoice_path(invoice_number, "html")
        return os.path.exists(pdf_path) or os.path.exists(html_path)

    def get_service_status(self) -> Dict[str, Any]:
        """Get invoice service status and configuration"""
        return {
            "reportlab_available": self.reportlab_available,
            "invoice_dir": self.invoice_dir,
            "invoice_dir_exists": os.path.exists(self.invoice_dir),
            "company_info": self.company_info,
        }
