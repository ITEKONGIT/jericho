#!/usr/bin/env python3
"""
Jericho Supabase Findings Aggregator
Combines all audit results into a single comprehensive report
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self, output_file='supabase_report.html'):
        self.output_file = output_file
        self.results = {}
        self.severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
    
    def load_results(self):
        """Load all JSON result files"""
        files = [
            'recon_results.json',
            'auth_findings.json',
            'rls_audit_results.json',
            'schema_enumeration.json',
            'function_audit.json',
            'storage_audit.json',
            'realtime_audit.json',
            'key_exposure.json'
        ]
        
        for file in files:
            if Path(file).exists():
                try:
                    with open(file, 'r') as f:
                        self.results[file.replace('.json', '')] = json.load(f)
                        print(f"[+] Loaded {file}")
                except Exception as e:
                    print(f"[-] Error loading {file}: {e}")
        
        if not self.results:
            print("[-] No result files found. Run audits first.")
            return False
        
        return True
    
    def aggregate_findings(self):
        """Aggregate all findings from different modules"""
        all_findings = []
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        
        # Import findings from RLS audit
        if 'rls_audit_results' in self.results:
            data = self.results['rls_audit_results']
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    all_findings.append({
                        'module': 'RLS Audit',
                        'severity': vuln.get('severity', 'MEDIUM'),
                        'finding': vuln.get('finding', 'Unknown'),
                        'detail': vuln.get('detail', ''),
                        'evidence': vuln.get('evidence', None)
                    })
        
        # Import findings from Auth audit
        if 'auth_findings' in self.results:
            for finding in self.results['auth_findings']:
                all_findings.append({
                    'module': 'Auth Audit',
                    'severity': finding.get('severity', 'MEDIUM'),
                    'finding': finding.get('finding', 'Unknown'),
                    'detail': finding.get('detail', ''),
                    'evidence': None
                })
        
        # Import findings from Storage audit
        if 'storage_audit' in self.results:
            data = self.results['storage_audit']
            if 'findings' in data:
                for finding in data['findings']:
                    all_findings.append({
                        'module': 'Storage Audit',
                        'severity': finding.get('severity', 'MEDIUM'),
                        'finding': finding.get('finding', 'Unknown'),
                        'detail': finding.get('detail', ''),
                        'evidence': None
                    })
        
        # Import findings from Realtime audit
        if 'realtime_audit' in self.results:
            for finding in self.results['realtime_audit']:
                all_findings.append({
                    'module': 'Realtime Audit',
                    'severity': finding.get('severity', 'MEDIUM'),
                    'finding': finding.get('finding', 'Unknown'),
                    'detail': finding.get('detail', ''),
                    'evidence': None
                })
        
        # Import findings from Key Exposure
        if 'key_exposure' in self.results:
            data = self.results['key_exposure']
            if 'findings' in data:
                for finding in data['findings']:
                    severity = finding.get('severity', 'MEDIUM')
                    all_findings.append({
                        'module': 'Key Exposure Scanner',
                        'severity': severity,
                        'finding': f"Exposed {finding.get('type', 'key')}",
                        'detail': f"Found in {finding.get('url', 'unknown')}",
                        'evidence': finding.get('value', None)
                    })
        
        # Count severities
        for finding in all_findings:
            severity = finding.get('severity', 'INFO')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return all_findings, severity_counts
    
    def generate_html_report(self, findings, severity_counts):
        """Generate HTML report"""
        print("[*] Generating HTML report...")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Supabase Security Assessment Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .severity-box {{
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            color: white;
            font-weight: bold;
        }}
        .CRITICAL {{ background: #d32f2f; }}
        .HIGH {{ background: #f57c00; }}
        .MEDIUM {{ background: #fbc02d; color: #333; }}
        .LOW {{ background: #388e3c; }}
        .INFO {{ background: #1976d2; }}
        .finding {{
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
        }}
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .severity-tag {{
            padding: 3px 10px;
            border-radius: 3px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        .evidence {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Supabase Security Assessment Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <h2>Executive Summary</h2>
        <div class="summary">
            <div class="severity-box CRITICAL">CRITICAL: {severity_counts.get('CRITICAL', 0)}</div>
            <div class="severity-box HIGH">HIGH: {severity_counts.get('HIGH', 0)}</div>
            <div class="severity-box MEDIUM">MEDIUM: {severity_counts.get('MEDIUM', 0)}</div>
            <div class="severity-box LOW">LOW: {severity_counts.get('LOW', 0)}</div>
            <div class="severity-box INFO">INFO: {severity_counts.get('INFO', 0)}</div>
        </div>
        
        <h2>Total Findings: {len(findings)}</h2>
"""
        
        if not findings:
            html += "<p><strong>No findings recorded.</strong></p>"
        else:
            # Sort findings by severity
            findings.sort(key=lambda x: self.severity_order.get(x.get('severity', 'INFO'), 99))
            
            for finding in findings:
                severity = finding.get('severity', 'INFO')
                module = finding.get('module', 'Unknown')
                title = finding.get('finding', 'Unknown finding')
                detail = finding.get('detail', '')
                evidence = finding.get('evidence', None)
                
                html += f"""
        <div class="finding">
            <div class="finding-header">
                <div>
                    <strong>{title}</strong>
                    <span style="margin-left: 10px; color: #666; font-size: 14px;">[{module}]</span>
                </div>
                <span class="severity-tag {severity}">{severity}</span>
            </div>
            <p style="margin: 10px 0 0 0; color: #444;">{detail}</p>
            """
                
                if evidence:
                    if isinstance(evidence, (dict, list)):
                        evidence_str = json.dumps(evidence, indent=2)
                    else:
                        evidence_str = str(evidence)
                    html += f"""
            <details>
                <summary style="cursor: pointer; color: #1976d2; margin-top: 10px;">View Evidence</summary>
                <div class="evidence"><pre>{evidence_str}</pre></div>
            </details>
            """
                
                html += """
        </div>
        """
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(self.output_file, 'w') as f:
            f.write(html)
        
        print(f"[+] Report generated: {self.output_file}")
    
    def run(self):
        """Generate the report"""
        print("="*60)
        print("JERICHO SUPABASE REPORT GENERATOR")
        print("="*60)
        
        if not self.load_results():
            print("[-] No results to process")
            return
        
        findings, severity_counts = self.aggregate_findings()
        self.generate_html_report(findings, severity_counts)
        
        # Print summary to console
        print("\n" + "="*60)
        print("FINDINGS SUMMARY")
        print("="*60)
        for severity, count in severity_counts.items():
            if count > 0:
                print(f"{severity}: {count}")
        print(f"\nTotal: {len(findings)} findings")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Findings Aggregator")
    parser.add_argument("-o", "--output", default="supabase_report.html", help="Output HTML report file")
    args = parser.parse_args()
    
    generator = ReportGenerator(args.output)
    generator.run()

if __name__ == "__main__":
    main()
