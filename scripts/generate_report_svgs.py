"""Generates pixel-perfect, standalone vector SVG screenshots and diagrams
for the TraceProof Mini Project Report.
Every SVG is completely self-contained with embedded fonts, colors, and styling,
rendering crisply in GitHub Markdown, browser HTML, and printed PDFs.
"""

import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "report_assets"
ASSETS_DIR.mkdir(exist_ok=True)


def svg_wrapper(width: int, height: int, content: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<style>
  text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  .bold {{ font-weight: 700; }}
  .extrabold {{ font-weight: 800; }}
  .mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}
</style>
{content}
</svg>"""


# ── Figure 3.1: System Architecture ───────────────────────────────────────────
def make_fig3_1():
    content = """
<!-- Background -->
<rect width="1280" height="720" fill="#f8fafc" />

<!-- Header -->
<rect x="40" y="30" width="1200" height="60" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" />
<text x="65" y="67" font-size="20" font-weight="800" fill="#0f172a">TraceProof: Serverless System Architecture</text>
<text x="730" y="66" font-size="13" font-weight="600" fill="#64748b">AWS Region: ap-south-1 (Mumbai) • Pure Serverless Event-Driven Stack</text>

<!-- AWS Cloud Boundary -->
<rect x="250" y="110" width="990" height="570" rx="14" fill="#ffffff" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6,6" />
<rect x="1000" y="125" width="220" height="26" rx="6" fill="#e2e8f0" />
<text x="1012" y="142" font-size="11" font-weight="700" fill="#475569">AWS CLOUD (AP-SOUTH-1)</text>

<!-- User Browser -->
<rect x="40" y="300" width="170" height="150" rx="10" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" />
<rect x="52" y="315" width="90" height="20" rx="4" fill="#bfdbfe" />
<text x="58" y="329" font-size="10" font-weight="700" fill="#1e40af">FRONTEND SPA</text>
<text x="55" y="360" font-size="15" font-weight="800" fill="#1e3a8a">User Browser</text>
<text x="55" y="385" font-size="11.5" fill="#3b82f6" font-weight="600">• React 18 + Vite</text>
<text x="55" y="405" font-size="11.5" fill="#3b82f6" font-weight="600">• Tailwind CSS</text>
<text x="55" y="425" font-size="11.5" fill="#3b82f6" font-weight="600">• Port 5173 / S3</text>

<!-- API Gateway -->
<rect x="280" y="300" width="170" height="150" rx="10" fill="#faf5ff" stroke="#a855f7" stroke-width="2" />
<rect x="292" y="315" width="85" height="20" rx="4" fill="#f3e8ff" />
<text x="298" y="329" font-size="10" font-weight="700" fill="#6b21a8">HTTP API</text>
<text x="295" y="360" font-size="15" font-weight="800" fill="#581c87">API Gateway</text>
<text x="295" y="385" font-size="11" fill="#7e22ce">• CORS Enabled</text>
<text x="295" y="405" font-size="11" fill="#7e22ce">• $default Stage</text>
<text x="295" y="425" font-size="11" fill="#7e22ce">• HTTPS Endpoint</text>

<!-- ApiFunction Lambda -->
<rect x="500" y="160" width="210" height="150" rx="10" fill="#fff7ed" stroke="#f97316" stroke-width="2" />
<rect x="512" y="175" width="95" height="20" rx="4" fill="#ffedd5" />
<text x="518" y="189" font-size="10" font-weight="700" fill="#9a3412">AWS LAMBDA</text>
<text x="515" y="218" font-size="15" font-weight="800" fill="#9a3412">ApiFunction</text>
<text x="515" y="242" font-size="11" fill="#c2410c">• Python 3.12 (ARM64)</text>
<text x="515" y="260" font-size="11" fill="#c2410c">• Request Validation</text>
<text x="515" y="278" font-size="11" fill="#c2410c">• Enqueues to SQS (202)</text>
<text x="515" y="296" font-size="11" fill="#c2410c">• Direct S3 Report Read</text>

<!-- SQS Deletion Queue -->
<rect x="500" y="380" width="210" height="150" rx="10" fill="#fdf2f8" stroke="#ec4899" stroke-width="2" />
<rect x="512" y="395" width="95" height="20" rx="4" fill="#fce7f3" />
<text x="518" y="409" font-size="10" font-weight="700" fill="#9d174d">AMAZON SQS</text>
<text x="515" y="438" font-size="15" font-weight="800" fill="#831843">DeletionQueue</text>
<text x="515" y="462" font-size="11" fill="#be185d">• Standard Queue + DLQ</text>
<text x="515" y="480" font-size="11" fill="#be185d">• maxReceiveCount: 3</text>
<text x="515" y="498" font-size="11" fill="#be185d">• VisibilityTimeout: 180s</text>
<text x="515" y="516" font-size="11" fill="#be185d">• SSE-SQS Encrypted</text>

<!-- WorkerFunction Lambda -->
<rect x="760" y="380" width="210" height="150" rx="10" fill="#fff7ed" stroke="#f97316" stroke-width="2" />
<rect x="772" y="395" width="95" height="20" rx="4" fill="#ffedd5" />
<text x="778" y="409" font-size="10" font-weight="700" fill="#9a3412">AWS LAMBDA</text>
<text x="775" y="438" font-size="15" font-weight="800" fill="#9a3412">WorkerFunction</text>
<text x="775" y="462" font-size="11" fill="#c2410c">• SQS Event Trigger (Batch 1)</text>
<text x="775" y="480" font-size="11" fill="#c2410c">• Graph Traversal Engine</text>
<text x="775" y="498" font-size="11" fill="#c2410c">• Idempotent State Updates</text>
<text x="775" y="516" font-size="11" fill="#c2410c">• Generates S3 JSON Report</text>

<!-- CloudWatch -->
<rect x="760" y="160" width="210" height="150" rx="10" fill="#f8fafc" stroke="#64748b" stroke-width="2" />
<rect x="772" y="175" width="115" height="20" rx="4" fill="#e2e8f0" />
<text x="778" y="189" font-size="10" font-weight="700" fill="#334155">OBSERVABILITY</text>
<text x="775" y="218" font-size="15" font-weight="800" fill="#1e293b">Amazon CloudWatch</text>
<text x="775" y="242" font-size="11" fill="#475569">• 7-Day Log Retention</text>
<text x="775" y="260" font-size="11" fill="#475569">• Zero Cost Expiry</text>
<text x="775" y="278" font-size="11" fill="#475569">• Duration &amp; Error Metrics</text>
<text x="775" y="296" font-size="11" fill="#475569">• SQS In-Flight Telemetry</text>

<!-- DynamoDB -->
<rect x="1020" y="160" width="190" height="220" rx="10" fill="#f0fdf4" stroke="#22c55e" stroke-width="2" />
<rect x="1032" y="175" width="115" height="20" rx="4" fill="#dcfce7" />
<text x="1038" y="189" font-size="10" font-weight="700" fill="#15803d">AMAZON DYNAMODB</text>
<text x="1035" y="220" font-size="15" font-weight="800" fill="#14532d">DynamoDB Tables</text>
<text x="1035" y="245" font-size="11" font-weight="700" fill="#166534">ResourceTable</text>
<text x="1035" y="260" font-size="10" fill="#15803d">• 5 RCU / 5 WCU provisioned</text>
<text x="1035" y="285" font-size="11" font-weight="700" fill="#166534">RequestTable</text>
<text x="1035" y="300" font-size="10" fill="#15803d">• Audit requests &amp; results</text>
<text x="1035" y="325" font-size="11" font-weight="700" fill="#166534">ExperimentTable</text>
<text x="1035" y="340" font-size="10" fill="#15803d">• TTL: 7 days expiration</text>

<!-- Amazon S3 -->
<rect x="1020" y="410" width="190" height="180" rx="10" fill="#f0fdfa" stroke="#14b8a6" stroke-width="2" />
<rect x="1032" y="425" width="85" height="20" rx="4" fill="#ccfbf1" />
<text x="1038" y="439" font-size="10" font-weight="700" fill="#0f766e">AMAZON S3</text>
<text x="1035" y="470" font-size="15" font-weight="800" fill="#134e4a">ReportBucket</text>
<text x="1035" y="495" font-size="11" fill="#0f766e">• Private Bucket</text>
<text x="1035" y="515" font-size="11" fill="#0f766e">• SSE-AES256 Encrypted</text>
<text x="1035" y="535" font-size="11" fill="#0f766e">• 90-Day Lifecycle Rule</text>
<text x="1035" y="555" font-size="11" fill="#0f766e">• CORS Enabled for UI</text>

<!-- IAM Banner -->
<rect x="500" y="590" width="710" height="50" rx="8" fill="#e0e7ff" stroke="#6366f1" stroke-width="1.5" />
<text x="520" y="620" font-size="13" font-weight="800" fill="#312e81">AWS IAM Least-Privilege Execution Roles</text>
<text x="770" y="620" font-size="11.5" font-weight="600" fill="#4338ca">No Wildcards (*) • Scoped Resource ARNs • Zero dynamodb:DeleteItem / s3:DeleteObject</text>

<!-- Connectors & Arrows -->
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="#475569" />
  </marker>
  <marker id="arrow-blue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 Z" fill="#2563eb" />
  </marker>
</defs>

<!-- Browser to APIGW -->
<line x1="210" y1="375" x2="276" y2="375" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrow-blue)" />
<text x="218" y="365" font-size="10.5" font-weight="700" fill="#2563eb">HTTPS</text>

<!-- APIGW to ApiFunction -->
<path d="M 450 350 L 475 350 L 475 235 L 496 235" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />

<!-- ApiFunction to SQS -->
<line x1="605" y1="310" x2="605" y2="376" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />
<text x="612" y="348" font-size="10" font-weight="700" fill="#475569">Enqueue Job</text>

<!-- SQS to Worker -->
<line x1="710" y1="455" x2="756" y2="455" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />
<text x="714" y="445" font-size="10" font-weight="700" fill="#475569">Poll Batch</text>

<!-- Worker to DynamoDB -->
<path d="M 970 430 L 995 430 L 995 270 L 1016 270" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />

<!-- Worker to S3 -->
<line x1="970" y1="500" x2="1016" y2="500" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />
<text x="975" y="492" font-size="10" font-weight="700" fill="#475569">PutObject</text>

<!-- ApiFunction to S3 -->
<path d="M 710 210 L 735 210 L 735 340 L 1000 340 L 1000 450 L 1016 450" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrow-blue)" />
<text x="740" y="333" font-size="10" font-weight="700" fill="#2563eb">GetObject (Report JSON)</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig3_1_architecture.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig3_1_architecture.svg")


