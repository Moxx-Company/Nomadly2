"""
NEW CLEAN DNS UI SYSTEM - SIMPLE & RESPONSIVE
Replaces the old complex DNS system with clean, simple interface
"""

class NewDNSUI:
    """Clean DNS management interface with simple callbacks"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
    async def show_dns_main_menu(self, query, domain):
        """Simple DNS main menu for a domain"""
        try:
            user_id = query.from_user.id
            user_lang = self.bot.user_sessions.get(user_id, {}).get("language", "en")
            clean_domain = domain.replace('_', '.')
            
            titles = {
                "en": f"🌐 DNS Manager - {clean_domain}",
                "fr": f"🌐 Gestionnaire DNS - {clean_domain}",
                "hi": f"🌐 DNS प्रबंधक - {clean_domain}",
                "zh": f"🌐 DNS 管理器 - {clean_domain}",
                "es": f"🌐 Gestor DNS - {clean_domain}"
            }
            
            # Simple menu options
            buttons = {
                "en": {"view": "📋 View Records", "add": "➕ Add Record", "edit": "✏️ Edit Records", "delete": "🗑️ Delete Records", "back": "← Back"},
                "fr": {"view": "📋 Voir Enregistrements", "add": "➕ Ajouter", "edit": "✏️ Modifier", "delete": "🗑️ Supprimer", "back": "← Retour"},
                "hi": {"view": "📋 रिकॉर्ड देखें", "add": "➕ जोड़ें", "edit": "✏️ संपादित करें", "delete": "🗑️ हटाएं", "back": "← वापस"},
                "zh": {"view": "📋 查看记录", "add": "➕ 添加记录", "edit": "✏️ 编辑记录", "delete": "🗑️ 删除记录", "back": "← 返回"},
                "es": {"view": "📋 Ver Registros", "add": "➕ Agregar", "edit": "✏️ Editar", "delete": "🗑️ Eliminar", "back": "← Volver"}
            }
            
            lang_buttons = buttons.get(user_lang, buttons["en"])
            text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\nChoose an action:"
            
            # Simple callback format: action_domain (no accumulation)
            keyboard = [
                [
                    {"text": lang_buttons["view"], "callback_data": f"dns_view_{domain}"},
                    {"text": lang_buttons["add"], "callback_data": f"dns_add_{domain}"}
                ],
                [
                    #{"text": lang_buttons["edit"], "callback_data": f"dns_edit_{domain}"},
                    {"text": lang_buttons["delete"], "callback_data": f"dns_delete_{domain}"}
                ],
                [{"text": lang_buttons["back"], "callback_data": f"my_domains"}]
            ]
            
            return text, keyboard
            
        except Exception as e:
            return f"❌ Error: {str(e)}", []
    
    async def show_dns_records(self, query, domain):
        """Show DNS records in clean format"""
        try:
            user_id = query.from_user.id
            user_lang = self.bot.user_sessions.get(user_id, {}).get("language", "en")
            clean_domain = domain.replace('_', '.')
            
            titles = {
                "en": f"📋 DNS Records - {clean_domain}",
                "fr": f"📋 Enregistrements DNS - {clean_domain}",
                "hi": f"📋 DNS रिकॉर्ड - {clean_domain}",
                "zh": f"📋 DNS 记录 - {clean_domain}",
                "es": f"📋 Registros DNS - {clean_domain}"
            }
            
            # Get records from unified DNS manager
            try:
                from unified_dns_manager import unified_dns_manager
                records = await unified_dns_manager.get_dns_records(clean_domain)
            except Exception:
                records = []  # Fallback if DNS manager unavailable
            
            if records:
                records_text = "\n".join([
                    f"• {r.get('type', 'A')} {r.get('name', '@')} → {r.get('content', 'N/A')}"
                    for r in records[:8]  # Show max 8 records
                ])
                text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{records_text}"
            else:
                no_records = {
                    "en": "No DNS records found.",
                    "fr": "Aucun enregistrement DNS trouvé.",
                    "hi": "कोई DNS रिकॉर्ड नहीं मिला।",
                    "zh": "未找到 DNS 记录。",
                    "es": "No se encontraron registros DNS."
                }
                text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{no_records.get(user_lang, no_records['en'])}"
            
            back_texts = {
                "en": "← Back to DNS Menu",
                "fr": "← Retour au menu DNS",
                "hi": "← DNS मेनू पर वापस",
                "zh": "← 返回 DNS 菜单",
                "es": "← Volver al menú DNS"
            }
            
            keyboard = [
                [{"text": back_texts.get(user_lang, back_texts["en"]), "callback_data": f"dns_main_{domain}"}]
            ]
            
            return text, keyboard
            
        except Exception as e:
            return f"❌ Error: {str(e)}", []
    
    async def show_add_record_types(self, query, domain):
        """Show record types for adding"""
        try:
            user_id = query.from_user.id
            user_lang = self.bot.user_sessions.get(user_id, {}).get("language", "en")
            clean_domain = domain.replace('_', '.')
            
            titles = {
                "en": f"➕ Add DNS Record - {clean_domain}",
                "fr": f"➕ Ajouter Enregistrement DNS - {clean_domain}",
                "hi": f"➕ DNS रिकॉर्ड जोड़ें - {clean_domain}",
                "zh": f"➕ 添加 DNS 记录 - {clean_domain}",
                "es": f"➕ Agregar Registro DNS - {clean_domain}"
            }
            
            choose_texts = {
                "en": "Choose record type:",
                "fr": "Choisissez le type d'enregistrement :",
                "hi": "रिकॉर्ड प्रकार चुनें:",
                "zh": "选择记录类型：",
                "es": "Elija el tipo de registro:"
            }
            
            text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{choose_texts.get(user_lang, choose_texts['en'])}"
            
            # Simple record type selection
            keyboard = [
                [
                    {"text": "A Record", "callback_data": f"dns_add_a_{domain}"},
                    {"text": "AAAA Record", "callback_data": f"dns_add_aaaa_{domain}"}
                ],
                [
                    {"text": "CNAME", "callback_data": f"dns_add_cname_{domain}"},
                    {"text": "MX Record", "callback_data": f"dns_add_mx_{domain}"}
                ],
                [
                    {"text": "TXT Record", "callback_data": f"dns_add_txt_{domain}"},
                    {"text": "SRV Record", "callback_data": f"dns_add_srv_{domain}"}
                ],
                [{"text": "← Back", "callback_data": f"dns_main_{domain}"}]
            ]
            
            return text, keyboard
            
        except Exception as e:
            return f"❌ Error: {str(e)}", []    
    async def show_edit_records(self, query, domain):
        """Show edit records interface with real DNS records"""
        try:
            user_id = query.from_user.id
            user_lang = self.bot.user_sessions.get(user_id, {}).get("language", "en")
            clean_domain = domain.replace('_', '.')
            
            titles = {
                "en": f"✏️ Edit DNS Records - {clean_domain}",
                "fr": f"✏️ Modifier Enregistrements DNS - {clean_domain}",
                "hi": f"✏️ DNS रिकॉर्ड संपादित करें - {clean_domain}",
                "zh": f"✏️ 编辑 DNS 记录 - {clean_domain}",
                "es": f"✏️ Editar Registros DNS - {clean_domain}"
            }
            
            # Get DNS records from unified DNS manager
            try:
                from unified_dns_manager import unified_dns_manager
                records = await unified_dns_manager.get_dns_records(clean_domain)
            except Exception:
                records = []  # Fallback if DNS manager unavailable
            
            if records:
                instructions = {
                    "en": "Select a record to edit:",
                    "fr": "Sélectionnez un enregistrement à modifier :",
                    "hi": "संपादित करने के लिए एक रिकॉर्ड चुनें:",
                    "zh": "选择要编辑的记录：",
                    "es": "Seleccione un registro para editar:"
                }
                
                text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{instructions.get(user_lang, instructions['en'])}\n\n"
                
                keyboard = []
                for i, record in enumerate(records[:10]):  # Show max 10 records
                    record_display = f"{record.get('type', 'A')} {record.get('name', '@')} → {record.get('content', 'N/A')[:30]}"
                    keyboard.append([{"text": f"✏️ {record_display}", "callback_data": f"edit_dns_record_{domain}_{i}"}])
                
                keyboard.append([{"text": "← Back", "callback_data": f"dns_main_{domain}"}])
                
            else:
                no_records = {
                    "en": "No DNS records found to edit.",
                    "fr": "Aucun enregistrement DNS trouvé à modifier.",
                    "hi": "संपादित करने के लिए कोई DNS रिकॉर्ड नहीं मिला।",
                    "zh": "未找到要编辑的 DNS 记录。",
                    "es": "No se encontraron registros DNS para editar."
                }
                text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{no_records.get(user_lang, no_records['en'])}"
                keyboard = [[{"text": "← Back", "callback_data": f"dns_main_{domain}"}]]
            
            return text, keyboard
            
        except Exception as e:
            return f"❌ Error: {str(e)}", []
    
    async def show_delete_records(self, query, domain):
        """Show delete records interface with real DNS records"""
        try:
            user_id = query.from_user.id
            user_lang = self.bot.user_sessions.get(user_id, {}).get("language", "en")
            clean_domain = domain.replace('_', '.')
            
            titles = {
                "en": f"🗑️ Delete DNS Records - {clean_domain}",
                "fr": f"🗑️ Supprimer Enregistrements DNS - {clean_domain}",
                "hi": f"🗑️ DNS रिकॉर्ड हटाएं - {clean_domain}",
                "zh": f"🗑️ 删除 DNS 记录 - {clean_domain}",
                "es": f"🗑️ Eliminar Registros DNS - {clean_domain}"
            }
            
            # Get DNS records from unified DNS manager
            try:
                from unified_dns_manager import unified_dns_manager
                records = await unified_dns_manager.get_dns_records(clean_domain)
            except Exception:
                records = []  # Fallback if DNS manager unavailable
            
            if records:
                warnings = {
                    "en": "⚠️ Warning: Deleting DNS records can make your domain inaccessible!\n\nSelect a record to delete:",
                    "fr": "⚠️ Attention : Supprimer des enregistrements DNS peut rendre votre domaine inaccessible !\n\nSélectionnez un enregistrement à supprimer :",
                    "hi": "⚠️ चेतावनी: DNS रिकॉर्ड हटाने से आपका डोमेन दुर्गम हो सकता है!\n\nहटाने के लिए एक रिकॉर्ड चुनें:",
                    "zh": "⚠️ 警告：删除 DNS 记录可能使您的域名无法访问！\n\n选择要删除的记录：",
                    "es": "⚠️ Advertencia: ¡Eliminar registros DNS puede hacer que su dominio sea inaccesible!\n\nSeleccione un registro para eliminar:"
                }
                
                text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{warnings.get(user_lang, warnings['en'])}\n\n"
                
                keyboard = []
                for i, record in enumerate(records[:10]):  # Show max 10 records
                    record_display = f"{record.get('type', 'A')} {record.get('name', '@')} → {record.get('content', 'N/A')[:30]}"
                    keyboard.append([{"text": f"🗑️ {record_display}", "callback_data": f"delete_dns_record_{domain}_{i}"}])
                
                keyboard.append([{"text": "← Back", "callback_data": f"dns_main_{domain}"}])
                
            else:
                no_records = {
                    "en": "No DNS records found to delete.",
                    "fr": "Aucun enregistrement DNS trouvé à supprimer.",
                    "hi": "हटाने के लिए कोई DNS रिकॉर्ड नहीं मिला।",
                    "zh": "未找到要删除的 DNS 记录。",
                    "es": "No se encontraron registros DNS para eliminar."
                }
                text = f"<b>{titles.get(user_lang, titles['en'])}</b>\n\n{no_records.get(user_lang, no_records['en'])}"
                keyboard = [[{"text": "← Back", "callback_data": f"dns_main_{domain}"}]]
            
            return text, keyboard
            
        except Exception as e:
            return f"❌ Error: {str(e)}", []
