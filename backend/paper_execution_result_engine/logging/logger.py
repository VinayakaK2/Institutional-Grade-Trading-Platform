import logging

logger = logging.getLogger("PaperExecutionResultEngine")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s\t%(name)s:%(filename)s:%(lineno)d %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class PaperExecutionResultLogger:
    @staticmethod
    def log_snapshot_created(snapshot) -> None:
        logger.info(
            f"Created PaperExecutionSnapshot | "
            f"Version: {snapshot.snapshot_version} | "
            f"Parent Fill: {snapshot.parent_fill_snapshot_version} | "
            f"Parent Order: {snapshot.parent_order_snapshot_version} | "
            f"Pipeline Version: {snapshot.schema_version} | "
            f"Fingerprint: {snapshot.business_fingerprint}"
        )