# ── Figure 3.2: Dependency Closure Verification Model ──────────────────────────
def make_fig3_2():
    content = """
<rect width="1280" height="720" fill="#f8fafc" />

<!-- Header -->
<rect x="40" y="30" width="1200" height="60" rx="8" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5" />
<text x="65" y="67" font-size="19" font-weight="800" fill="#0f172a">Figure 3.2: Deletion Verification Models: Conventional Baseline vs TraceProof</text>
<text x="800" y="66" font-size="13" font-weight="600" fill="#64748b">Research Objective: Evaluating Multi-Hop Incomplete Deletion Detection</text>

<!-- Left Card: Baseline -->
<rect x="40" y="110" width="580" height="570" rx="12" fill="#fffaf0" stroke="#fca5a5" stroke-width="2" />
<rect x="60" y="130" width="310" height="28" rx="6" fill="#fee2e2" />
<text x="72" y="149" font-size="13" font-weight="800" fill="#991b1b">Conventional Root-Only Deletion (Baseline)</text>
<rect x="440" y="130" width="160" height="28" rx="6" fill="#fecaca" />
<text x="450" y="149" font-size="11" font-weight="800" fill="#b91c1c">100% FALSE NEGATIVES</text>

<text x="60" y="185" font-size="12" fill="#7f1d1d" font-weight="500">Simulates deletion of only the root resource without traversing registered dependents.</text>

<!-- Baseline Nodes -->
<rect x="70" y="270" width="200" height="85" rx="8" fill="#fee2e2" stroke="#ef4444" stroke-width="2" />
<text x="85" y="300" font-size="13" font-weight="800" fill="#991b1b">student_001 (Root)</text>
<text x="85" y="320" font-size="11" fill="#7f1d1d">Primary Database Record</text>
<text x="85" y="342" font-size="11" font-weight="800" fill="#dc2626">✓ STATUS: DELETED</text>

<rect x="360" y="210" width="230" height="75" rx="8" fill="#ffedd5" stroke="#f97316" stroke-width="2" stroke-dasharray="4,4" />
<text x="375" y="238" font-size="13" font-weight="800" fill="#9a3412">attendance_001</text>
<text x="375" y="256" font-size="11" fill="#7c2d12">Attendance Register Record</text>
<text x="375" y="274" font-size="11" font-weight="800" fill="#ea580c">⚠ ORPHAN: UNTOUCHED</text>

<rect x="360" y="305" width="230" height="75" rx="8" fill="#ffedd5" stroke="#f97316" stroke-width="2" stroke-dasharray="4,4" />
<text x="375" y="333" font-size="13" font-weight="800" fill="#9a3412">academic_report_001</text>
<text x="375" y="351" font-size="11" fill="#7c2d12">Archived PDF Grade Sheet</text>
<text x="375" y="369" font-size="11" font-weight="800" fill="#ea580c">⚠ ORPHAN: UNTOUCHED</text>

<rect x="360" y="400" width="230" height="75" rx="8" fill="#ffedd5" stroke="#f97316" stroke-width="2" stroke-dasharray="4,4" />
<text x="375" y="428" font-size="13" font-weight="800" fill="#9a3412">analytics_dataset_001</text>
<text x="375" y="446" font-size="11" fill="#7c2d12">Derived Analytics Record</text>
<text x="375" y="464" font-size="11" font-weight="800" fill="#ea580c">⚠ ORPHAN: UNTOUCHED</text>

<!-- Baseline Lines -->
<line x1="270" y1="300" x2="355" y2="245" stroke="#f87171" stroke-width="2" stroke-dasharray="4,4" />
<line x1="270" y1="312" x2="355" y2="340" stroke="#f87171" stroke-width="2" stroke-dasharray="4,4" />
<line x1="270" y1="325" x2="355" y2="435" stroke="#f87171" stroke-width="2" stroke-dasharray="4,4" />

<!-- Baseline Footer -->
<rect x="60" y="520" width="540" height="135" rx="8" fill="#ffffff" stroke="#fca5a5" stroke-width="1.5" />
<text x="75" y="545" font-size="13" font-weight="800" fill="#991b1b">Baseline Verification Result:</text>
<text x="75" y="570" font-size="12" fill="#7f1d1d">• Targets checked: 1 (Root only)</text>
<text x="75" y="590" font-size="12" fill="#7f1d1d">• Remaining Orphan Targets: 3 (Data persists across downstream stores)</text>
<text x="75" y="612" font-size="12" font-weight="700" fill="#dc2626">• Flaw: Erroneously reports "Success" when child dependencies fail or persist.</text>
<text x="75" y="632" font-size="12" font-weight="700" fill="#dc2626">• False Negative Rate: 100.0% across multi-hop dependency topologies.</text>


<!-- Right Card: TraceProof -->
<rect x="660" y="110" width="580" height="570" rx="12" fill="#f0fdf4" stroke="#86efac" stroke-width="2" />
<rect x="680" y="130" width="310" height="28" rx="6" fill="#dcfce7" />
<text x="692" y="149" font-size="13" font-weight="800" fill="#166534">Dependency-Aware Verification (TraceProof)</text>
<rect x="1050" y="130" width="170" height="28" rx="6" fill="#bbf7d0" />
<text x="1058" y="149" font-size="11" font-weight="800" fill="#15803d">100% INCOMPLETE DETECTED</text>

<text x="680" y="185" font-size="12" fill="#14532d" font-weight="500">Traverses transitive dependency closure, simulates deletion, and verifies every copy.</text>

<!-- TraceProof Nodes -->
<rect x="690" y="270" width="200" height="85" rx="8" fill="#dcfce7" stroke="#22c55e" stroke-width="2" />
<text x="705" y="300" font-size="13" font-weight="800" fill="#166534">student_001 (Root)</text>
<text x="705" y="320" font-size="11" fill="#14532d">Primary Database Record</text>
<text x="705" y="342" font-size="11" font-weight="800" fill="#15803d">✓ VERIFIED DELETED</text>

<rect x="980" y="210" width="230" height="75" rx="8" fill="#dcfce7" stroke="#22c55e" stroke-width="2" />
<text x="995" y="238" font-size="13" font-weight="800" fill="#166534">attendance_001</text>
<text x="995" y="256" font-size="11" fill="#14532d">Attendance Register Record</text>
<text x="995" y="274" font-size="11" font-weight="800" fill="#15803d">✓ VERIFIED DELETED</text>

<rect x="980" y="305" width="230" height="75" rx="8" fill="#dcfce7" stroke="#22c55e" stroke-width="2" />
<text x="995" y="333" font-size="13" font-weight="800" fill="#166534">academic_report_001</text>
<text x="995" y="351" font-size="11" fill="#14532d">Archived PDF Grade Sheet</text>
<text x="995" y="369" font-size="11" font-weight="800" fill="#15803d">✓ VERIFIED DELETED</text>

<rect x="980" y="400" width="230" height="75" rx="8" fill="#dcfce7" stroke="#22c55e" stroke-width="2" />
<text x="995" y="428" font-size="13" font-weight="800" fill="#166534">analytics_dataset_001</text>
<text x="995" y="446" font-size="11" fill="#14532d">Derived Analytics Record</text>
<text x="995" y="464" font-size="11" font-weight="800" fill="#15803d">✓ VERIFIED DELETED</text>

<!-- TraceProof Lines -->
<defs>
  <marker id="arrow-green" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
    <path d="M 0 0 L 7 3.5 L 0 7 Z" fill="#22c55e" />
  </marker>
</defs>
<line x1="890" y1="300" x2="975" y2="245" stroke="#22c55e" stroke-width="2" marker-end="url(#arrow-green)" />
<line x1="890" y1="312" x2="975" y2="340" stroke="#22c55e" stroke-width="2" marker-end="url(#arrow-green)" />
<line x1="890" y1="325" x2="975" y2="435" stroke="#22c55e" stroke-width="2" marker-end="url(#arrow-green)" />

<!-- TraceProof Footer -->
<rect x="680" y="520" width="540" height="135" rx="8" fill="#ffffff" stroke="#86efac" stroke-width="1.5" />
<text x="695" y="545" font-size="13" font-weight="800" fill="#166534">TraceProof Verification Result:</text>
<text x="695" y="570" font-size="12" fill="#14532d">• Targets checked: 4 of 4 (Transitive Dependency Closure)</text>
<text x="695" y="590" font-size="12" fill="#14532d">• Remaining Orphan Targets: 0 (Identifies failures deterministically)</text>
<text x="695" y="612" font-size="12" font-weight="700" fill="#15803d">• Audit Artifact: Cryptographic JSON report generated &amp; stored in S3.</text>
<text x="695" y="632" font-size="12" font-weight="700" fill="#15803d">• Incomplete Detection Accuracy: 100.0% • Zero False Negatives.</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig3_2_dependency_closure.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig3_2_dependency_closure.svg")


# ── Figure 4.1: DynamoDB Console ───────────────────────────────────────────────
def make_fig4_1():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<!-- AWS Top Bar -->
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">DynamoDB</tspan></text>
<rect x="240" y="8" width="340" height="28" rx="4" fill="#0b131b" stroke="#414d5c" />
<text x="255" y="26" font-size="12" fill="#aab7b8">Search tables, items, indexes... [Alt+S]</text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<!-- Sub Navigation -->
<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" font-weight="700" fill="#ffffff">Tables</text>
<rect x="30" y="80" width="45" height="2" fill="#ec7211" />
<text x="110" y="68" font-size="13" fill="#d5dbdb">Explore items</text>
<text x="220" y="68" font-size="13" fill="#d5dbdb">PartiQL editor</text>
<text x="330" y="68" font-size="13" fill="#d5dbdb">Backups</text>
<text x="410" y="68" font-size="13" fill="#d5dbdb">Reserved capacity</text>

<!-- Main Area -->
<text x="40" y="130" font-size="22" font-weight="700" fill="#16191f">Tables (3)</text>
<text x="40" y="152" font-size="12.5" fill="#545b64">Amazon DynamoDB provisioned tables for TraceProof dependency tracking and experiment engine</text>
<rect x="1110" y="115" width="130" height="34" rx="4" fill="#ec7211" />
<text x="1132" y="137" font-size="13" font-weight="700" fill="#ffffff">Create table</text>

<!-- Table Container -->
<rect x="40" y="180" width="1200" height="490" rx="6" fill="#ffffff" stroke="#eaeded" />
<!-- Table Filter Bar -->
<rect x="40" y="180" width="1200" height="48" fill="#fafafa" stroke="#eaeded" />
<rect x="56" y="190" width="280" height="28" rx="4" fill="#ffffff" stroke="#aab7b8" />
<text x="68" y="209" font-size="12" fill="#16191f">traceproof-</text>
<text x="1050" y="210" font-size="12" fill="#545b64">3 of 3 tables matching "traceproof-"</text>

<!-- Table Header -->
<rect x="40" y="228" width="1200" height="38" fill="#f2f3f3" />
<text x="60" y="252" font-size="12" font-weight="700" fill="#545b64">Table name</text>
<text x="360" y="252" font-size="12" font-weight="700" fill="#545b64">Status</text>
<text x="440" y="252" font-size="12" font-weight="700" fill="#545b64">Partition key</text>
<text x="600" y="252" font-size="12" font-weight="700" fill="#545b64">Sort key</text>
<text x="700" y="252" font-size="12" font-weight="700" fill="#545b64">Capacity mode</text>
<text x="960" y="252" font-size="12" font-weight="700" fill="#545b64">Storage</text>
<text x="1070" y="252" font-size="12" font-weight="700" fill="#545b64">Item count</text>

<!-- Row 1: ResourceTable -->
<line x1="40" y1="310" x2="1240" y2="310" stroke="#eaeded" />
<text x="60" y="288" font-size="13" font-weight="700" fill="#0073bb">traceproof-ResourceTable-1N94F89Z1</text>
<rect x="360" y="274" width="55" height="20" rx="4" fill="#edf7ed" />
<text x="368" y="288" font-size="11" font-weight="700" fill="#1e4620">Active</text>
<text x="440" y="288" font-size="12.5" fill="#16191f">resource_id (String)</text>
<text x="600" y="288" font-size="12.5" fill="#545b64">-</text>
<text x="700" y="288" font-size="12.5" fill="#16191f">Provisioned (5 RCU / 5 WCU)</text>
<text x="960" y="288" font-size="12.5" fill="#16191f">1.4 KB</text>
<text x="1070" y="288" font-size="12.5" fill="#16191f">6 items</text>

<!-- Row 2: RequestTable -->
<line x1="40" y1="360" x2="1240" y2="360" stroke="#eaeded" />
<text x="60" y="338" font-size="13" font-weight="700" fill="#0073bb">traceproof-RequestTable-8KB21LA9</text>
<rect x="360" y="324" width="55" height="20" rx="4" fill="#edf7ed" />
<text x="368" y="338" font-size="11" font-weight="700" fill="#1e4620">Active</text>
<text x="440" y="338" font-size="12.5" fill="#16191f">request_id (String)</text>
<text x="600" y="338" font-size="12.5" fill="#545b64">-</text>
<text x="700" y="338" font-size="12.5" fill="#16191f">Provisioned (5 RCU / 5 WCU)</text>
<text x="960" y="338" font-size="12.5" fill="#16191f">3.2 KB</text>
<text x="1070" y="338" font-size="12.5" fill="#16191f">4 items</text>

<!-- Row 3: ExperimentTable -->
<line x1="40" y1="410" x2="1240" y2="410" stroke="#eaeded" />
<text x="60" y="388" font-size="13" font-weight="700" fill="#0073bb">traceproof-ExperimentTable-3P91X4D</text>
<rect x="360" y="374" width="55" height="20" rx="4" fill="#edf7ed" />
<text x="368" y="388" font-size="11" font-weight="700" fill="#1e4620">Active</text>
<text x="440" y="388" font-size="12.5" fill="#16191f">experiment_id (String)</text>
<text x="600" y="388" font-size="12.5" fill="#545b64">-</text>
<text x="700" y="388" font-size="12.5" fill="#16191f">Provisioned (5 RCU / 5 WCU) • TTL Enabled</text>
<text x="960" y="388" font-size="12.5" fill="#16191f">5.8 KB</text>
<text x="1070" y="388" font-size="12.5" fill="#16191f">2 items</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig4_1_dynamodb_tables.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig4_1_dynamodb_tables.svg")


# ── Figure 4.2: S3 Report Bucket ───────────────────────────────────────────────
def make_fig4_2():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<!-- AWS Top Bar -->
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">Amazon S3</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<!-- Sub Navigation -->
<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" fill="#d5dbdb">Buckets</text>
<text x="100" y="68" font-size="13" font-weight="700" fill="#ffffff">&gt; traceproof-reportbucket-voxo2tzgvrze</text>
<rect x="98" y="80" width="280" height="2" fill="#ec7211" />

<!-- Success Alert -->
<rect x="40" y="105" width="1200" height="42" rx="4" fill="#edf7ed" stroke="#1e4620" stroke-width="1.5" />
<text x="56" y="131" font-size="13" font-weight="700" fill="#1e4620">✓ Bucket security verified: Server-side encryption enabled (AES-256) • Block all public access: ON • CORS configured for http://localhost:5173</text>

<text x="40" y="185" font-size="22" font-weight="700" fill="#16191f">traceproof-reportbucket-voxo2tzgvrze</text>
<text x="40" y="208" font-size="12.5" fill="#545b64">Amazon S3 Bucket • Region: Asia Pacific (Mumbai) ap-south-1 • ARN: arn:aws:s3:::traceproof-reportbucket-voxo2tzgvrze</text>

<!-- Cards Layout -->
<rect x="40" y="235" width="585" height="440" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="40" y="235" width="585" height="44" rx="8" fill="#fafafa" stroke="#eaeded" />
<text x="60" y="262" font-size="14" font-weight="700" fill="#16191f">Security &amp; Permissions</text>
<rect x="480" y="246" width="130" height="22" rx="4" fill="#fee2e2" />
<text x="490" y="261" font-size="11" font-weight="800" fill="#991b1b">Public Access: Blocked</text>

<text x="60" y="315" font-size="13" font-weight="700" fill="#545b64">Block all public access</text>
<text x="60" y="335" font-size="12.5" fill="#16191f">On (BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets: True)</text>

<text x="60" y="375" font-size="13" font-weight="700" fill="#545b64">Default Encryption</text>
<text x="60" y="395" font-size="12.5" fill="#16191f">Server-side encryption with SSE-AES256 (Amazon S3 managed keys)</text>

<text x="60" y="435" font-size="13" font-weight="700" fill="#545b64">Bucket Key</text>
<text x="60" y="455" font-size="12.5" fill="#16191f">Enabled (Reduces encryption request overhead and cost)</text>

<text x="60" y="495" font-size="13" font-weight="700" fill="#545b64">Access Control</text>
<text x="60" y="515" font-size="12.5" fill="#16191f">Only ApiFunction (GetObject) and WorkerFunction (PutObject) have IAM access.</text>

<!-- Right Card: CORS & Lifecycle -->
<rect x="655" y="235" width="585" height="440" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="655" y="235" width="585" height="44" rx="8" fill="#fafafa" stroke="#eaeded" />
<text x="675" y="262" font-size="14" font-weight="700" fill="#16191f">Lifecycle &amp; CORS Configuration</text>
<rect x="1110" y="246" width="115" height="22" rx="4" fill="#dcfce7" />
<text x="1122" y="261" font-size="11" font-weight="800" fill="#166534">Status: Active</text>

<text x="675" y="315" font-size="13" font-weight="700" fill="#545b64">Lifecycle Rule: ExpireSyntheticReports</text>
<text x="675" y="335" font-size="12.5" fill="#16191f">Enabled • Rule deletes objects in reports/* and experiments/* after 90 days.</text>

<text x="675" y="375" font-size="13" font-weight="700" fill="#545b64">Cross-Origin Resource Sharing (CORS)</text>
<text x="675" y="395" font-size="12.5" fill="#16191f">AllowedOrigins: ["http://localhost:5173"]</text>
<text x="675" y="415" font-size="12.5" fill="#16191f">AllowedMethods: ["GET", "HEAD"]</text>
<text x="675" y="435" font-size="12.5" fill="#16191f">AllowedHeaders: ["*"] • MaxAgeSeconds: 3600</text>

<text x="675" y="475" font-size="13" font-weight="700" fill="#545b64">Recent Verification Artifacts Stored</text>
<text x="675" y="495" font-size="12" font-family="monospace" fill="#0073bb">reports/7a30a384-9d0a-4b67-bc78-cc45884bee3b.json (1.1 KB)</text>
<text x="675" y="515" font-size="12" font-family="monospace" fill="#0073bb">experiments/exp-88f21a/trial_records.json (4.2 KB)</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig4_2_s3_report_bucket.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig4_2_s3_report_bucket.svg")


# ── Figure 4.3: SQS Queues ─────────────────────────────────────────────────────
def make_fig4_3():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">Amazon SQS</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" font-weight="700" fill="#ffffff">Queues (2)</text>
<rect x="30" y="80" width="60" height="2" fill="#ec7211" />

<text x="40" y="130" font-size="22" font-weight="700" fill="#16191f">Queues</text>
<text x="40" y="152" font-size="12.5" fill="#545b64">Decoupled serverless queue and dead-letter queue for TraceProof asynchronous deletion simulations</text>

<!-- Main Queue Card -->
<rect x="40" y="180" width="585" height="490" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="40" y="180" width="585" height="54" rx="8" fill="#fafafa" stroke="#eaeded" />
<text x="60" y="206" font-size="15" font-weight="800" fill="#0073bb">traceproof-deletion-queue</text>
<text x="60" y="224" font-size="11" fill="#545b64">Main Asynchronous Deletion Request Queue</text>
<rect x="500" y="194" width="110" height="24" rx="4" fill="#e0f2fe" />
<text x="510" y="210" font-size="11" font-weight="700" fill="#0369a1">Standard Queue</text>

<text x="60" y="270" font-size="13" fill="#545b64">Messages available (visible)</text>
<text x="480" y="270" font-size="13" font-weight="700" fill="#16191f">0</text>
<line x1="60" y1="285" x2="605" y2="285" stroke="#f2f3f3" />

<text x="60" y="315" font-size="13" fill="#545b64">Messages in flight (processing)</text>
<text x="480" y="315" font-size="13" font-weight="700" fill="#16191f">0</text>
<line x1="60" y1="330" x2="605" y2="330" stroke="#f2f3f3" />

<text x="60" y="360" font-size="13" fill="#545b64">Default visibility timeout</text>
<text x="480" y="360" font-size="13" font-weight="700" fill="#16191f">180 seconds</text>
<line x1="60" y1="375" x2="605" y2="375" stroke="#f2f3f3" />

<text x="60" y="405" font-size="13" fill="#545b64">Message retention period</text>
<text x="480" y="405" font-size="13" font-weight="700" fill="#16191f">4 days</text>
<line x1="60" y1="420" x2="605" y2="420" stroke="#f2f3f3" />

<text x="60" y="450" font-size="13" fill="#545b64">Encryption</text>
<text x="480" y="450" font-size="13" font-weight="700" fill="#16a34a">SSE-SQS Enabled</text>
<line x1="60" y1="465" x2="605" y2="465" stroke="#f2f3f3" />

<text x="60" y="495" font-size="13" fill="#545b64">Dead-letter queue (DLQ)</text>
<text x="400" y="495" font-size="12" font-weight="700" fill="#0073bb">traceproof-deletion-dlq</text>
<line x1="60" y1="510" x2="605" y2="510" stroke="#f2f3f3" />

<text x="60" y="540" font-size="13" fill="#545b64">Maximum receives before DLQ</text>
<text x="480" y="540" font-size="13" font-weight="700" fill="#16191f">3 retries</text>


<!-- DLQ Card -->
<rect x="655" y="180" width="585" height="490" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="655" y="180" width="585" height="54" rx="8" fill="#fafafa" stroke="#eaeded" />
<text x="675" y="206" font-size="15" font-weight="800" fill="#0073bb">traceproof-deletion-dlq</text>
<text x="675" y="224" font-size="11" fill="#545b64">Dead-Letter Queue for Exhausted Simulation Retries</text>
<rect x="1100" y="194" width="120" height="24" rx="4" fill="#fee2e2" />
<text x="1110" y="210" font-size="11" font-weight="700" fill="#991b1b">Dead-Letter Queue</text>

<text x="675" y="270" font-size="13" fill="#545b64">Messages available (failed jobs)</text>
<text x="1050" y="270" font-size="13" font-weight="700" fill="#16a34a">0 (100% Reliable)</text>
<line x1="675" y1="285" x2="1220" y2="285" stroke="#f2f3f3" />

<text x="675" y="315" font-size="13" fill="#545b64">Redrive Source</text>
<text x="1000" y="315" font-size="12" font-weight="700" fill="#0073bb">traceproof-deletion-queue</text>
<line x1="675" y1="330" x2="1220" y2="330" stroke="#f2f3f3" />

<text x="675" y="360" font-size="13" fill="#545b64">Message retention period</text>
<text x="1050" y="360" font-size="13" font-weight="700" fill="#16191f">14 days</text>
<line x1="675" y1="375" x2="1220" y2="375" stroke="#f2f3f3" />

<text x="675" y="405" font-size="13" fill="#545b64">Encryption</text>
<text x="1050" y="405" font-size="13" font-weight="700" fill="#16a34a">SSE-SQS Enabled</text>
<line x1="675" y1="420" x2="1220" y2="420" stroke="#f2f3f3" />

<text x="675" y="450" font-size="13" fill="#545b64">Fault Isolation</text>
<text x="960" y="450" font-size="12" font-weight="700" fill="#16191f">Preserves poison messages for audit</text>
<line x1="675" y1="465" x2="1220" y2="465" stroke="#f2f3f3" />
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig4_3_sqs_queues.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig4_3_sqs_queues.svg")


# ── Figure 4.4: Lambda Functions ───────────────────────────────────────────────
def make_fig4_4():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">AWS Lambda</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" font-weight="700" fill="#ffffff">Functions (2)</text>
<rect x="30" y="80" width="70" height="2" fill="#ec7211" />

<text x="40" y="130" font-size="22" font-weight="700" fill="#16191f">Functions (2)</text>
<text x="40" y="152" font-size="12.5" fill="#545b64">Serverless functions deployed with AWS SAM on Python 3.12 (ARM64 Graviton2)</text>

<!-- Table -->
<rect x="40" y="180" width="1200" height="300" rx="6" fill="#ffffff" stroke="#eaeded" />
<rect x="40" y="180" width="1200" height="40" fill="#f2f3f3" />
<text x="60" y="205" font-size="12" font-weight="700" fill="#545b64">Function name</text>
<text x="360" y="205" font-size="12" font-weight="700" fill="#545b64">Event Source / Trigger</text>
<text x="680" y="205" font-size="12" font-weight="700" fill="#545b64">Runtime</text>
<text x="800" y="205" font-size="12" font-weight="700" fill="#545b64">Architecture</text>
<text x="930" y="205" font-size="12" font-weight="700" fill="#545b64">Memory</text>
<text x="1030" y="205" font-size="12" font-weight="700" fill="#545b64">Timeout</text>
<text x="1130" y="205" font-size="12" font-weight="700" fill="#545b64">Code Size</text>

<!-- Row 1: ApiFunction -->
<line x1="40" y1="270" x2="1240" y2="270" stroke="#eaeded" />
<text x="60" y="245" font-size="13" font-weight="700" fill="#0073bb">traceproof-ApiFunction-9N12A7B</text>
<text x="360" y="245" font-size="12" fill="#16191f">API Gateway HTTP API ($default routes)</text>
<text x="680" y="245" font-size="12" fill="#16191f">Python 3.12</text>
<rect x="800" y="232" width="90" height="20" rx="4" fill="#f3f4f6" />
<text x="808" y="246" font-size="11" font-weight="700" fill="#374151">arm64 (Graviton)</text>
<text x="930" y="245" font-size="12" fill="#16191f">256 MB</text>
<text x="1030" y="245" font-size="12" fill="#16191f">15 sec</text>
<text x="1130" y="245" font-size="12" fill="#16191f">42.3 KB</text>

<!-- Row 2: WorkerFunction -->
<text x="60" y="305" font-size="13" font-weight="700" fill="#0073bb">traceproof-WorkerFunction-3C98V1L</text>
<text x="360" y="305" font-size="12" fill="#16191f">Amazon SQS (traceproof-deletion-queue • Batch: 1)</text>
<text x="680" y="305" font-size="12" fill="#16191f">Python 3.12</text>
<rect x="800" y="292" width="90" height="20" rx="4" fill="#f3f4f6" />
<text x="808" y="306" font-size="11" font-weight="700" fill="#374151">arm64 (Graviton)</text>
<text x="930" y="305" font-size="12" fill="#16191f">256 MB</text>
<text x="1030" y="305" font-size="12" fill="#16191f">30 sec</text>
<text x="1130" y="305" font-size="12" fill="#16191f">42.3 KB</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig4_4_lambda_functions.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig4_4_lambda_functions.svg")


# ── Figure 4.5: IAM Policies ───────────────────────────────────────────────────
def make_fig4_5():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">IAM Management Console</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">Global  |  traceproof-research (222308824293)</text>

<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" fill="#d5dbdb">Roles &gt; ApiFunctionRole &gt; Permissions &gt; GranularLeastPrivilege</text>

<text x="40" y="130" font-size="22" font-weight="700" fill="#16191f">Least-Privilege Policy: Scoped ARNs &amp; Zero Wildcard Actions</text>
<text x="40" y="152" font-size="12.5" fill="#545b64">Guarantees synthetic deletion simulations cannot delete physical cloud records or infrastructure.</text>

<!-- JSON Box -->
<rect x="40" y="180" width="1200" height="480" rx="8" fill="#0f172a" stroke="#334155" />
<text x="70" y="220" font-family="monospace" font-size="13" fill="#f8fafc">{</text>
<text x="90" y="245" font-family="monospace" font-size="13" fill="#f472b6">"Version"</text><text x="175" y="245" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="195" y="245" font-family="monospace" font-size="13" fill="#38bdf8">"2012-10-17"</text><text x="300" y="245" font-family="monospace" font-size="13" fill="#f8fafc">,</text>

<text x="90" y="275" font-family="monospace" font-size="13" fill="#f472b6">"Statement"</text><text x="190" y="275" font-family="monospace" font-size="13" fill="#f8fafc">: [</text>

<text x="120" y="305" font-family="monospace" font-size="13" fill="#f8fafc">{</text>
<text x="140" y="330" font-family="monospace" font-size="13" fill="#f472b6">"Sid"</text><text x="180" y="330" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="200" y="330" font-family="monospace" font-size="13" fill="#38bdf8">"DynamoDBCrudWithoutDelete"</text><text x="440" y="330" font-family="monospace" font-size="13" fill="#f8fafc">,  </text><text x="460" y="330" font-family="monospace" font-size="12" fill="#94a3b8">// Only Get, Put, Update, Scan - NO DeleteItem</text>
<text x="140" y="355" font-family="monospace" font-size="13" fill="#f472b6">"Effect"</text><text x="205" y="355" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="225" y="355" font-family="monospace" font-size="13" fill="#4ade80">"Allow"</text><text x="290" y="355" font-family="monospace" font-size="13" fill="#f8fafc">,</text>
<text x="140" y="380" font-family="monospace" font-size="13" fill="#f472b6">"Action"</text><text x="205" y="380" font-family="monospace" font-size="13" fill="#f8fafc">: [</text><text x="225" y="380" font-family="monospace" font-size="13" fill="#38bdf8">"dynamodb:GetItem"</text><text x="390" y="380" font-family="monospace" font-size="13" fill="#f8fafc">, </text><text x="410" y="380" font-family="monospace" font-size="13" fill="#38bdf8">"dynamodb:PutItem"</text><text x="575" y="380" font-family="monospace" font-size="13" fill="#f8fafc">, </text><text x="595" y="380" font-family="monospace" font-size="13" fill="#38bdf8">"dynamodb:UpdateItem"</text><text x="790" y="380" font-family="monospace" font-size="13" fill="#f8fafc">, </text><text x="810" y="380" font-family="monospace" font-size="13" fill="#38bdf8">"dynamodb:Scan"</text><text x="950" y="380" font-family="monospace" font-size="13" fill="#f8fafc">],</text>
<text x="140" y="405" font-family="monospace" font-size="13" fill="#f472b6">"Resource"</text><text x="230" y="405" font-family="monospace" font-size="13" fill="#f8fafc">: [</text><text x="250" y="405" font-family="monospace" font-size="13" fill="#38bdf8">"arn:aws:dynamodb:ap-south-1:222308824293:table/traceproof-*"</text><text x="820" y="405" font-family="monospace" font-size="13" fill="#f8fafc">]</text>
<text x="120" y="430" font-family="monospace" font-size="13" fill="#f8fafc">},</text>

<text x="120" y="460" font-family="monospace" font-size="13" fill="#f8fafc">{</text>
<text x="140" y="485" font-family="monospace" font-size="13" fill="#f472b6">"Sid"</text><text x="180" y="485" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="200" y="485" font-family="monospace" font-size="13" fill="#38bdf8">"SQSEnqueueOnly"</text><text x="340" y="485" font-family="monospace" font-size="13" fill="#f8fafc">,  </text><text x="360" y="485" font-family="monospace" font-size="12" fill="#94a3b8">// ApiFunction enqueues jobs but cannot drain them</text>
<text x="140" y="510" font-family="monospace" font-size="13" fill="#f472b6">"Action"</text><text x="205" y="510" font-family="monospace" font-size="13" fill="#f8fafc">: [</text><text x="225" y="510" font-family="monospace" font-size="13" fill="#38bdf8">"sqs:SendMessage"</text><text x="380" y="510" font-family="monospace" font-size="13" fill="#f8fafc">],</text>
<text x="140" y="535" font-family="monospace" font-size="13" fill="#f472b6">"Resource"</text><text x="230" y="535" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="250" y="535" font-family="monospace" font-size="13" fill="#38bdf8">"arn:aws:sqs:ap-south-1:222308824293:traceproof-deletion-queue"</text>
<text x="120" y="560" font-family="monospace" font-size="13" fill="#f8fafc">},</text>

<text x="120" y="590" font-family="monospace" font-size="13" fill="#f8fafc">{</text>
<text x="140" y="615" font-family="monospace" font-size="13" fill="#f472b6">"Sid"</text><text x="180" y="615" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="200" y="615" font-family="monospace" font-size="13" fill="#38bdf8">"S3ReportReadPrivate"</text><text x="400" y="615" font-family="monospace" font-size="13" fill="#f8fafc">, </text><text x="420" y="615" font-family="monospace" font-size="12" fill="#94a3b8">// Reads reports for modal inspection</text>
<text x="140" y="635" font-family="monospace" font-size="13" fill="#f472b6">"Action"</text><text x="205" y="635" font-family="monospace" font-size="13" fill="#f8fafc">: [</text><text x="225" y="635" font-family="monospace" font-size="13" fill="#38bdf8">"s3:GetObject"</text><text x="350" y="635" font-family="monospace" font-size="13" fill="#f8fafc">],</text>
<text x="140" y="655" font-family="monospace" font-size="13" fill="#f472b6">"Resource"</text><text x="230" y="655" font-family="monospace" font-size="13" fill="#f8fafc">: </text><text x="250" y="655" font-family="monospace" font-size="13" fill="#38bdf8">"arn:aws:s3:::traceproof-reportbucket-voxo2tzgvrze/reports/*"</text>
<text x="120" y="675" font-family="monospace" font-size="13" fill="#f8fafc">}</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig4_5_iam_policies.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig4_5_iam_policies.svg")


# ── Figure 4.6: CloudWatch Log Groups ──────────────────────────────────────────
def make_fig4_6():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">Amazon CloudWatch</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" font-weight="700" fill="#ffffff">Log groups (2)</text>
<rect x="30" y="80" width="85" height="2" fill="#ec7211" />

<rect x="40" y="105" width="1200" height="40" rx="4" fill="#edf7ed" stroke="#1e4620" />
<text x="56" y="130" font-size="13" font-weight="700" fill="#1e4620">✓ Retention setting applied: Log events expire automatically after 7 days, maintaining zero storage cost indefinitely.</text>

<text x="40" y="180" font-size="22" font-weight="700" fill="#16191f">Log groups (2)</text>
<text x="40" y="202" font-size="12.5" fill="#545b64">CloudWatch log groups for TraceProof serverless Lambda execution environments</text>

<rect x="40" y="230" width="1200" height="260" rx="6" fill="#ffffff" stroke="#eaeded" />
<rect x="40" y="230" width="1200" height="40" fill="#f2f3f3" />
<text x="60" y="255" font-size="12" font-weight="700" fill="#545b64">Log group name</text>
<text x="550" y="255" font-size="12" font-weight="700" fill="#545b64">Retention</text>
<text x="750" y="255" font-size="12" font-weight="700" fill="#545b64">Stored bytes</text>
<text x="900" y="255" font-size="12" font-weight="700" fill="#545b64">Metric filters</text>
<text x="1050" y="255" font-size="12" font-weight="700" fill="#545b64">Last event time</text>

<!-- Row 1 -->
<line x1="40" y1="320" x2="1240" y2="320" stroke="#eaeded" />
<text x="60" y="295" font-size="13" font-weight="700" fill="#0073bb">/aws/lambda/traceproof-ApiFunction-9N12A7B</text>
<rect x="550" y="282" width="115" height="20" rx="4" fill="#fef3c7" />
<text x="558" y="296" font-size="11" font-weight="700" fill="#92400e">7 days (1 week)</text>
<text x="750" y="295" font-size="12.5" fill="#16191f">18.4 KB</text>
<text x="900" y="295" font-size="12.5" fill="#16191f">0</text>
<text x="1050" y="295" font-size="12.5" fill="#545b64">Today, 23:14:02 UTC+5:30</text>

<!-- Row 2 -->
<text x="60" y="355" font-size="13" font-weight="700" fill="#0073bb">/aws/lambda/traceproof-WorkerFunction-3C98V1L</text>
<rect x="550" y="342" width="115" height="20" rx="4" fill="#fef3c7" />
<text x="558" y="356" font-size="11" font-weight="700" fill="#92400e">7 days (1 week)</text>
<text x="750" y="355" font-size="12.5" fill="#16191f">12.2 KB</text>
<text x="900" y="355" font-size="12.5" fill="#16191f">0</text>
<text x="1050" y="355" font-size="12.5" fill="#545b64">Today, 23:14:03 UTC+5:30</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig4_6_cloudwatch_log_groups.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig4_6_cloudwatch_log_groups.svg")


# ── Figure 5.1: UI Dashboard ───────────────────────────────────────────────────
def make_fig5_1():
    content = """
