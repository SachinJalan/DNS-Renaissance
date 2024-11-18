# Evaluating DNS Protocol Implementation Inefficiencies in Resource-Constrained Environments

## Problem Statement

- DNS protocol unchanged since 1983
- Inefficient for resource-constrained devices (IoT, edge devices)
- Key overheads:
  - Latency in recursive/iterative queries
  - Poor scalability with high device density
  - Security vulnerabilities
  - Power consumption

## Objectives

1. Analyze DNS traffic patterns using sandboxed packet capture
2. Identify overhead and inefficiencies
3. Study optimization opportunities
4. Propose solutions with proof of concept

## Methodology

- Docker container for sandboxed environment
- Tools: dumpcap, wget, python-pcapng
- Analysis Parameters:
  - Total packets and bytes
  - DNS-specific packets and bytes
  - Time metrics (total, DNS, TTFB)
  - DNS cycles and energy
  - Domain statistics

## Key Findings

1. Resource Usage

   - 60% websites exceed 5% byte overhead for DNS
   - 40% exceed 5% time overhead
   - 35% exceed 5% packet overhead

2. DNS Resolution Patterns
   - Only A and AAAA records observed for top 1000 websites
   - 0.3% queries shifted to TCP (primarily AAAA records)
   - 5% requests benefited from name server delegation
3. Protocol Inefficiencies
   - 7 bytes of DNS header consistently unused
   - Multiple sequential queries where parallel possible
   - Redundant record requests

## Future Work

- Mobile/edge device analysis
- Multiple query optimization
- Protocol redesign opportunities
- Intelligent caching mechanisms

## Contact Information

[Authors and Institution details]
