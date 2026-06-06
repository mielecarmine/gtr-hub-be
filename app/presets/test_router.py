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
        
        # Mock database select result for non-existent client_id checking
        result_mock = MagicMock()
        result_mock.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
        db_mock.execute = AsyncMock(return_value=result_mock)
        
        # Act
        preset = await create_preset(body=body, db=db_mock, current_user=MagicMock(id=1))
        
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
        
        # Mock database select result for non-existent client_id checking
        result_mock = MagicMock()
        result_mock.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))
        db_mock.execute = AsyncMock(return_value=result_mock)
        
        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            await create_preset(body=body, db=db_mock, current_user=MagicMock(id=1))
            
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Database error during preset creation", context.exception.detail)
        db_mock.rollback.assert_called_once()

    async def test_create_preset_idempotency(self) -> None:
        """
        Verifica che create_preset restituisca il preset esistente se viene fornito lo stesso client_id.
        """
        # Arrange
        body = PresetCreate(
            name="Idempotent Preset",
            client_id="unique-uuid-123",
            effects_chain=[]
        )
        
        db_mock = MagicMock()
        db_mock.add = MagicMock()
        
        # Simula il risultato della query per client_id
        existing_preset = MagicMock()
        existing_preset.name = "Idempotent Preset"
        existing_preset.client_id = "unique-uuid-123"
        
        result_mock = MagicMock()
        result_mock.scalars = MagicMock(return_value=MagicMock(first=MagicMock(return_value=existing_preset)))
        db_mock.execute = AsyncMock(return_value=result_mock)
        
        # Act
        preset = await create_preset(body=body, db=db_mock, current_user=MagicMock(id=1))
        
        # Assert
        self.assertEqual(preset, existing_preset)
        db_mock.add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
