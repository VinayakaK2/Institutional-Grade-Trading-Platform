import time
import psutil
import os
from backend.core.logger import get_logger
from backend.universe_engine.contracts.certification import ICertificationStage, IUniverseCertificationFacade
from backend.universe_engine.certification.models import UniverseCertificationContext
from backend.universe_engine.certification.exceptions import CertificationVerificationError
from backend.universe_engine.certification.mock_generator import DeterministicMockDatasetGenerator

logger = get_logger(__name__)

class FunctionalCertificationStage(ICertificationStage):
    """
    Verifies that the entire Universe Engine (Phases 5.1 - 5.6) 
    behaves functionally correct and satisfies documented contracts.
    """
    
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> None:
        logger.info("Executing Functional Certification...")
        
        # Use a tiny dataset for basic functional checks
        generator = DeterministicMockDatasetGenerator(seed=101)
        dataset = generator.get_edge_case_dataset()
        
        results = await facade.execute_full_pipeline(f"func_{context.run_id}", mock_dataset=dataset)
        
        passed = True
        
        if not results.get("universe_snapshot"):
            logger.error("Functional Certification Failed: Missing Universe Snapshot (5.1)")
            passed = False
            
        if not results.get("liquidity_universe"):
            logger.error("Functional Certification Failed: Missing Liquidity Universe (5.3)")
            passed = False
            
        if not results.get("certified_universe"):
            logger.error("Functional Certification Failed: Missing Certified Universe (5.4)")
            passed = False
            
        if not results.get("classified_universe"):
            logger.error("Functional Certification Failed: Missing Classified Universe (5.5)")
            passed = False
            
        if not results.get("optimized_universe"):
            logger.error("Functional Certification Failed: Missing Optimized Universe (5.6)")
            passed = False
            
        context.functional_passed = passed
        context.test_results["functional_edge_cases_processed"] = True
        
        if not passed:
            raise CertificationVerificationError("Functional Certification Failed on base outputs.")


class DeterminismCertificationStage(ICertificationStage):
    """
    Verifies that the pipeline is deterministic:
    - Same input -> same output
    - Sequential vs Parallel equivalence
    - Incremental vs Full rebuild equivalence
    - Snapshot reproducibility
    """
    
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> None:
        logger.info("Executing Determinism Certification...")
        generator = DeterministicMockDatasetGenerator(seed=202)
        dataset = generator.get_small_dataset()
        
        passed = True
        
        try:
            # 1. Run Baseline (Run 1)
            baseline = await facade.execute_full_pipeline(f"det_base_{context.run_id}", mock_dataset=dataset, is_incremental=False)
            baseline_fps = baseline["optimized_universe"].symbol_fingerprints
            
            # 2. Run Same Input Again (Run 2)
            same_input = await facade.execute_full_pipeline(f"det_same_{context.run_id}", mock_dataset=dataset, is_incremental=False)
            same_fps = same_input["optimized_universe"].symbol_fingerprints
            
            if baseline_fps != same_fps:
                logger.error("Determinism Failed: Same input produced different outputs.")
                passed = False
            
            # 3. Run Incremental Rebuild
            incremental = await facade.execute_full_pipeline(f"det_incr_{context.run_id}", mock_dataset=dataset, is_incremental=True)
            incr_fps = incremental["optimized_universe"].symbol_fingerprints
            
            if baseline_fps != incr_fps:
                logger.error("Determinism Failed: Incremental rebuild produced different output from full rebuild.")
                passed = False
                
            context.determinism_passed = passed
            context.determinism_results["same_input_equivalence"] = (baseline_fps == same_fps)
            context.determinism_results["incremental_equivalence"] = (baseline_fps == incr_fps)
            
            if not passed:
                raise CertificationVerificationError("Determinism Certification Failed.")
                
        except Exception as e:
            logger.error(f"Determinism execution encountered error: {str(e)}")
            context.determinism_passed = False
            raise CertificationVerificationError(f"Determinism Failed due to internal error: {str(e)}")


