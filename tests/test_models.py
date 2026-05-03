"""
SPDX-FileCopyrightText: 2025 Michael Czigler
SPDX-License-Identifier: BSD-3-Clause

Data model tests.
"""

from unittest import main
from unittest import TestCase
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

from openhti.models.base import Measurement
from openhti.models.base import MeasurementOutcome
from openhti.models.base import Phase
from openhti.models.base import PhaseOutcome
from openhti.models.base import PhaseResult
from openhti.models.base import Procedure
from openhti.models.base import UnitUnderTest
from openhti.models.broker import Broker
from openhti.models.recipe import in_range
from openhti.models.recipe import get_millis


class TestMeasurementOutcome(TestCase):
    """Test MeasurementOutcome enum."""

    def test_measurement_outcome_pass(self):
        """Test PASS outcome."""

        self.assertEqual(MeasurementOutcome.PASS, "PASS")

    def test_measurement_outcome_fail(self):
        """Test FAIL outcome."""

        self.assertEqual(MeasurementOutcome.FAIL, "FAIL")

    def test_measurement_outcome_unset(self):
        """Test UNSET outcome."""

        self.assertEqual(MeasurementOutcome.UNSET, "UNSET")


class TestPhaseOutcome(TestCase):
    """Test PhaseOutcome enum."""

    def test_phase_outcome_pass(self):
        """Test PASS outcome."""

        self.assertEqual(PhaseOutcome.PASS, "PASS")

    def test_phase_outcome_fail(self):
        """Test FAIL outcome."""

        self.assertEqual(PhaseOutcome.FAIL, "FAIL")

    def test_phase_outcome_skip(self):
        """Test SKIP outcome."""

        self.assertEqual(PhaseOutcome.SKIP, "SKIP")

    def test_phase_outcome_error(self):
        """Test ERROR outcome."""

        self.assertEqual(PhaseOutcome.ERROR, "ERROR")


class TestPhaseResult(TestCase):
    """Test PhaseResult enum."""

    def test_phase_result_continue(self):
        """Test CONTINUE result."""

        self.assertEqual(PhaseResult.CONTINUE, "CONTINUE")

    def test_phase_result_fail_and_continue(self):
        """Test FAIL_AND_CONTINUE result."""

        self.assertEqual(PhaseResult.FAIL_AND_CONTINUE, "FAIL_AND_CONTINUE")

    def test_phase_result_repeat(self):
        """Test REPEAT result."""

        self.assertEqual(PhaseResult.REPEAT, "REPEAT")

    def test_phase_result_skip(self):
        """Test SKIP result."""

        self.assertEqual(PhaseResult.SKIP, "SKIP")

    def test_phase_result_stop(self):
        """Test STOP result."""

        self.assertEqual(PhaseResult.STOP, "STOP")


class TestMeasurementDataclass(TestCase):
    """Test Measurement dataclass."""

    def test_measurement_creation_minimal(self):
        """Test creating Measurement with minimal fields."""

        m = Measurement(name="voltage", outcome=MeasurementOutcome.PASS)
        self.assertEqual(m.name, "voltage")
        self.assertEqual(m.outcome, MeasurementOutcome.PASS)
        self.assertIsNone(m.measured_value)
        self.assertIsNone(m.units)

    def test_measurement_creation_full(self):
        """Test creating Measurement with all fields."""

        m = Measurement(
            name="voltage",
            outcome=MeasurementOutcome.PASS,
            measured_value=5.0,
            units="V",
            lower_limit=4.5,
            upper_limit=5.5,
            validators=["voltage_validator"],
            docstring="Voltage test",
        )
        self.assertEqual(m.name, "voltage")
        self.assertEqual(m.outcome, MeasurementOutcome.PASS)
        self.assertEqual(m.measured_value, 5.0)
        self.assertEqual(m.units, "V")
        self.assertEqual(m.lower_limit, 4.5)
        self.assertEqual(m.upper_limit, 5.5)
        self.assertEqual(m.validators, ["voltage_validator"])
        self.assertEqual(m.docstring, "Voltage test")

    def test_measurement_with_failed_outcome(self):
        """Test Measurement with FAIL outcome."""

        m = Measurement(
            name="current",
            outcome=MeasurementOutcome.FAIL,
            measured_value=2.0,
            lower_limit=1.0,
            upper_limit=1.5,
        )
        self.assertEqual(m.outcome, MeasurementOutcome.FAIL)
        self.assertEqual(m.measured_value, 2.0)


