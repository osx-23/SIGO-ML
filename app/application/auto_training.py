"""Reentrenamiento periódico en el único proceso del servidor FastAPI."""
import asyncio
from contextlib import asynccontextmanager, suppress
import logging
import os

from app.application.predictor import load_artifact
from training.retrain import retrain

logger = logging.getLogger(__name__)
WEEK_SECONDS = 7 * 24 * 60 * 60


async def training_loop():
    while True:
        try:
            changed = await asyncio.to_thread(retrain)
            if changed:
                # Un request posterior usa el archivo nuevo, no el objeto cacheado.
                load_artifact.cache_clear()
                logger.info("SIGO-ML: modelo recargado tras entrenamiento válido")
        except Exception:
            logger.exception("SIGO-ML: falló el reentrenamiento; se conserva el modelo existente")
        await asyncio.sleep(WEEK_SECONDS)


@asynccontextmanager
async def lifespan(app):
    enabled = os.getenv("SIGO_ML_AUTO_TRAIN_ENABLED", "false").lower() == "true"
    task = asyncio.create_task(training_loop()) if enabled else None
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
