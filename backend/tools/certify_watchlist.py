#!/usr/bin/env python
"""
CLI runner for Watchlist Engine Certification.
"""
import sys
import os
import asyncio
import json

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.watchlist_engine.certification.engine import CertificationEngine


async def main():
    print("=" * 60)
    print("WATCHLIST ENGINE CERTIFICATION".center(60))
    print("=" * 60)
    
    engine = CertificationEngine()
    print("\nExecuting certification pipeline (Functional -> Regression -> Determinism -> Stress)...")
    
    report = await engine.run_certification()
    
    print("\n" + "=" * 60)
    print("CERTIFICATION STAGE RESULTS".center(60))
    print("=" * 60)
    
    for stage_res in report.stage_results:
        status = "[PASS]" if stage_res.passed else "[FAIL]"
        print(f"{status} | {stage_res.stage_name} ({stage_res.execution_time_ms:.1f} ms)")
        if not stage_res.passed:
            for err in stage_res.errors:
                print(f"  - ERROR: {err}")
        for warn in stage_res.warnings:
            print(f"  - WARN: {warn}")
            
    print("\n" + "=" * 60)
    print("FINAL CERTIFICATION STATUS".center(60))
    print("=" * 60)
    
    final_status = "CERTIFIED" if report.passed else "FAILED"
    
    print(f"Status:             {final_status}")
    print(f"Total Execution:    {report.execution_metadata.execution_time_ms:.1f} ms")
    print(f"Memory Usage:       {report.execution_metadata.memory_usage_mb:.1f} MB")
    print(f"Pipeline Version:   {report.business_metadata.pipeline_version}")
    print(f"Config Hash:        {report.business_metadata.config_hash}")
    
    # Save the report
    report_json = report.model_dump_json(indent=2)
    report_file = os.path.join(os.path.dirname(__file__), "certification_report.json")
    with open(report_file, "w") as f:
        f.write(report_json)
        
    print(f"\nReport saved to: {report_file}")
    
    if not report.passed:
        sys.exit(1)
        
if __name__ == "__main__":
    asyncio.run(main())