class TestPhaseDataclass(TestCase):
    """Test Phase dataclass."""

    def test_phase_creation_minimal(self):
        """Test creating Phase with minimal fields."""

        p = Phase(
            name="initialization",
            outcome=PhaseOutcome.PASS,
            start_time_millis=1000,
            end_time_millis=2000,
        )
        self.assertEqual(p.name, "initialization")
        self.assertEqual(p.outcome, PhaseOutcome.PASS)
        self.assertEqual(p.start_time_millis, 1000)
        self.assertEqual(p.end_time_millis, 2000)
        self.assertIsNone(p.measurements)

    def test_phase_creation_with_measurements(self):
        """Test creating Phase with measurements."""

        measurements = [
            Measurement(name="voltage", outcome=MeasurementOutcome.PASS),
            Measurement(name="current", outcome=MeasurementOutcome.PASS),
        ]
        p = Phase(
            name="test",
            outcome=PhaseOutcome.PASS,
            start_time_millis=1000,
            end_time_millis=3000,
            measurements=measurements,
        )
        self.assertEqual(len(p.measurements), 2)
        self.assertEqual(p.measurements[0].name, "voltage")

    def test_phase_with_failed_outcome(self):
        """Test Phase with FAIL outcome and measurements."""

        measurements = [
            Measurement(name="voltage", outcome=MeasurementOutcome.FAIL),
        ]
        p = Phase(
            name="test",
            outcome=PhaseOutcome.FAIL,
            start_time_millis=1000,
            end_time_millis=2000,
            measurements=measurements,
        )
        self.assertEqual(p.outcome, PhaseOutcome.FAIL)
        self.assertEqual(len(p.measurements), 1)


class TestUnitUnderTestDataclass(TestCase):
    """Test UnitUnderTest dataclass."""

    def test_unit_creation_minimal(self):
        """Test creating UnitUnderTest with serial number only."""

        u = UnitUnderTest(serial_number="SN123456")
        self.assertEqual(u.serial_number, "SN123456")
        self.assertIsNone(u.part_number)
        self.assertIsNone(u.part_name)

    def test_unit_creation_full(self):
        """Test creating UnitUnderTest with all fields."""

        u = UnitUnderTest(
            serial_number="SN123456",
            part_number="PN-001",
            part_name="Widget A",
            revision="1.0",
            batch_number="BATCH-2025-001",
            global_trade_item_number="5012345678905",
        )
        self.assertEqual(u.serial_number, "SN123456")
        self.assertEqual(u.part_number, "PN-001")
        self.assertEqual(u.part_name, "Widget A")
        self.assertEqual(u.revision, "1.0")
        self.assertEqual(u.batch_number, "BATCH-2025-001")


class TestProcedureDataclass(TestCase):
    """Test Procedure dataclass."""

    def test_procedure_creation_minimal(self):
        """Test creating Procedure with minimal fields."""

        p = Procedure(
            procedure_id="PROC-001",
            procedure_name="Initialization Test",
        )
        self.assertEqual(p.procedure_id, "PROC-001")
        self.assertEqual(p.procedure_name, "Initialization Test")
        self.assertIsNone(p.unit_under_test)
        self.assertEqual(p.phases, [])
        self.assertTrue(p.run_passed)

    def test_procedure_creation_with_unit(self):
        """Test creating Procedure with unit under test."""

        unit = UnitUnderTest(serial_number="SN123")
        p = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            unit_under_test=unit,
        )
        self.assertEqual(p.unit_under_test.serial_number, "SN123")

    def test_procedure_creation_with_phases(self):
        """Test creating Procedure with phases."""

        phases = [
            Phase(
                name="phase1",
                outcome=PhaseOutcome.PASS,
                start_time_millis=1000,
                end_time_millis=2000,
            ),
        ]
        p = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            phases=phases,
        )
        self.assertEqual(len(p.phases), 1)
        self.assertEqual(p.phases[0].name, "phase1")

    def test_procedure_run_failed(self):
        """Test Procedure with run_passed=False."""

        p = Procedure(
            procedure_id="PROC-001",
            procedure_name="Test",
            run_passed=False,
        )
        self.assertFalse(p.run_passed)