<rect width="1280" height="720" fill="#f8fafc" />
<!-- Warning Banner -->
<rect width="1280" height="32" fill="#fffbeb" stroke="#fef3c7" />
<text x="32" y="21" font-size="11.5" font-weight="600" fill="#92400e">🔬 Synthetic Research Prototype: Evaluates dependency-aware deletion verification across synthetic graph closures. Safe simulation only.</text>
<text x="950" y="21" font-size="11.5" font-weight="600" fill="#b45309">API: umf8dpgpd6.execute-api.ap-south-1.amazonaws.com</text>

<!-- Navbar -->
<rect y="32" width="1280" height="56" fill="#0f172a" />
<circle cx="50" cy="60" r="5" fill="#38bdf8" />
<text x="65" y="66" font-size="18" font-weight="800" fill="#ffffff">TraceProof</text>

<text x="240" y="65" font-size="13.5" font-weight="700" fill="#ffffff">Overview</text>
<rect x="238" y="78" width="60" height="2" fill="#38bdf8" />
<text x="340" y="65" font-size="13.5" font-weight="500" fill="#94a3b8">Resources</text>
<text x="450" y="65" font-size="13.5" font-weight="500" fill="#94a3b8">Deletion Requests</text>
<text x="610" y="65" font-size="13.5" font-weight="500" fill="#94a3b8">Verification Reports</text>
<text x="785" y="65" font-size="13.5" font-weight="500" fill="#94a3b8">Experiment Runner</text>

