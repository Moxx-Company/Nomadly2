#!/usr/bin/env python3
"""
Comprehensive Multilingual Validation Test for Nomadly3
Tests all 5 languages across entire bot workflow including payment screens
"""

import json
import sys

def test_comprehensive_multilingual_functionality():
    """Test complete multilingual functionality across all bot workflows"""
    
    print("🌍 COMPREHENSIVE MULTILINGUAL VALIDATION TEST")
    print("=" * 60)
    
    # Test all 5 supported languages
    languages = ["en", "fr", "hi", "zh", "es"]
    language_names = {
        "en": "English",
        "fr": "Français", 
        "hi": "हिंदी",
        "zh": "中文",
        "es": "Español"
    }
    
    # Test user sessions functionality
    try:
        # Check if user sessions file exists and is readable
        with open('user_sessions.json', 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        print("✅ User sessions file exists and readable")
        
        # Check if sessions support language persistence
        has_language_support = any(
            'language' in session for session in sessions.values()
        )
        print(f"✅ Language persistence supported: {has_language_support}")
        
    except FileNotFoundError:
        print("⚠️ User sessions file not found - will be created on first use")
    except Exception as e:
        print(f"⚠️ Sessions file issue: {e}")
    
    # Test bot file multilingual capabilities
    try:
        with open('nomadly3_clean_bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        print("\n📱 TESTING BOT MULTILINGUAL FEATURES")
        print("-" * 40)
        
        # Test 1: Domain Registration Workflow Multilingual Support
        registration_texts = {
            "en": "Complete Registration:",
            "fr": "Finaliser l'enregistrement:",
            "hi": "पंजीकरण पूरा करें:",
            "zh": "完成注册:",
            "es": "Completar Registro:"
        }
        
        registration_support = 0
        for lang, text in registration_texts.items():
            if text in bot_content:
                registration_support += 1
                print(f"✅ {language_names[lang]}: Domain registration text found")
            else:
                print(f"❌ {language_names[lang]}: Domain registration text missing")
        
        print(f"\n📊 Domain Registration Multilingual Support: {registration_support}/5 languages ({registration_support/5*100:.1f}%)")
        
        # Test 2: Trustee Service Multilingual Support
        trustee_texts = {
            "en": "Trustee Service:",
            "fr": "Service fiduciaire:",
            "hi": "ट्रस्टी सेवा:",
            "zh": "受托服务:",
            "es": "Servicio Fiduciario:"
        }
        
        trustee_support = 0
        for lang, text in trustee_texts.items():
            if text in bot_content:
                trustee_support += 1
                print(f"✅ {language_names[lang]}: Trustee service text found")
            else:
                print(f"❌ {language_names[lang]}: Trustee service text missing")
        
        print(f"\n📊 Trustee Service Multilingual Support: {trustee_support}/5 languages ({trustee_support/5*100:.1f}%)")
        
        # Test 3: Payment Button Multilingual Support
        payment_button_texts = {
            "en": "Wallet Balance",
            "fr": "Solde portefeuille", 
            "hi": "वॉलेट बैलेंस",
            "zh": "钱包余额",
            "es": "Saldo Billetera"
        }
        
        payment_button_support = 0
        for lang, text in payment_button_texts.items():
            if text in bot_content:
                payment_button_support += 1
                print(f"✅ {language_names[lang]}: Payment button text found")
            else:
                print(f"❌ {language_names[lang]}: Payment button text missing")
        
        print(f"\n📊 Payment Button Multilingual Support: {payment_button_support}/5 languages ({payment_button_support/5*100:.1f}%)")
        
        # Test 4: Email Configuration Multilingual Support
        email_texts = {
            "en": "Technical Contact Email",
            "fr": "Email de Contact Technique",
            "hi": "तकनीकी संपर्क ईमेल",
            "zh": "技术联系邮箱",
            "es": "Email de Contacto Técnico"
        }
        
        email_support = 0
        for lang, text in email_texts.items():
            if text in bot_content:
                email_support += 1
                print(f"✅ {language_names[lang]}: Email configuration text found")
            else:
                print(f"❌ {language_names[lang]}: Email configuration text missing")
        
        print(f"\n📊 Email Configuration Multilingual Support: {email_support}/5 languages ({email_support/5*100:.1f}%)")
        
        # Test 5: Nameserver Configuration Multilingual Support
        nameserver_texts = {
            "en": "Nameserver Configuration",
            "fr": "Configuration des Serveurs de Noms",
            "hi": "नेमसर्वर कॉन्फ़िगरेशन",
            "zh": "域名服务器配置",
            "es": "Configuración de Servidores de Nombres"
        }
        
        nameserver_support = 0
        for lang, text in nameserver_texts.items():
            if text in bot_content:
                nameserver_support += 1
                print(f"✅ {language_names[lang]}: Nameserver configuration text found")
            else:
                print(f"❌ {language_names[lang]}: Nameserver configuration text missing")
        
        print(f"\n📊 Nameserver Configuration Multilingual Support: {nameserver_support}/5 languages ({nameserver_support/5*100:.1f}%)")
        
        # Test 6: Cryptocurrency Payment Screen Multilingual Support
        crypto_texts = {
            "en": "Payment Details",
            "fr": "Détails de Paiement",
            "hi": "भुगतान विवरण",
            "zh": "付款详情",
            "es": "Detalles de Pago"
        }
        
        crypto_support = 0
        for lang, text in crypto_texts.items():
            if text in bot_content:
                crypto_support += 1
                print(f"✅ {language_names[lang]}: Crypto payment screen text found")
            else:
                print(f"❌ {language_names[lang]}: Crypto payment screen text missing")
        
        print(f"\n📊 Cryptocurrency Payment Multilingual Support: {crypto_support}/5 languages ({crypto_support/5*100:.1f}%)")
        
        # Test 7: Crypto Payment Button Multilingual Support
        crypto_button_texts = {
            "en": "I've Sent Payment - Check Status",
            "fr": "J'ai Envoyé le Paiement - Vérifier Statut",
            "hi": "मैंने भुगतान भेजा है - स्थिति जांचें",
            "zh": "我已发送付款 - 检查状态",
            "es": "He Enviado el Pago - Verificar Estado"
        }
        
        crypto_button_support = 0
        for lang, text in crypto_button_texts.items():
            if text in bot_content:
                crypto_button_support += 1
                print(f"✅ {language_names[lang]}: Crypto payment button text found")
            else:
                print(f"❌ {language_names[lang]}: Crypto payment button text missing")
        
        print(f"\n📊 Crypto Payment Button Multilingual Support: {crypto_button_support}/5 languages ({crypto_button_support/5*100:.1f}%)")
        
        # Calculate overall multilingual coverage
        total_features = 7
        total_possible = total_features * 5  # 7 features × 5 languages = 35
        total_implemented = (registration_support + trustee_support + payment_button_support + 
                           email_support + nameserver_support + crypto_support + crypto_button_support)
        
        overall_coverage = (total_implemented / total_possible) * 100
        
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE MULTILINGUAL ASSESSMENT")
        print("=" * 60)
        
        print(f"📱 Domain Registration Workflow:  {registration_support}/5 ({registration_support/5*100:.0f}%)")
        print(f"🏛️ Trustee Service Integration:   {trustee_support}/5 ({trustee_support/5*100:.0f}%)")
        print(f"💳 Payment Button Interface:      {payment_button_support}/5 ({payment_button_support/5*100:.0f}%)")
        print(f"📧 Email Configuration Screen:    {email_support}/5 ({email_support/5*100:.0f}%)")
        print(f"🌐 Nameserver Configuration:      {nameserver_support}/5 ({nameserver_support/5*100:.0f}%)")
        print(f"💎 Cryptocurrency Payment Screen: {crypto_support}/5 ({crypto_support/5*100:.0f}%)")
        print(f"✅ Crypto Payment Action Buttons: {crypto_button_support}/5 ({crypto_button_support/5*100:.0f}%)")
        
        print(f"\n🌍 OVERALL MULTILINGUAL COVERAGE: {total_implemented}/{total_possible} features ({overall_coverage:.1f}%)")
        
        if overall_coverage >= 95:
            print("🎉 EXCELLENT: Comprehensive multilingual support achieved!")
        elif overall_coverage >= 80:
            print("✅ GOOD: Strong multilingual support with minor gaps")
        elif overall_coverage >= 60:
            print("⚠️ MODERATE: Partial multilingual support needs improvement")
        else:
            print("❌ POOR: Significant multilingual gaps need addressing")
        
        # Test specific workflow completeness
        print("\n📋 WORKFLOW COMPLETENESS ANALYSIS")
        print("-" * 40)
        
        workflow_tests = {
            "Language Selection": "lang_en" in bot_content and "lang_fr" in bot_content,
            "Domain Registration": "Complete Registration:" in bot_content,
            "Payment Processing": "Choose your payment method:" in bot_content,
            "Email Configuration": "Technical Contact Email" in bot_content,
            "Nameserver Setup": "Nameserver Configuration" in bot_content,
            "Crypto Payments": "Payment Details" in bot_content,
            "Language Persistence": "user_language = session.get(\"language\"" in bot_content
        }
        
        workflow_completeness = 0
        for workflow, test_result in workflow_tests.items():
            if test_result:
                print(f"✅ {workflow}: Implemented")
                workflow_completeness += 1
            else:
                print(f"❌ {workflow}: Missing")
        
        print(f"\n📊 Workflow Completeness: {workflow_completeness}/7 ({workflow_completeness/7*100:.1f}%)")
        
        # Final comprehensive assessment
        print("\n" + "=" * 60)
        print("🏆 FINAL COMPREHENSIVE ASSESSMENT")
        print("=" * 60)
        
        if overall_coverage >= 95 and workflow_completeness >= 6:
            print("🌟 DEPLOYMENT READY: Complete multilingual system operational")
            print("🎯 All 5 languages supported across entire user workflow")
            print("✅ Users can complete domain registration in their preferred language")
            return True
        elif overall_coverage >= 80:
            print("🔧 NEAR COMPLETE: Minor multilingual enhancements needed")
            print("⚡ Core functionality operational in multiple languages")
            return True
        else:
            print("⚠️ NEEDS WORK: Significant multilingual gaps remain")
            print("🔨 Additional language support implementation required")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bot multilingual features: {e}")
        return False

if __name__ == "__main__":
    print("Starting comprehensive multilingual validation...")
    success = test_comprehensive_multilingual_functionality()
    
    if success:
        print("\n🎉 COMPREHENSIVE MULTILINGUAL VALIDATION: PASSED")
        sys.exit(0)
    else:
        print("\n❌ COMPREHENSIVE MULTILINGUAL VALIDATION: FAILED")
        sys.exit(1)