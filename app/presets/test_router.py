"""
test_router.py - Unit test per verificare gli endpoint dei preset.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.presets.router import create_preset
from app.presets.schemas import PresetCreate
from app.users.models import User  # Necessario per registrare la classe User in SQLAlchemy registry


class TestPresetRouter(unittest.IsolatedAsyncioTestCase):

    async def test_create_preset_success(self) -> None:
        """
        Verifica che create_preset salvi correttamente il preset con user_id=1.
        """
        # Arrange
        body = PresetCreate(
            name="Classic Clean",
            description="Clean pedal chain",
            effects_chain=[
                {
                    "id": "delay-1",
                    "type": "delay",
                    "order_index": 0,
                    "bypass": False,
                    "params": {"delay_time": 0.4}
                }
            ]
        )
        
        db_mock = MagicMock()
        db_mock.add = MagicMock()
        db_mock.flush = AsyncMock()
        db_mock.refresh = AsyncMock()
        
        # Act
        preset = await create_preset(body=body, db=db_mock)
        
        # Assert
        self.assertEqual(preset.name, "Classic Clean")
        self.assertEqual(preset.description, "Clean pedal chain")
        self.assertEqual(preset.user_id, 1)
        self.assertEqual(len(preset.config_json), 1)
        self.assertEqual(preset.config_json[0]["type"], "delay")
        
        # Verify db actions
        db_mock.add.assert_called_once_with(preset)
        db_mock.flush.assert_called_once()
        db_mock.refresh.assert_called_once_with(preset)

    async def test_create_preset_db_error_rollback(self) -> None:
        """
        Verifica che un errore del database esegua il rollback e sollevi un errore HTTP 400.
        """
        # Arrange
        body = PresetCreate(
            name="Classic Clean",
            description="Clean pedal chain",
            effects_chain=[]
        )
        
        db_mock = MagicMock()
        db_mock.add = MagicMock()
        db_mock.flush = AsyncMock(side_effect=SQLAlchemyError("Database connection lost"))
        db_mock.rollback = AsyncMock()
        
        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            await create_preset(body=body, db=db_mock)
            
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Database error during preset creation", context.exception.detail)
        db_mock.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