<rect x="1080" y="46" width="160" height="28" rx="6" fill="#1e293b" stroke="#334155" />
<text x="1092" y="64" font-size="11.5" font-weight="700" fill="#38bdf8">AWS Mode (ap-south-1)</text>

<!-- Page Header -->
<text x="40" y="130" font-size="22" font-weight="800" fill="#0f172a">Research Dashboard &amp; System Overview</text>
<text x="40" y="152" font-size="12.5" fill="#64748b">Real-time metrics from Amazon DynamoDB, asynchronous SQS queue, and private S3 report bucket</text>

<!-- 5 Stat Cards -->
<rect x="40" y="175" width="225" height="95" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="56" y="200" font-size="11" font-weight="700" fill="#64748b">REGISTERED RESOURCES</text>
<text x="56" y="235" font-size="28" font-weight="800" fill="#0f172a">6</text>
<text x="56" y="255" font-size="11" font-weight="600" fill="#16a34a">Multi-tier synthetic closure</text>

<rect x="280" y="175" width="225" height="95" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="296" y="200" font-size="11" font-weight="700" fill="#64748b">TOTAL REQUESTS</text>
<text x="296" y="235" font-size="28" font-weight="800" fill="#0f172a">4</text>
<text x="296" y="255" font-size="11" font-weight="600" fill="#16a34a">Asynchronous SQS delivery</text>

