#!/usr/bin/env python3
"""
Usability Testing System (Test 11)
Comprehensive usability analysis and user experience testing
"""

import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os

@dataclass
class UsabilityIssue:
    """Usability issue found during testing"""
    severity: str  # 'critical', 'major', 'minor'
    category: str  # 'navigation', 'messaging', 'flow', 'feedback', 'errors'
    description: str
    location: str
    recommendation: str
    impact: str

@dataclass
class UserFlowAnalysis:
    """Analysis of user flow complexity"""
    flow_name: str
    steps_count: int
    decision_points: int
    callback_handlers: int
    complexity_score: float
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class UsabilityAnalyzer:
    """Comprehensive usability testing and analysis"""
    
    def __init__(self):
        self.issues = []
        self.flow_analyses = []
        self.complexity_thresholds = {
            'low': 0.3,
            'moderate': 0.6, 
            'high': 0.8
        }
    
    def analyze_bot_code_structure(self, file_path: str = "nomadly2_bot.py") -> Dict[str, Any]:
        """Analyze bot code structure for usability issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_size': len(content),
                'line_count': len(content.splitlines()),
                'callback_handlers': content.count('callback_data='),
                'menu_options': content.count('InlineKeyboardButton'),
                'user_messages': content.count('sendMessage') + content.count('editMessageText'),
                'error_handling': content.count('try:') + content.count('except'),
                'loading_indicators': len(re.findall(r'Loading\.\.\.|⚡|🔄|⏳', content)),
                'user_friendly_terms': len(re.findall(r'please|welcome|thank you|help|support', content, re.IGNORECASE)),
                'confirmation_dialogs': len(re.findall(r'confirm|are you sure|proceed', content, re.IGNORECASE)),
                'navigation_elements': content.count('main_menu') + content.count('back') + content.count('home')
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate_ui_complexity(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate UI complexity based on code analysis"""
        callback_count = analysis.get('callback_handlers', 0)
        menu_options = analysis.get('menu_options', 0)
        line_count = analysis.get('line_count', 0)
        
        # Calculate complexity score (0-1 scale)
        complexity_factors = {
            'callback_density': min(callback_count / 100, 1.0),  # Normalize to 100 callbacks
            'menu_density': min(menu_options / 200, 1.0),       # Normalize to 200 buttons
            'code_complexity': min(line_count / 5000, 1.0)      # Normalize to 5000 lines
        }
        
        overall_complexity = sum(complexity_factors.values()) / len(complexity_factors)
        
        # Determine complexity level
        if overall_complexity <= self.complexity_thresholds['low']:
            complexity_level = 'Low'
            complexity_status = '✅'
        elif overall_complexity <= self.complexity_thresholds['moderate']:
            complexity_level = 'Moderate'
            complexity_status = '⚠️'
        elif overall_complexity <= self.complexity_thresholds['high']:
            complexity_level = 'High'
            complexity_status = '🔶'
        else:
            complexity_level = 'Very High'
            complexity_status = '❌'
        
        return {
            'complexity_score': overall_complexity,
            'complexity_level': complexity_level,
            'complexity_status': complexity_status,
            'factors': complexity_factors,
            'callback_count': callback_count,
            'recommendations': self._get_complexity_recommendations(complexity_level, callback_count)
        }
    
    def _get_complexity_recommendations(self, level: str, callback_count: int) -> List[str]:
        """Get recommendations based on complexity level"""
        recommendations = []
        
        if level in ['High', 'Very High']:
            recommendations.append("Urgently simplify user interface by consolidating similar functions")
            recommendations.append("Implement menu categories to reduce cognitive load")
            recommendations.append("Consider wizard-style flows for complex operations")
        
        if callback_count > 500:
            recommendations.append("Break down large callback handlers into focused modules")
            recommendations.append("Implement callback routing system to reduce complexity")
        
        if level == 'Very High':
            recommendations.append("Conduct user journey mapping to identify unnecessary steps")
            recommendations.append("Consider complete UI redesign with user-centered approach")
        
        return recommendations
    
    def analyze_user_messaging(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user-facing messaging quality"""
        user_friendly_count = analysis.get('user_friendly_terms', 0)
        total_messages = analysis.get('user_messages', 1)  # Avoid division by zero
        
        # Calculate messaging quality score (avoid division by zero)
        if total_messages > 0:
            messaging_quality = min(user_friendly_count / (total_messages * 0.1), 1.0)
        else:
            messaging_quality = 0.0
        
        if messaging_quality >= 0.8:
            messaging_status = '✅ Excellent'
        elif messaging_quality >= 0.6:
            messaging_status = '✅ Good'
        elif messaging_quality >= 0.4:
            messaging_status = '⚠️ Needs Improvement'
        else:
            messaging_status = '❌ Poor'
        
        recommendations = []
        if messaging_quality < 0.6:
            recommendations.extend([
                "Add more welcoming and helpful language",
                "Include 'please' and 'thank you' in user interactions",
                "Provide clear guidance and support options"
            ])
        
        return {
            'messaging_quality': messaging_quality,
            'messaging_status': messaging_status,
            'friendly_terms_count': user_friendly_count,
            'total_messages': total_messages,
            'recommendations': recommendations
        }
    
    def analyze_error_handling(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze error handling and user feedback quality"""
        error_handling_count = analysis.get('error_handling', 0)
        line_count = analysis.get('line_count', 1)
        
        # Calculate error handling coverage
        error_coverage = min(error_handling_count / (line_count * 0.05), 1.0)
        
        if error_coverage >= 0.8:
            error_status = '✅ Comprehensive'
        elif error_coverage >= 0.6:
            error_status = '✅ Good'
        elif error_coverage >= 0.4:
            error_status = '⚠️ Adequate'
        else:
            error_status = '❌ Insufficient'
        
        recommendations = []
        if error_coverage < 0.6:
            recommendations.extend([
                "Add more try-catch blocks for API operations",
                "Implement user-friendly error messages",
                "Provide recovery options for common errors"
            ])
        
        return {
            'error_coverage': error_coverage,
            'error_status': error_status,
            'error_blocks_count': error_handling_count,
            'recommendations': recommendations
        }
    
    def analyze_navigation_design(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze navigation structure and flow"""
        nav_elements = analysis.get('navigation_elements', 0)
        callback_handlers = analysis.get('callback_handlers', 1)
        
        # Calculate navigation density
        nav_density = nav_elements / callback_handlers if callback_handlers > 0 else 0
        
        if nav_density >= 0.1:
            nav_status = '✅ Good Navigation'
        elif nav_density >= 0.05:
            nav_status = '⚠️ Limited Navigation'  
        else:
            nav_status = '❌ Poor Navigation'
        
        recommendations = []
        if nav_density < 0.1:
            recommendations.extend([
                "Add more back buttons and menu options",
                "Implement breadcrumb navigation for complex flows",
                "Provide clear paths to main menu from any screen"
            ])
        
        return {
            'navigation_density': nav_density,
            'navigation_status': nav_status,
            'navigation_elements': nav_elements,
            'recommendations': recommendations
        }
    
    def analyze_confirmation_dialogs(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confirmation dialog usage"""
        confirmation_count = analysis.get('confirmation_dialogs', 0)
        callback_handlers = analysis.get('callback_handlers', 1)
        
        # Calculate confirmation coverage for critical actions
        confirmation_coverage = min(confirmation_count / (callback_handlers * 0.1), 1.0)
        
        if confirmation_coverage >= 0.8:
            confirmation_status = '✅ Well Protected'
        elif confirmation_coverage >= 0.5:
            confirmation_status = '✅ Adequate'
        elif confirmation_coverage >= 0.3:
            confirmation_status = '⚠️ Limited'
        else:
            confirmation_status = '❌ Insufficient'
        
        recommendations = []
        if confirmation_coverage < 0.5:
            recommendations.extend([
                "Add confirmation dialogs for critical actions",
                "Implement double-confirmation for destructive operations",
                "Provide clear action descriptions in confirmations"
            ])
        
        return {
            'confirmation_coverage': confirmation_coverage,
            'confirmation_status': confirmation_status,
            'confirmation_count': confirmation_count,
            'recommendations': recommendations
        }
    
    def check_documentation_completeness(self) -> Dict[str, Any]:
        """Check documentation and help resources"""
        docs_to_check = [
            'README.md',
            'ADMIN_GUIDE.md', 
            'USER_GUIDE.md',
            'COMPLETE_FEATURE_SPECIFICATION.md',
            'NOMADLY_USER_JOURNEY_MAP.md'
        ]
        
        found_docs = []
        missing_docs = []
        
        for doc in docs_to_check:
            try:
                with open(doc, 'r') as f:
                    content = f.read()
                    if len(content) > 100:  # Meaningful content
                        found_docs.append(doc)
                    else:
                        missing_docs.append(f"{doc} (too short)")
            except FileNotFoundError:
                missing_docs.append(doc)
        
        documentation_score = len(found_docs) / len(docs_to_check)
        
        if documentation_score >= 0.8:
            doc_status = '✅ Comprehensive'
        elif documentation_score >= 0.6:
            doc_status = '✅ Good'
        elif documentation_score >= 0.4:
            doc_status = '⚠️ Basic'
        else:
            doc_status = '❌ Insufficient'
        
        return {
            'documentation_score': documentation_score,
            'documentation_status': doc_status,
            'found_documents': found_docs,
            'missing_documents': missing_docs,
            'recommendations': [
                "Create missing user documentation",
                "Add troubleshooting guides",
                "Include feature usage examples"
            ] if documentation_score < 0.8 else []
        }
    
    def identify_usability_issues(self, all_analyses: Dict[str, Any]) -> List[UsabilityIssue]:
        """Identify specific usability issues"""
        issues = []
        
        # UI Complexity Issues
        complexity_analysis = all_analyses.get('complexity', {})
        if complexity_analysis.get('complexity_level') == 'Very High':
            issues.append(UsabilityIssue(
                severity='critical',
                category='navigation',
                description=f"Extremely high UI complexity ({complexity_analysis.get('callback_count')} callbacks)",
                location='nomadly2_bot.py',
                recommendation='Implement menu categorization and workflow simplification',
                impact='Users will be overwhelmed and confused by too many options'
            ))
        
        # Messaging Issues
        messaging_analysis = all_analyses.get('messaging', {})
        if messaging_analysis.get('messaging_quality', 0) < 0.4:
            issues.append(UsabilityIssue(
                severity='major',
                category='messaging',
                description='Insufficient user-friendly language in bot interactions',
                location='nomadly2_bot.py',
                recommendation='Add welcoming language, clear instructions, and helpful guidance',
                impact='Users may feel the bot is unfriendly or difficult to understand'
            ))
        
        # Error Handling Issues
        error_analysis = all_analyses.get('error_handling', {})
        if error_analysis.get('error_coverage', 0) < 0.4:
            issues.append(UsabilityIssue(
                severity='major',
                category='errors',
                description='Insufficient error handling and user feedback',
                location='nomadly2_bot.py',
                recommendation='Implement comprehensive error handling with recovery options',
                impact='Users may encounter crashes or confusing error states'
            ))
        
        # Navigation Issues
        nav_analysis = all_analyses.get('navigation', {})
        if nav_analysis.get('navigation_density', 0) < 0.05:
            issues.append(UsabilityIssue(
                severity='major',
                category='navigation',
                description='Poor navigation structure with limited back/menu options',
                location='nomadly2_bot.py',
                recommendation='Add consistent navigation elements throughout the interface',
                impact='Users may get lost in deep menu structures without escape routes'
            ))
        
        # Confirmation Issues
        confirmation_analysis = all_analyses.get('confirmation', {})
        if confirmation_analysis.get('confirmation_coverage', 0) < 0.3:
            issues.append(UsabilityIssue(
                severity='major',
                category='feedback',
                description='Insufficient confirmation dialogs for critical actions',
                location='nomadly2_bot.py',
                recommendation='Add confirmation dialogs for payments, deletions, and changes',
                impact='Users may accidentally perform destructive actions'
            ))
        
        # Documentation Issues
        doc_analysis = all_analyses.get('documentation', {})
        if doc_analysis.get('documentation_score', 0) < 0.6:
            issues.append(UsabilityIssue(
                severity='minor',
                category='support',
                description='Incomplete user documentation and help resources',
                location='Documentation files',
                recommendation='Create comprehensive user guides and FAQ',
                impact='Users may not understand features or how to resolve issues'
            ))
        
        return issues
    
    def generate_usability_report(self) -> Dict[str, Any]:
        """Generate comprehensive usability report"""
        # Analyze bot code
        code_analysis = self.analyze_bot_code_structure()
        
        if 'error' in code_analysis:
            return {'error': code_analysis['error']}
        
        # Perform all analyses
        all_analyses = {
            'complexity': self.evaluate_ui_complexity(code_analysis),
            'messaging': self.analyze_user_messaging(code_analysis),
            'error_handling': self.analyze_error_handling(code_analysis),
            'navigation': self.analyze_navigation_design(code_analysis),
            'confirmation': self.analyze_confirmation_dialogs(code_analysis),
            'documentation': self.check_documentation_completeness()
        }
        
        # Identify issues
        issues = self.identify_usability_issues(all_analyses)
        
        # Calculate overall usability score
        scores = [
            all_analyses['complexity']['complexity_score'],
            all_analyses['messaging']['messaging_quality'],
            all_analyses['error_handling']['error_coverage'],
            all_analyses['navigation']['navigation_density'] * 10,  # Scale to 0-1
            all_analyses['confirmation']['confirmation_coverage'],
            all_analyses['documentation']['documentation_score']
        ]
        
        # Invert complexity score (lower is better)
        scores[0] = 1.0 - scores[0]
        
        overall_score = sum(scores) / len(scores)
        
        if overall_score >= 0.8:
            usability_grade = 'A - Excellent'
        elif overall_score >= 0.7:
            usability_grade = 'B - Good'  
        elif overall_score >= 0.6:
            usability_grade = 'C - Fair'
        elif overall_score >= 0.5:
            usability_grade = 'D - Poor'
        else:
            usability_grade = 'F - Critical Issues'
        
        return {
            'overall_score': overall_score,
            'usability_grade': usability_grade,
            'code_metrics': code_analysis,
            'detailed_analyses': all_analyses,
            'usability_issues': issues,
            'critical_issues': [i for i in issues if i.severity == 'critical'],
            'major_issues': [i for i in issues if i.severity == 'major'],
            'minor_issues': [i for i in issues if i.severity == 'minor']
        }

async def test_usability_system():
    """Test the usability analysis system"""
    print("🧪 TESTING USABILITY ANALYSIS SYSTEM")
    print("=" * 50)
    
    analyzer = UsabilityAnalyzer()
    
    # Generate comprehensive usability report
    print("📊 Generating usability report...")
    report = analyzer.generate_usability_report()
    
    if 'error' in report:
        print(f"❌ Error generating report: {report['error']}")
        return
    
    # Display results
    print(f"\n🎯 OVERALL USABILITY ASSESSMENT")
    print(f"Score: {report['overall_score']:.2f}/1.00")
    print(f"Grade: {report['usability_grade']}")
    
    print(f"\n📊 CODE METRICS:")
    metrics = report['code_metrics']
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print(f"\n📈 DETAILED ANALYSIS:")
    for category, analysis in report['detailed_analyses'].items():
        print(f"\n{category.upper()}:")
        status_key = f"{category}_status" if f"{category}_status" in analysis else 'status'
        if status_key in analysis:
            print(f"  Status: {analysis[status_key]}")
        
        if 'recommendations' in analysis and analysis['recommendations']:
            print("  Recommendations:")
            for rec in analysis['recommendations']:
                print(f"    • {rec}")
    
    # Display issues by severity
    print(f"\n🚨 USABILITY ISSUES FOUND:")
    
    critical_issues = report.get('critical_issues', [])
    major_issues = report.get('major_issues', [])
    minor_issues = report.get('minor_issues', [])
    
    if critical_issues:
        print(f"\n❌ CRITICAL ISSUES ({len(critical_issues)}):")
        for issue in critical_issues:
            print(f"  • {issue.description}")
            print(f"    Recommendation: {issue.recommendation}")
            print(f"    Impact: {issue.impact}")
    
    if major_issues:
        print(f"\n⚠️ MAJOR ISSUES ({len(major_issues)}):")
        for issue in major_issues:
            print(f"  • {issue.description}")
            print(f"    Recommendation: {issue.recommendation}")
    
    if minor_issues:
        print(f"\n📋 MINOR ISSUES ({len(minor_issues)}):")
        for issue in minor_issues:
            print(f"  • {issue.description}")
    
    # Priority recommendations
    all_recommendations = []
    for analysis in report['detailed_analyses'].values():
        all_recommendations.extend(analysis.get('recommendations', []))
    
    if all_recommendations:
        print(f"\n💡 TOP PRIORITY RECOMMENDATIONS:")
        unique_recs = list(set(all_recommendations))[:5]
        for rec in unique_recs:
            print(f"• {rec}")

if __name__ == "__main__":
    asyncio.run(test_usability_system())