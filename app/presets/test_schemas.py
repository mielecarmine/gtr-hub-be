"""
test_schemas.py - Unit test per verificare la validazione e serializzazione degli schemi dei preset.
"""
import unittest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.pedal.schemas import PedalSchema
from app.presets.schemas import PresetCreate, PresetOut


class MockSQLAlchemyPreset:
    """
    Simula un modello ORM SQLAlchemy per testare model_validate.
    """
    def __init__(self, id: int, name: str, description: str | None, user_id: int, config_json: list, created_at: datetime):
        self.id = id
        self.name = name
        self.description = description
        self.user_id = user_id
        self.config_json = config_json
        self.created_at = created_at


class TestPresetSchemas(unittest.TestCase):

    def test_valid_preset_creation_happy_path(self) -> None:
        """
        AC 2: Verifica la creazione con successo di un preset valido avente una catena effetti.
        """
        payload = {
            "name": "Heavy Metal Rhythm",
            "description": "Preset con alto guadagno per chitarra metal",
            "effects_chain": [
                {
                    "id": "pedal-1",
                    "type": "distortion",
                    "order_index": 0,
                    "bypass": False,
                    "params": {
                        "gain": 8.5,
                        "tone": 5.0,
                        "volume": 7.0
                    }
                },
                {
                    "id": "pedal-2",
                    "type": "amplifier",
                    "order_index": 1,
                    "bypass": False,
                    "params": {
                        "bass": 6,
                        "middle": 4,
                        "treble": 7,
                        "presence": True
                    }
                }
            ]
        }
        preset = PresetCreate(**payload)
        self.assertEqual(preset.name, "Heavy Metal Rhythm")
        self.assertEqual(len(preset.effects_chain), 2)
        self.assertEqual(preset.effects_chain[0].type, "distortion")
        self.assertEqual(preset.effects_chain[1].params["presence"], True)

    def test_empty_effects_chain(self) -> None:
        """
        AC 2: L'oggetto effects_chain deve essere validato come lista vuota [] (canale pulito).
        """
        payload = {
            "name": "Clean Signal",
            "description": "Nessun pedale attivo nella catena",
            "effects_chain": []
        }
        preset = PresetCreate(**payload)
        self.assertEqual(preset.effects_chain, [])

    def test_invalid_pedal_type(self) -> None:
        """
        AC 1: Il campo type deve accettare solo stringhe predefinite. Se viene inserito "flanger", solleva ValidationError.
        """
        payload = {
            "name": "Psychedelic Flanger",
            "effects_chain": [
                {
                    "id": "pedal-1",
                    "type": "flanger",  # Non supportato da Literal
                    "order_index": 0,
                    "bypass": False,
                    "params": {}
                }
            ]
        }
        with self.assertRaises(ValidationError) as context:
            PresetCreate(**payload)
        
        self.assertIn("type", str(context.exception))
        self.assertIn("Input should be 'distortion', 'delay', 'reverb', 'amplifier' or 'chorus'", str(context.exception))

    def test_prevention_of_malformed_nested_payload(self) -> None:
        """
        AC 4: Se params contiene strutture nidificate non autorizzate (es: dizionari o liste), solleva ValidationError.
        """
        payload = {
            "name": "Malformed Params",
            "effects_chain": [
                {
                    "id": "pedal-1",
                    "type": "delay",
                    "order_index": 0,
                    "bypass": False,
                    "params": {
                        "time": {"seconds": 0.5, "milliseconds": 500}  # Struttura nidificata non ammessa
                    }
                }
            ]
        }
        with self.assertRaises(ValidationError) as context:
            PresetCreate(**payload)
            
        self.assertIn("effects_chain", str(context.exception))
        # Verifica che il fallimento sia dovuto al tipo non consentito per PedalParamValue
        self.assertIn("Input should be a valid integer", str(context.exception))

    def test_orm_compatibility_preset_out(self) -> None:
        """
        AC 3: PresetOut deve essere in grado di effettuare il parsing diretto dal modello SQLAlchemy
        (che ha la colonna config_json) tramite from_attributes=True.
        """
        now = datetime.now(timezone.utc)
        orm_mock = MockSQLAlchemyPreset(
            id=123,
            name="Classic Overdrive",
            description="Simulatore TS9",
            user_id=1,
            config_json=[
                {
                    "id": "ts9",
                    "type": "distortion",
                    "order_index": 0,
                    "bypass": False,
                    "params": {
                        "drive": 6.5,
                        "tone": 4.0
                    }
                }
            ],
            created_at=now
        )

        preset_out = PresetOut.model_validate(orm_mock)
        self.assertEqual(preset_out.id, 123)
        self.assertEqual(preset_out.name, "Classic Overdrive")
        self.assertEqual(len(preset_out.effects_chain), 1)
        self.assertEqual(preset_out.effects_chain[0].id, "ts9")
        self.assertEqual(preset_out.effects_chain[0].params["drive"], 6.5)


if __name__ == "__main__":
    unittest.main()