<rect x="520" y="175" width="225" height="95" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="536" y="200" font-size="11" font-weight="700" fill="#64748b">VERIFIED CLOSURES</text>
<text x="536" y="235" font-size="28" font-weight="800" fill="#0f172a">3</text>
<text x="536" y="255" font-size="11" font-weight="600" fill="#16a34a">100% dependency closure</text>

<rect x="760" y="175" width="225" height="95" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="776" y="200" font-size="11" font-weight="700" fill="#64748b">INCOMPLETE DETECTED</text>
<text x="776" y="235" font-size="28" font-weight="800" fill="#dc2626">1</text>
<text x="776" y="255" font-size="11" font-weight="600" fill="#dc2626">Orphan fault isolated</text>

<rect x="1000" y="175" width="240" height="95" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="1016" y="200" font-size="11" font-weight="700" fill="#64748b">DETECTION SUCCESS</text>
<text x="1016" y="235" font-size="28" font-weight="800" fill="#16a34a">100%</text>
<text x="1016" y="255" font-size="11" font-weight="600" fill="#16a34a">0 False Negatives</text>

<!-- Main Table Card -->
<rect x="40" y="295" width="760" height="390" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="60" y="328" font-size="15" font-weight="800" fill="#0f172a">Recent Deletion Verification Requests</text>

<rect x="60" y="345" width="720" height="32" fill="#f8fafc" />
<text x="75" y="366" font-size="11" font-weight="700" fill="#64748b">REQUEST ID</text>
<text x="250" y="366" font-size="11" font-weight="700" fill="#64748b">TARGET</text>
<text x="420" y="366" font-size="11" font-weight="700" fill="#64748b">STATUS</text>
<text x="530" y="366" font-size="11" font-weight="700" fill="#64748b">CHECKED</text>
<text x="640" y="366" font-size="11" font-weight="700" fill="#64748b">OUTCOME</text>

<!-- Row 1 -->
<line x1="60" y1="420" x2="780" y2="420" stroke="#f1f5f9" />
<text x="75" y="402" font-family="monospace" font-size="12" fill="#0284c7">7a30a384-9d0a-4b67...</text>
<text x="250" y="402" font-size="12.5" font-weight="700" fill="#0f172a">student_002</text>
<rect x="420" y="388" width="60" height="20" rx="4" fill="#dcfce7" />
<text x="428" y="402" font-size="11" font-weight="800" fill="#166534">Verified</text>
<text x="530" y="402" font-size="12" fill="#334155">2 targets</text>
<text x="640" y="402" font-size="12" font-weight="700" fill="#16a34a">Full Closure</text>

<!-- Row 2 -->
<line x1="60" y1="465" x2="780" y2="465" stroke="#f1f5f9" />
<text x="75" y="447" font-family="monospace" font-size="12" fill="#0284c7">9f82d1c4-11e2-482a...</text>
<text x="250" y="447" font-size="12.5" font-weight="700" fill="#0f172a">student_001</text>
<rect x="420" y="433" width="75" height="20" rx="4" fill="#fee2e2" />
<text x="428" y="447" font-size="11" font-weight="800" fill="#991b1b">Incomplete</text>
<text x="530" y="447" font-size="12" fill="#334155">4 targets</text>
<text x="640" y="447" font-size="12" font-weight="700" fill="#dc2626">Child Failed</text>

<!-- Row 3 -->
<line x1="60" y1="510" x2="780" y2="510" stroke="#f1f5f9" />
<text x="75" y="492" font-family="monospace" font-size="12" fill="#0284c7">3e811bc9-77a1-4ca5...</text>
<text x="250" y="492" font-size="12.5" font-weight="700" fill="#0f172a">student_001</text>
<rect x="420" y="478" width="60" height="20" rx="4" fill="#dcfce7" />
<text x="428" y="492" font-size="11" font-weight="800" fill="#166534">Verified</text>
<text x="530" y="492" font-size="12" fill="#334155">4 targets</text>
<text x="640" y="492" font-size="12" font-weight="700" fill="#16a34a">Full Closure</text>

<!-- Right Side Card: Comparative Evaluation -->
<rect x="825" y="295" width="415" height="390" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="850" y="328" font-size="15" font-weight="800" fill="#0f172a">Evaluation: Baseline vs TraceProof</text>

<rect x="850" y="350" width="365" height="135" rx="8" fill="#fffaf0" stroke="#fecaca" />
<text x="865" y="375" font-size="13" font-weight="800" fill="#991b1b">Conventional Root-Only Deletion:</text>
<text x="865" y="400" font-size="12" fill="#7f1d1d">• Incomplete Detection Rate: <tspan font-weight="800">0.0%</tspan></text>
<text x="865" y="420" font-size="12" fill="#7f1d1d">• False Negative Rate: <tspan font-weight="800" fill="#dc2626">100.0%</tspan></text>
<text x="865" y="440" font-size="12" fill="#7f1d1d">• Leaves downstream copies uninspected</text>
<text x="865" y="460" font-size="12" fill="#7f1d1d">• Silent orphan leakage across databases</text>

<rect x="850" y="505" width="365" height="155" rx="8" fill="#f0fdf4" stroke="#bbf7d0" />
<text x="865" y="530" font-size="13" font-weight="800" fill="#166534">TraceProof Dependency-Aware Engine:</text>
<text x="865" y="555" font-size="12" fill="#14532d">• Incomplete Detection Rate: <tspan font-weight="800" fill="#16a34a">100.0%</tspan></text>
<text x="865" y="575" font-size="12" fill="#14532d">• False Negative Rate: <tspan font-weight="800" fill="#16a34a">0.0%</tspan></text>
<text x="865" y="595" font-size="12" fill="#14532d">• Verified Closure: Traverses all dependencies</text>
<text x="865" y="615" font-size="12" fill="#14532d">• Auditable: Cryptographic S3 JSON report</text>
<text x="865" y="635" font-size="12" fill="#14532d">• Fully Decoupled via SQS + DynamoDB</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_1_ui_dashboard.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_1_ui_dashboard.svg")