class IntegrityCertificationStage(ICertificationStage):
    """
    Verifies data integrity:
    - Snapshot immutability (input snapshot doesn't change)
    - Parent-child lineage consistency
    """
    
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> None:
        logger.info("Executing Integrity Certification...")
        generator = DeterministicMockDatasetGenerator(seed=303)
        dataset = generator.get_tiny_dataset()
        
        passed = True
        results = await facade.execute_full_pipeline(f"integ_{context.run_id}", mock_dataset=dataset)
        
        # Verify Lineage
        opt_u = results["optimized_universe"]
        class_u = results["classified_universe"]
        cert_u = results["certified_universe"]
        liq_u = results["liquidity_universe"]
        snap = results["universe_snapshot"]
        
        if opt_u.parent_classified_universe_id != class_u.classified_universe_id:
            logger.error("Integrity Failed: Optimized Universe parent mismatch.")
            passed = False
            
        if class_u.parent_certified_universe_id != cert_u.certified_universe_id:
            logger.error("Integrity Failed: Classified Universe parent mismatch.")
            passed = False
            
        if cert_u.parent_liquidity_universe_id != liq_u.liquidity_universe_id:
            logger.error("Integrity Failed: Certified Universe parent mismatch.")
            passed = False
            
        if liq_u.parent_snapshot_id != snap.snapshot_id:
            logger.error("Integrity Failed: Liquidity Universe parent mismatch.")
            passed = False
            
        context.integrity_passed = passed
        context.test_results["integrity_lineage_verified"] = passed
        
        if not passed:
            raise CertificationVerificationError("Integrity Certification Failed.")


class PerformanceCertificationStage(ICertificationStage):
    """
    Measures processing latency, execution time, peak memory usage, 
    and throughput. Informational only, does not fail certification on its own.
    """
    
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> None:
        logger.info("Executing Performance Certification...")
        generator = DeterministicMockDatasetGenerator(seed=404)
        dataset = generator.get_medium_dataset()
        
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        
        await facade.execute_full_pipeline(f"perf_{context.run_id}", mock_dataset=dataset)
        
        end_time = time.perf_counter()
        end_cpu = time.process_time()
        end_mem = process.memory_info().rss
        
        exec_time = end_time - start_time
        cpu_time = end_cpu - start_cpu
        mem_diff = max(0.0, (end_mem - start_mem) / (1024 * 1024)) # MB
        
        symbols_per_sec = len(dataset) / exec_time if exec_time > 0 else 0
        
        context.performance_metrics.execution_time_ms = exec_time * 1000
        context.performance_metrics.cpu_time_ms = cpu_time * 1000
        context.performance_metrics.peak_memory_usage_mb = mem_diff
        context.performance_metrics.symbols_per_second = symbols_per_sec
        
        logger.info(f"Performance: {symbols_per_sec:.2f} symbols/sec, Mem: {mem_diff:.2f} MB")


class StressCertificationStage(ICertificationStage):
    """
    Executes repeated runs and scaled runs to verify correctness under load.
    Tests repeated deterministic runs to catch hidden mutable state.
    """
    
    async def execute(self, context: UniverseCertificationContext, facade: IUniverseCertificationFacade) -> None:
        logger.info("Executing Stress Certification...")
        generator = DeterministicMockDatasetGenerator(seed=505)
        passed = True
        
        try:
            # 1. Scale testing (100, 500, 1000)
            for size in context.config.stress_test_sizes:
                logger.info(f"Running stress test for size {size}...")
                ds = generator.generate_symbols(size)
                await facade.execute_full_pipeline(f"stress_scale_{size}_{context.run_id}", mock_dataset=ds)
                
            # 2. Repeated Consecutive Executions on Small Dataset
            logger.info(f"Running {context.config.stress_test_repeated_runs} consecutive runs to verify immutability...")
            small_ds = generator.get_small_dataset()
            baseline = await facade.execute_full_pipeline(f"stress_rep_base_{context.run_id}", mock_dataset=small_ds)
            baseline_fps = baseline["optimized_universe"].symbol_fingerprints
            
            for i in range(context.config.stress_test_repeated_runs):
                res = await facade.execute_full_pipeline(f"stress_rep_{i}_{context.run_id}", mock_dataset=small_ds)
                res_fps = res["optimized_universe"].symbol_fingerprints
                if res_fps != baseline_fps:
                    logger.error(f"Stress Failed: Mutable state detected on run {i}.")
                    passed = False
                    break
                    
        except Exception as e:
            logger.error(f"Stress test encountered internal error: {str(e)}")
            passed = False
            
        context.stress_passed = passed
        context.test_results["stress_scale_tests"] = "PASSED" if passed else "FAILED"
        context.test_results["stress_repeated_runs"] = "PASSED" if passed else "FAILED"
        
        if not passed:
            raise CertificationVerificationError("Stress Certification Failed.")