class TestBroker(TestCase):
    """Test Broker websocket message broker."""

    def test_broker_init(self):
        """Test Broker initialization."""

        broker = Broker()
        self.assertEqual(len(broker.connections), 0)
        self.assertIsInstance(broker.connections, set)

    async def test_broker_subscribe(self):
        """Test subscribing to broker."""

        broker = Broker()
        # Create subscription
        subscription = broker.subscribe()
        # Connection should be added
        self.assertEqual(len(broker.connections), 1)

    @patch("asyncio.Queue")
    async def test_broker_publish(self, mock_queue_class):
        """Test publishing message to all subscribers."""

        mock_queue = AsyncMock()
        broker = Broker()
        # Manually add a connection
        broker.connections.add(mock_queue)
        # Publish message
        await broker.publish("test message")
        # Verify put was called
        mock_queue.put.assert_called_once_with("test message")


class TestInRangeFunction(TestCase):
    """Test in_range function for measurement validation."""

    def test_in_range_pass(self):
        """Test value within range returns PASS."""

        result = in_range(value=5.0, ll=4.0, ul=6.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.PASS)

    def test_in_range_fail_above_upper_limit(self):
        """Test value above upper limit returns FAIL."""

        result = in_range(value=7.0, ll=4.0, ul=6.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.FAIL)

    def test_in_range_fail_below_lower_limit(self):
        """Test value below lower limit returns FAIL."""

        result = in_range(value=3.0, ll=4.0, ul=6.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.FAIL)

    def test_in_range_at_upper_limit(self):
        """Test value at upper limit boundary returns FAIL (exclusive)."""

        result = in_range(value=6.0, ll=4.0, ul=6.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.FAIL)

    def test_in_range_at_lower_limit(self):
        """Test value at lower limit boundary returns FAIL (exclusive)."""

        result = in_range(value=4.0, ll=4.0, ul=6.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.FAIL)

    def test_in_range_with_precision(self):
        """Test rounding with precision parameter."""

        result = in_range(value=5.04, ll=5.0, ul=5.1, prec=2)
        self.assertEqual(result, MeasurementOutcome.PASS)

    def test_in_range_with_high_precision(self):
        """Test rounding with high precision (3 decimals)."""

        result = in_range(value=5.0001, ll=5.0, ul=5.001, prec=3)
        self.assertEqual(result, MeasurementOutcome.PASS)

    def test_in_range_negative_values(self):
        """Test in_range with negative values."""

        result = in_range(value=-5.0, ll=-6.0, ul=-4.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.PASS)

    def test_in_range_negative_fail(self):
        """Test in_range with negative values fails correctly."""

        result = in_range(value=-7.0, ll=-6.0, ul=-4.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.FAIL)

    def test_in_range_zero_crossing(self):
        """Test in_range with range crossing zero."""

        result = in_range(value=0.0, ll=-5.0, ul=5.0, prec=1)
        self.assertEqual(result, MeasurementOutcome.PASS)

    def test_in_range_floating_point_precision(self):
        """Test in_range with floating point precision edge case."""

        result = in_range(value=0.1 + 0.2, ll=0.2, ul=0.4, prec=1)
        # 0.1 + 0.2 = 0.30000000000000004, should round to 0.3
        self.assertEqual(result, MeasurementOutcome.PASS)


class TestGetMillisFunction(TestCase):
    """Test get_millis timestamp function."""

    def test_get_millis_returns_float(self):
        """Test get_millis returns a float timestamp."""

        result = get_millis()
        self.assertIsInstance(result, float)

    def test_get_millis_is_positive(self):
        """Test get_millis returns positive value."""

        result = get_millis()
        self.assertGreater(result, 0)

    def test_get_millis_increases(self):
        """Test get_millis increases over time."""

        import time

        millis1 = get_millis()
        time.sleep(0.01)  # Sleep 10ms
        millis2 = get_millis()
        self.assertGreater(millis2, millis1)


if __name__ == "__main__":
    main()