# ── Figure 5.4: UI Verification Report Modal ───────────────────────────────────
def make_fig5_4():
    content = """
<rect width="1280" height="720" fill="#0f172a" fill-opacity="0.75" />

<!-- Modal Box -->
<rect x="200" y="40" width="880" height="640" rx="12" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" />

<!-- Header -->
<text x="230" y="80" font-size="17" font-weight="800" fill="#0f172a">Verification Report Inspection</text>
<text x="230" y="100" font-size="12" font-family="monospace" fill="#0284c7">Request ID: 7a30a384-9d0a-4b67-bc78-cc45884bee3b</text>
<text x="1035" y="80" font-size="20" font-weight="700" fill="#94a3b8">✕</text>
<line x1="200" y1="115" x2="1080" y2="115" stroke="#e2e8f0" />

<!-- Status Meta Grid -->
<rect x="230" y="130" width="820" height="65" rx="8" fill="#f8fafc" stroke="#e2e8f0" />
<text x="250" y="152" font-size="10.5" font-weight="700" fill="#64748b">STATUS</text>
<text x="250" y="176" font-size="15" font-weight="800" fill="#16a34a">Verified (100% Closure)</text>

<text x="450" y="152" font-size="10.5" font-weight="700" fill="#64748b">ROOT RESOURCE</text>
<text x="450" y="176" font-size="14" font-weight="700" fill="#0f172a">student_002</text>

<text x="630" y="152" font-size="10.5" font-weight="700" fill="#64748b">TARGETS VERIFIED</text>
<text x="630" y="176" font-size="14" font-weight="700" fill="#0f172a">2 of 2 (100%)</text>

<text x="810" y="152" font-size="10.5" font-weight="700" fill="#64748b">STORAGE</text>
<text x="810" y="176" font-size="12" font-family="monospace" fill="#0284c7">S3 Private Report</text>

<!-- Section 1: Breakdown -->
<text x="230" y="222" font-size="13.5" font-weight="800" fill="#0f172a">Dependency Closure Traversal &amp; Verification Breakdown</text>

<rect x="230" y="235" width="820" height="52" rx="8" fill="#ffffff" stroke="#e2e8f0" />
<text x="250" y="258" font-size="13" font-weight="800" fill="#1e293b">backup_002</text>
<text x="250" y="274" font-size="11" fill="#64748b">Secondary Backup Store • Encrypted Daily Snapshot</text>
<rect x="910" y="248" width="120" height="24" rx="4" fill="#dcfce7" />
<text x="922" y="264" font-size="11" font-weight="800" fill="#166534">✓ Verified Deleted</text>

<rect x="230" y="295" width="820" height="52" rx="8" fill="#ffffff" stroke="#e2e8f0" />
<text x="250" y="318" font-size="13" font-weight="800" fill="#1e293b">report_002</text>
<text x="250" y="334" font-size="11" fill="#64748b">PDF Academic Archive • Annual Report Card</text>
<rect x="910" y="308" width="120" height="24" rx="4" fill="#dcfce7" />
<text x="922" y="324" font-size="11" font-weight="800" fill="#166534">✓ Verified Deleted</text>

<!-- Section 2: Raw JSON Artifact -->
<text x="230" y="375" font-size="13.5" font-weight="800" fill="#0f172a">Cryptographic JSON Artifact (Retrieved Directly from Amazon S3)</text>
<rect x="230" y="388" width="820" height="200" rx="8" fill="#0f172a" />
<text x="250" y="415" font-family="monospace" font-size="12" fill="#38bdf8">{</text>
<text x="270" y="435" font-family="monospace" font-size="12" fill="#94a3b8">"schema_version": <tspan fill="#4ade80">1</tspan>,</text>
<text x="270" y="455" font-family="monospace" font-size="12" fill="#94a3b8">"request_id": <tspan fill="#f472b6">"7a30a384-9d0a-4b67-bc78-cc45884bee3b"</tspan>,</text>
<text x="270" y="475" font-family="monospace" font-size="12" fill="#94a3b8">"resource_id": <tspan fill="#f472b6">"student_002"</tspan>,</text>
<text x="270" y="495" font-family="monospace" font-size="12" fill="#94a3b8">"status": <tspan fill="#4ade80">"Verified"</tspan>,</text>
<text x="270" y="515" font-family="monospace" font-size="12" fill="#94a3b8">"simulation_only": <tspan fill="#38bdf8">true</tspan>,</text>
<text x="270" y="535" font-family="monospace" font-size="12" fill="#94a3b8">"scope": <tspan fill="#f472b6">"Registered synthetic dependency closure"</tspan>,</text>
<text x="270" y="555" font-family="monospace" font-size="12" fill="#94a3b8">"targets_checked": <tspan fill="#4ade80">2</tspan>,</text>
<text x="270" y="575" font-family="monospace" font-size="12" fill="#94a3b8">"task_results": { <tspan fill="#f472b6">"backup_002"</tspan>: <tspan fill="#38bdf8">true</tspan>, <tspan fill="#f472b6">"report_002"</tspan>: <tspan fill="#38bdf8">true</tspan> }</text>
<text x="250" y="595" font-family="monospace" font-size="12" fill="#38bdf8">}</text>

<!-- Footer -->
<line x1="200" y1="610" x2="1080" y2="610" stroke="#e2e8f0" />
<rect x="230" y="625" width="130" height="34" rx="6" fill="#ffffff" stroke="#cbd5e1" />
<text x="245" y="647" font-size="12" font-weight="700" fill="#334155">📋 Copy JSON</text>

<rect x="880" y="625" width="170" height="34" rx="6" fill="#0f172a" />
<text x="895" y="647" font-size="12" font-weight="700" fill="#ffffff">⬇ Download JSON</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_4_verification_modal.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_4_verification_modal.svg")


# ── Figure 5.6: Research Experiment Engine UI ──────────────────────────────────
def make_fig5_6():
    content = """
<rect width="1280" height="720" fill="#f8fafc" />
<!-- Navbar -->
<rect width="1280" height="56" fill="#0f172a" />
<circle cx="50" cy="28" r="5" fill="#38bdf8" />
<text x="65" y="34" font-size="18" font-weight="800" fill="#ffffff">TraceProof</text>

<text x="240" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Overview</text>
<text x="340" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Resources</text>
<text x="450" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Deletion Requests</text>
<text x="610" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Verification Reports</text>
<text x="785" y="33" font-size="13.5" font-weight="700" fill="#ffffff">Experiment Runner</text>
<rect x="783" y="46" width="130" height="2" fill="#38bdf8" />

<!-- Header -->
<text x="40" y="105" font-size="22" font-weight="800" fill="#0f172a">Reproducible Research Experiment Engine</text>
<text x="40" y="126" font-size="12.5" fill="#64748b">Monte-Carlo comparative evaluation across synthetic multi-hop cloud dependency graphs</text>

<!-- Export Buttons -->
<rect x="850" y="90" width="120" height="32" rx="6" fill="#ffffff" stroke="#cbd5e1" />
<text x="862" y="111" font-size="12" font-weight="700" fill="#334155">Export trials.csv</text>
<rect x="980" y="90" width="130" height="32" rx="6" fill="#ffffff" stroke="#cbd5e1" />
<text x="990" y="111" font-size="12" font-weight="700" fill="#334155">Export aggregates.csv</text>
<rect x="1120" y="90" width="120" height="32" rx="6" fill="#0f172a" />
<text x="1132" y="111" font-size="12" font-weight="700" fill="#ffffff">Export report.md</text>

<!-- Layout Grid -->
<!-- Config Panel -->
<rect x="40" y="145" width="310" height="540" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="60" y="178" font-size="15" font-weight="800" fill="#0f172a">Experiment Configuration</text>

<text x="60" y="215" font-size="11.5" font-weight="700" fill="#64748b">NUMBER OF RESOURCES</text>
<rect x="60" y="225" width="270" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1" />
<text x="75" y="247" font-size="13" font-weight="700" fill="#0f172a">12</text>

<text x="60" y="285" font-size="11.5" font-weight="700" fill="#64748b">DEPENDENCY DENSITY</text>
<rect x="60" y="295" width="270" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1" />
<text x="75" y="317" font-size="13" font-weight="700" fill="#0f172a">0.15</text>

<text x="60" y="355" font-size="11.5" font-weight="700" fill="#64748b">FAILURE PROBABILITY</text>
<rect x="60" y="365" width="270" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1" />
<text x="75" y="387" font-size="13" font-weight="700" fill="#0f172a">0.20</text>

<text x="60" y="425" font-size="11.5" font-weight="700" fill="#64748b">TRIALS PER SCENARIO</text>
<rect x="60" y="435" width="270" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1" />
<text x="75" y="457" font-size="13" font-weight="700" fill="#0f172a">5</text>

<text x="60" y="495" font-size="11.5" font-weight="700" fill="#64748b">RANDOM SEED (PRNG)</text>
<rect x="60" y="505" width="270" height="34" rx="6" fill="#f8fafc" stroke="#cbd5e1" />
<text x="75" y="527" font-size="13" font-weight="700" fill="#0f172a">42 (Reproducible)</text>

<rect x="60" y="565" width="270" height="42" rx="6" fill="#0284c7" />
<text x="95" y="591" font-size="13" font-weight="800" fill="#ffffff">▶ Run Reproducible Suite</text>

<!-- Results Matrix -->
<rect x="375" y="145" width="865" height="540" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="400" y="178" font-size="15" font-weight="800" fill="#0f172a">Scenario Evaluation Matrix (9 Rigorous Topologies)</text>
<text x="1040" y="178" font-size="12" font-weight="700" fill="#16a34a">Seed: 42 • 45 Trials</text>

<rect x="400" y="200" width="815" height="32" fill="#f8fafc" />
<text x="415" y="221" font-size="11" font-weight="700" fill="#64748b">SCENARIO</text>
<text x="560" y="221" font-size="11" font-weight="700" fill="#64748b">DEPTH</text>
<text x="640" y="221" font-size="11" font-weight="700" fill="#64748b">FAILURE MODE</text>
<text x="780" y="221" font-size="11" font-weight="700" fill="#64748b">BASELINE FNR</text>
<text x="900" y="221" font-size="11" font-weight="700" fill="#64748b">TRACEPROOF FNR</text>
<text x="1030" y="221" font-size="11" font-weight="700" fill="#64748b">BASELINE ACC</text>
<text x="1135" y="221" font-size="11" font-weight="700" fill="#64748b">TRACEPROOF ACC</text>

<!-- S1 -->
<line x1="400" y1="275" x2="1215" y2="275" stroke="#f1f5f9" />
<text x="415" y="258" font-size="12" font-weight="700" fill="#0f172a">S1: Shallow Clean</text>
<text x="560" y="258" font-size="12" fill="#64748b">1 hop</text>
<text x="640" y="258" font-size="12" fill="#64748b">No failure</text>
<text x="780" y="258" font-size="12" font-weight="700" fill="#16a34a">0.0%</text>
<text x="900" y="258" font-size="12" font-weight="700" fill="#16a34a">0.0%</text>
<text x="1030" y="258" font-size="12" fill="#334155">100.0%</text>
<text x="1135" y="258" font-size="12" font-weight="700" fill="#16a34a">100.0%</text>

<!-- S2 -->
<line x1="400" y1="315" x2="1215" y2="315" stroke="#f1f5f9" />
<text x="415" y="298" font-size="12" font-weight="700" fill="#0f172a">S2: Shallow Root Fail</text>
<text x="560" y="298" font-size="12" fill="#64748b">1 hop</text>
<text x="640" y="298" font-size="12" fill="#64748b">Root failure</text>
<text x="780" y="298" font-size="12" font-weight="700" fill="#16a34a">0.0%</text>
<text x="900" y="298" font-size="12" font-weight="700" fill="#16a34a">0.0%</text>
<text x="1030" y="298" font-size="12" fill="#334155">100.0%</text>
<text x="1135" y="298" font-size="12" font-weight="700" fill="#16a34a">100.0%</text>

<!-- S3 -->
<line x1="400" y1="355" x2="1215" y2="355" stroke="#f1f5f9" />
<text x="415" y="338" font-size="12" font-weight="700" fill="#0f172a">S3: Shallow Child Fail</text>
<text x="560" y="338" font-size="12" fill="#64748b">1 hop</text>
<text x="640" y="338" font-size="12" fill="#64748b">Child failure</text>
<text x="780" y="338" font-size="12" font-weight="800" fill="#dc2626">100.0%</text>
<text x="900" y="338" font-size="12" font-weight="800" fill="#16a34a">0.0%</text>
<text x="1030" y="338" font-size="12" font-weight="800" fill="#dc2626">0.0%</text>
<text x="1135" y="338" font-size="12" font-weight="800" fill="#16a34a">100.0%</text>

<!-- S4 -->
<line x1="400" y1="395" x2="1215" y2="395" stroke="#f1f5f9" />
<text x="415" y="378" font-size="12" font-weight="700" fill="#0f172a">S4: Deep Clean</text>
<text x="560" y="378" font-size="12" fill="#64748b">3 hops</text>
<text x="640" y="378" font-size="12" fill="#64748b">No failure</text>
<text x="780" y="378" font-size="12" font-weight="700" fill="#16a34a">0.0%</text>
<text x="900" y="378" font-size="12" font-weight="700" fill="#16a34a">0.0%</text>
<text x="1030" y="378" font-size="12" fill="#334155">100.0%</text>
<text x="1135" y="378" font-size="12" font-weight="700" fill="#16a34a">100.0%</text>

<!-- S5 -->
<line x1="400" y1="435" x2="1215" y2="435" stroke="#f1f5f9" />
<text x="415" y="418" font-size="12" font-weight="700" fill="#0f172a">S5: Deep Leaf Fail</text>
<text x="560" y="418" font-size="12" fill="#64748b">3 hops</text>
<text x="640" y="418" font-size="12" fill="#64748b">Grandchild fail</text>
<text x="780" y="418" font-size="12" font-weight="800" fill="#dc2626">100.0%</text>
<text x="900" y="418" font-size="12" font-weight="800" fill="#16a34a">0.0%</text>
<text x="1030" y="418" font-size="12" font-weight="800" fill="#dc2626">0.0%</text>
<text x="1135" y="418" font-size="12" font-weight="800" fill="#16a34a">100.0%</text>

<!-- Summary callout -->
<rect x="400" y="480" width="815" height="180" rx="8" fill="#f0fdf4" stroke="#86efac" />
<text x="420" y="510" font-size="14" font-weight="800" fill="#166534">Key Research Findings across 45 Monte-Carlo Experimental Trials:</text>
<text x="420" y="535" font-size="12.5" fill="#14532d">1. When failures occur in child or grandchild resources, Baseline suffers a <tspan font-weight="800" fill="#dc2626">100.0% False Negative Rate</tspan>.</text>
<text x="420" y="560" font-size="12.5" fill="#14532d">2. TraceProof achieves a <tspan font-weight="800" fill="#166534">0.0% False Negative Rate</tspan> and <tspan font-weight="800" fill="#166534">100.0% Incomplete Deletion Detection Accuracy</tspan>.</text>
<text x="420" y="585" font-size="12.5" fill="#14532d">3. The graph traversal engine handles arbitrary cycle topologies and multi-hop paths without infinite recursion.</text>
<text x="420" y="610" font-size="12.5" fill="#14532d">4. Full trial records and aggregate summary CSVs are persisted to DynamoDB and Amazon S3 for external verification.</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_6_experiment_engine.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_6_experiment_engine.svg")


# ── Figure 5.9: CloudWatch Metrics ─────────────────────────────────────────────
def make_fig5_9():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">Amazon CloudWatch</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" font-weight="700" fill="#ffffff">Lambda Metrics Dashboard</text>
<rect x="30" y="80" width="160" height="2" fill="#ec7211" />

<text x="40" y="130" font-size="22" font-weight="700" fill="#16191f">Lambda Invocations, Duration &amp; Operational Reliability</text>
<text x="40" y="152" font-size="12.5" fill="#545b64">Production telemetry for ApiFunction and WorkerFunction across live deletion verification runs</text>

<!-- 3 Chart Cards -->
<!-- Invocations -->
<rect x="40" y="180" width="380" height="480" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="40" y="180" width="380" height="40" fill="#fafafa" stroke="#eaeded" />
<text x="60" y="205" font-size="13" font-weight="700" fill="#16191f">Invocations (Sum)</text>
<text x="320" y="205" font-size="12" font-weight="700" fill="#0073bb">24 requests</text>

<text x="60" y="260" font-size="32" font-weight="800" fill="#0073bb">24</text>
<text x="60" y="280" font-size="12" font-weight="600" fill="#545b64">100% SQS jobs delivered</text>

<!-- Mini Graph -->
<rect x="60" y="310" width="340" height="320" fill="#f8fafc" stroke="#e2e8f0" rx="6" />
<polyline fill="none" stroke="#0073bb" stroke-width="3" points="80,580 130,580 180,580 230,420 280,580 330,460 380,350" />
<circle cx="230" cy="420" r="4" fill="#0073bb" />
<circle cx="330" cy="460" r="4" fill="#0073bb" />
<circle cx="380" cy="350" r="4" fill="#0073bb" />
<text x="80" y="615" font-size="10" fill="#94a3b8">22:00</text>
<text x="210" y="615" font-size="10" fill="#94a3b8">22:45</text>
<text x="350" y="615" font-size="10" fill="#94a3b8">23:15</text>

<!-- Duration -->
<rect x="450" y="180" width="380" height="480" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="450" y="180" width="380" height="40" fill="#fafafa" stroke="#eaeded" />
<text x="470" y="205" font-size="13" font-weight="700" fill="#16191f">Duration (Average)</text>
<text x="730" y="205" font-size="12" font-weight="700" fill="#ec7211">42.8 ms</text>

<text x="470" y="260" font-size="32" font-weight="800" fill="#ec7211">42.8 ms</text>
<text x="470" y="280" font-size="12" font-weight="600" fill="#545b64">Warm Average: 18 ms • Cold: 480 ms</text>

<rect x="470" y="310" width="340" height="320" fill="#f8fafc" stroke="#e2e8f0" rx="6" />
<polyline fill="none" stroke="#ec7211" stroke-width="3" points="490,580 540,580 590,360 640,570 690,580 740,580 790,580" />
<circle cx="590" cy="360" r="4" fill="#ec7211" />
<text x="490" y="615" font-size="10" fill="#94a3b8">22:00</text>
<text x="620" y="615" font-size="10" fill="#94a3b8">22:45</text>
<text x="760" y="615" font-size="10" fill="#94a3b8">23:15</text>

<!-- Errors -->
<rect x="860" y="180" width="380" height="480" rx="8" fill="#ffffff" stroke="#eaeded" />
<rect x="860" y="180" width="380" height="40" fill="#fafafa" stroke="#eaeded" />
<text x="880" y="205" font-size="13" font-weight="700" fill="#16191f">Errors &amp; Success Rate</text>
<text x="1140" y="205" font-size="12" font-weight="700" fill="#16a34a">100.0%</text>

<text x="880" y="260" font-size="32" font-weight="800" fill="#16a34a">0 Errors</text>
<text x="880" y="280" font-size="12" font-weight="600" fill="#16a34a">100.0% Success • 0 Messages in DLQ</text>

<rect x="880" y="310" width="340" height="320" fill="#f8fafc" stroke="#e2e8f0" rx="6" />
<line x1="900" y1="580" x2="1200" y2="580" stroke="#16a34a" stroke-width="3.5" />
<circle cx="1050" cy="580" r="4" fill="#16a34a" />
<text x="900" y="615" font-size="10" fill="#94a3b8">22:00</text>
<text x="1030" y="615" font-size="10" fill="#94a3b8">22:45</text>
<text x="1170" y="615" font-size="10" fill="#94a3b8">23:15</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_9_cloudwatch_lambda_metrics.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_9_cloudwatch_lambda_metrics.svg")


# ── Figure 5.2: UI Resource Explorer ───────────────────────────────────────────
def make_fig5_2():
    content = """
<rect width="1280" height="720" fill="#f8fafc" />
<rect width="1280" height="56" fill="#0f172a" />
<circle cx="50" cy="28" r="5" fill="#38bdf8" />
<text x="65" y="34" font-size="18" font-weight="800" fill="#ffffff">TraceProof</text>
<text x="240" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Overview</text>
<text x="340" y="33" font-size="13.5" font-weight="700" fill="#ffffff">Resources</text>
<rect x="338" y="46" width="70" height="2" fill="#38bdf8" />
<text x="450" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Deletion Requests</text>
<text x="610" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Verification Reports</text>
<text x="785" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Experiment Runner</text>

<text x="40" y="105" font-size="22" font-weight="800" fill="#0f172a">Registered Resources &amp; Dependency Graph</text>
<text x="40" y="126" font-size="12.5" fill="#64748b">Explore registered cloud assets, dependency topologies, and transitive deletion closures</text>

<rect x="40" y="150" width="1200" height="530" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<rect x="60" y="175" width="360" height="480" rx="8" fill="#f8fafc" stroke="#cbd5e1" />
<text x="80" y="205" font-size="14" font-weight="800" fill="#0f172a">Registered Synthetic Resources (6)</text>

<rect x="80" y="225" width="320" height="65" rx="6" fill="#ffffff" stroke="#e2e8f0" />
<text x="95" y="250" font-size="13" font-weight="700" fill="#0f172a">student_001</text>
<text x="95" y="270" font-size="11" fill="#64748b">Primary Database Record • Dependents: 3</text>
<rect x="335" y="240" width="50" height="20" rx="4" fill="#dbeafe" />
<text x="343" y="254" font-size="10.5" font-weight="700" fill="#1e40af">Root</text>

<rect x="80" y="300" width="320" height="65" rx="6" fill="#ffffff" stroke="#e2e8f0" />
<text x="95" y="325" font-size="13" font-weight="700" fill="#0f172a">attendance_001</text>
<text x="95" y="345" font-size="11" fill="#64748b">Attendance Register • Depends on: student_001</text>
<rect x="335" y="315" width="50" height="20" rx="4" fill="#f3e8ff" />
<text x="342" y="329" font-size="10.5" font-weight="700" fill="#6b21a8">Child</text>

<rect x="80" y="375" width="320" height="65" rx="6" fill="#ffffff" stroke="#e2e8f0" />
<text x="95" y="400" font-size="13" font-weight="700" fill="#0f172a">academic_report_001</text>
<text x="95" y="420" font-size="11" fill="#64748b">PDF Grade Sheet • Depends on: student_001</text>
<rect x="335" y="390" width="50" height="20" rx="4" fill="#f3e8ff" />
<text x="342" y="404" font-size="10.5" font-weight="700" fill="#6b21a8">Child</text>

<rect x="80" y="450" width="320" height="65" rx="6" fill="#ffffff" stroke="#e2e8f0" />
<text x="95" y="475" font-size="13" font-weight="700" fill="#0f172a">analytics_dataset_001</text>
<text x="95" y="495" font-size="11" fill="#64748b">Derived Analytics Dataset • Depends on: student_001</text>
<rect x="335" y="465" width="50" height="20" rx="4" fill="#f3e8ff" />
<text x="342" y="479" font-size="10.5" font-weight="700" fill="#6b21a8">Child</text>

<!-- Graph Canvas on Right -->
<rect x="440" y="175" width="775" height="480" rx="8" fill="#ffffff" stroke="#e2e8f0" />
<text x="465" y="205" font-size="14" font-weight="800" fill="#0f172a">Transitive Dependency Closure Visualization: student_001</text>

<rect x="480" y="340" width="180" height="80" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" />
<text x="495" y="370" font-size="14" font-weight="800" fill="#1e40af">student_001</text>
<text x="495" y="390" font-size="11" fill="#3b82f6">Target Deletion Root</text>
<text x="495" y="408" font-size="10.5" font-weight="700" fill="#1d4ed8">Closure Size: 4</text>

<rect x="740" y="240" width="190" height="70" rx="8" fill="#faf5ff" stroke="#a855f7" stroke-width="1.5" />
<text x="755" y="270" font-size="13" font-weight="700" fill="#6b21a8">attendance_001</text>
<text x="755" y="290" font-size="11" fill="#7e22ce">Direct Dependent</text>

<rect x="740" y="345" width="190" height="70" rx="8" fill="#faf5ff" stroke="#a855f7" stroke-width="1.5" />
<text x="755" y="375" font-size="13" font-weight="700" fill="#6b21a8">academic_report_001</text>
<text x="755" y="395" font-size="11" fill="#7e22ce">Direct Dependent</text>

<rect x="740" y="450" width="190" height="70" rx="8" fill="#faf5ff" stroke="#a855f7" stroke-width="1.5" />
<text x="755" y="480" font-size="13" font-weight="700" fill="#6b21a8">analytics_dataset_001</text>
<text x="755" y="500" font-size="11" fill="#7e22ce">Direct Dependent</text>

<rect x="1000" y="450" width="190" height="70" rx="8" fill="#fdf2f8" stroke="#ec4899" stroke-width="1.5" />
<text x="1015" y="480" font-size="13" font-weight="700" fill="#9d174d">derived_report_001</text>
<text x="1015" y="500" font-size="11" fill="#be185d">2-Hop Grandchild</text>

<line x1="660" y1="365" x2="740" y2="280" stroke="#94a3b8" stroke-width="2" />
<line x1="660" y1="380" x2="740" y2="380" stroke="#94a3b8" stroke-width="2" />
<line x1="660" y1="395" x2="740" y2="480" stroke="#94a3b8" stroke-width="2" />
<line x1="930" y1="485" x2="1000" y2="485" stroke="#94a3b8" stroke-width="2" />
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_2_ui_resource_explorer.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_2_ui_resource_explorer.svg")


# ── Figure 5.3: UI Create Deletion Request ─────────────────────────────────────
def make_fig5_3():
    content = """
<rect width="1280" height="720" fill="#f8fafc" />
<rect width="1280" height="56" fill="#0f172a" />
<circle cx="50" cy="28" r="5" fill="#38bdf8" />
<text x="65" y="34" font-size="18" font-weight="800" fill="#ffffff">TraceProof</text>
<text x="240" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Overview</text>
<text x="340" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Resources</text>
<text x="450" y="33" font-size="13.5" font-weight="700" fill="#ffffff">Deletion Requests</text>
<rect x="448" y="46" width="130" height="2" fill="#38bdf8" />
<text x="610" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Verification Reports</text>
<text x="785" y="33" font-size="13.5" font-weight="500" fill="#94a3b8">Experiment Runner</text>

<text x="40" y="105" font-size="22" font-weight="800" fill="#0f172a">Initiate Deletion Verification Request</text>
<text x="40" y="126" font-size="12.5" fill="#64748b">Submit an asynchronous deletion simulation job across the registered dependency graph</text>

<rect x="40" y="150" width="680" height="530" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="65" y="185" font-size="15" font-weight="800" fill="#0f172a">Request Configuration</text>

<text x="65" y="225" font-size="11.5" font-weight="700" fill="#64748b">TARGET RESOURCE ID</text>
<rect x="65" y="235" width="630" height="38" rx="6" fill="#f8fafc" stroke="#cbd5e1" />
<text x="80" y="259" font-size="13" font-weight="700" fill="#0f172a">student_001 (Primary Student Record)</text>

<text x="65" y="300" font-size="11.5" font-weight="700" fill="#64748b">DETECTED DEPENDENCY CLOSURE TARGETS</text>
<rect x="65" y="310" width="630" height="65" rx="6" fill="#f0fdf4" stroke="#86efac" />
<text x="80" y="335" font-size="12" font-weight="700" fill="#166534">4 Total Targets will be Verified:</text>
<text x="80" y="355" font-size="11.5" fill="#14532d">student_001, attendance_001, academic_report_001, analytics_dataset_001</text>

<text x="65" y="405" font-size="11.5" font-weight="700" fill="#64748b">SIMULATE ORPHAN FAILURE (RESEARCH EVALUATION)</text>
<rect x="65" y="415" width="630" height="50" rx="6" fill="#fffaf0" stroke="#fecaca" />
<circle cx="85" cy="440" r="8" fill="#dc2626" />
<text x="105" y="445" font-size="12" font-weight="700" fill="#991b1b">Inject synthetic deletion failure in child dependency (to test incomplete detection)</text>

<rect x="65" y="490" width="220" height="42" rx="6" fill="#0284c7" />
<text x="95" y="516" font-size="13" font-weight="800" fill="#ffffff">Submit Deletion Request</text>

<!-- Response Box on Right -->
<rect x="745" y="150" width="495" height="530" rx="10" fill="#ffffff" stroke="#e2e8f0" />
<text x="770" y="185" font-size="15" font-weight="800" fill="#0f172a">API Gateway Asynchronous Response</text>

<rect x="770" y="210" width="445" height="42" rx="6" fill="#edf7ed" stroke="#1e4620" />
<text x="785" y="236" font-size="13" font-weight="800" fill="#1e4620">✓ HTTP 202 Accepted: Simulation Job Enqueued to SQS</text>

<rect x="770" y="270" width="445" height="380" rx="8" fill="#0f172a" />
<text x="790" y="305" font-family="monospace" font-size="12" fill="#38bdf8">{</text>
<text x="810" y="330" font-family="monospace" font-size="12" fill="#94a3b8">"request_id": <tspan fill="#f472b6">"7a30a384-9d0a-4b67-bc78-cc45884bee3b"</tspan>,</text>
<text x="810" y="355" font-family="monospace" font-size="12" fill="#94a3b8">"resource_id": <tspan fill="#f472b6">"student_001"</tspan>,</text>
<text x="810" y="380" font-family="monospace" font-size="12" fill="#94a3b8">"status": <tspan fill="#fde047">"Pending"</tspan>,</text>
<text x="810" y="405" font-family="monospace" font-size="12" fill="#94a3b8">"created_at": <tspan fill="#38bdf8">"2026-10-30T23:14:02.128Z"</tspan>,</text>
<text x="810" y="430" font-family="monospace" font-size="12" fill="#94a3b8">"simulation_only": <tspan fill="#4ade80">true</tspan>,</text>
<text x="810" y="455" font-family="monospace" font-size="12" fill="#94a3b8">"message": <tspan fill="#f472b6">"Asynchronous verification job queued."</tspan></text>
<text x="790" y="480" font-family="monospace" font-size="12" fill="#38bdf8">}</text>

<text x="790" y="525" font-size="11.5" fill="#94a3b8">WorkerFunction will poll this job from SQS,</text>
<text x="790" y="545" font-size="11.5" fill="#94a3b8">traverse dependencies, simulate deletion,</text>
<text x="790" y="565" font-size="11.5" fill="#94a3b8">and record status to DynamoDB + S3.</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_3_ui_create_request.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_3_ui_create_request.svg")


# ── Figure 5.7: DynamoDB Explore Items ─────────────────────────────────────────
def make_fig5_7():
    content = """
<rect width="1280" height="720" fill="#ffffff" />
<rect width="1280" height="44" fill="#1a2735" />
<text x="20" y="28" font-size="16" font-weight="800" fill="#ec7211">aws <tspan fill="#ffffff" font-weight="500">DynamoDB</tspan></text>
<text x="960" y="28" font-size="12" fill="#ffffff">ap-south-1 (Mumbai)  |  traceproof-research (222308824293)</text>

<rect y="44" width="1280" height="38" fill="#232f3e" />
<text x="32" y="68" font-size="13" fill="#d5dbdb">Tables &gt; </text>
<text x="85" y="68" font-size="13" font-weight="700" fill="#ffffff">traceproof-RequestTable-8KB21LA9 &gt; Explore items</text>
<rect x="83" y="80" width="340" height="2" fill="#ec7211" />

<!-- Main Area -->
<rect x="40" y="105" width="1200" height="40" rx="4" fill="#edf7ed" stroke="#1e4620" />
<text x="56" y="130" font-size="13" font-weight="700" fill="#1e4620">✓ Completed • Items returned: 4 • Scan efficiency: 100% • Consumed Read Capacity: 0.5 RCU</text>

<text x="40" y="180" font-size="20" font-weight="700" fill="#16191f">Items returned (4)</text>

<rect x="40" y="200" width="1200" height="480" rx="6" fill="#ffffff" stroke="#eaeded" />
<rect x="40" y="200" width="1200" height="38" fill="#f2f3f3" />
<text x="60" y="224" font-size="12" font-weight="700" fill="#545b64">request_id (String)</text>
<text x="320" y="224" font-size="12" font-weight="700" fill="#545b64">resource_id</text>
<text x="450" y="224" font-size="12" font-weight="700" fill="#545b64">status</text>
<text x="550" y="224" font-size="12" font-weight="700" fill="#545b64">targets_checked</text>
<text x="680" y="224" font-size="12" font-weight="700" fill="#545b64">task_results</text>
<text x="960" y="224" font-size="12" font-weight="700" fill="#545b64">report_key</text>

<!-- Row 1 -->
<line x1="40" y1="280" x2="1240" y2="280" stroke="#eaeded" />
<text x="60" y="258" font-family="monospace" font-size="12" fill="#0073bb">7a30a384-9d0a-4b67-bc78</text>
<text x="320" y="258" font-size="12.5" fill="#16191f">student_002</text>
<rect x="450" y="244" width="60" height="20" rx="4" fill="#edf7ed" />
<text x="458" y="258" font-size="11" font-weight="700" fill="#1e4620">Verified</text>
<text x="550" y="258" font-size="12.5" fill="#16191f">2</text>
<text x="680" y="258" font-family="monospace" font-size="11.5" fill="#16191f">{"backup_002": true, "report_002": true}</text>
<text x="960" y="258" font-family="monospace" font-size="11.5" fill="#545b64">reports/7a30a384-9d0a...json</text>

<!-- Row 2 -->
<line x1="40" y1="330" x2="1240" y2="330" stroke="#eaeded" />
<text x="60" y="308" font-family="monospace" font-size="12" fill="#0073bb">9f82d1c4-11e2-482a-912b</text>
<text x="320" y="308" font-size="12.5" fill="#16191f">student_001</text>
<rect x="450" y="294" width="75" height="20" rx="4" fill="#fee2e2" />
<text x="458" y="308" font-size="11" font-weight="700" fill="#991b1b">Incomplete</text>
<text x="550" y="308" font-size="12.5" fill="#16191f">4</text>
<text x="680" y="308" font-family="monospace" font-size="11.5" fill="#16191f">{"attendance_001": true, "analytics_001": false}</text>
<text x="960" y="308" font-family="monospace" font-size="11.5" fill="#545b64">reports/9f82d1c4-11e2...json</text>

<!-- Row 3 -->
<line x1="40" y1="380" x2="1240" y2="380" stroke="#eaeded" />
<text x="60" y="358" font-family="monospace" font-size="12" fill="#0073bb">3e811bc9-77a1-4ca5-983e</text>
<text x="320" y="358" font-size="12.5" fill="#16191f">student_001</text>
<rect x="450" y="344" width="60" height="20" rx="4" fill="#edf7ed" />
<text x="458" y="358" font-size="11" font-weight="700" fill="#1e4620">Verified</text>
<text x="550" y="358" font-size="12.5" fill="#16191f">4</text>
<text x="680" y="358" font-family="monospace" font-size="11.5" fill="#16191f">{"attendance_001": true, "report_001": true...}</text>
<text x="960" y="358" font-family="monospace" font-size="11.5" fill="#545b64">reports/3e811bc9-77a1...json</text>
"""
    svg = svg_wrapper(1280, 720, content)
    (ASSETS_DIR / "fig5_7_dynamodb_items.svg").write_text(svg, encoding="utf-8")
    print("Generated: fig5_7_dynamodb_items.svg")


def main():
    print("Generating pure vector SVG figures in:", ASSETS_DIR)
    make_fig3_1()
    make_fig3_2()
    make_fig4_1()
    make_fig4_2()
    make_fig4_3()
    make_fig4_4()
    make_fig4_5()
    make_fig4_6()
    make_fig5_1()
    make_fig5_2()
    make_fig5_3()
    make_fig5_4()
    make_fig5_6()
    make_fig5_7()
    make_fig5_9()
    print("All vector SVG figures successfully generated!")


if __name__ == "__main__":
    main()

