import pytest
import cirq as cirq
import random
from sdim.circuit import Circuit
from sdim.program import Program
from sdim.tableau.dataclasses import MeasurementResult
from sdim.circuit_io import cirq_statevector_from_circuit

def test_phase_kickback():
    circuit = Circuit(2, 2)
    circuit.add_gate("H", 1)
    circuit.add_gate("P", 1)

    circuit.add_gate("H", 0)
    circuit.add_gate("CNOT", 0, 1)
    circuit.add_gate("H", 1)
    circuit.add_gate("CNOT", 0, 1)
    circuit.add_gate("H", 1)

    circuit.add_gate("P", 0)
    circuit.add_gate("H", 0)
    circuit.add_gate("M", 0)
    circuit.add_gate("P", 1)
    circuit.add_gate("H", 1)
    circuit.add_gate("M", 1)
    program = Program(circuit)
    assert program.simulate() == [MeasurementResult(0, True, 1), MeasurementResult(1, True, 1)]

def test_qubit_flip():
    circuit = Circuit(2, 2)
    circuit.add_gate("H", 0)
    circuit.add_gate("P", 0)
    circuit.add_gate("P", 0)
    circuit.add_gate("H", 0)
    circuit.add_gate("M", 0)
    circuit.add_gate("X", 1)
    circuit.add_gate("M", 1)
    program = Program(circuit)
    assert program.simulate() == [MeasurementResult(0, True, 1), MeasurementResult(1, True, 1)]

def test_qutrit_flip():
    circuit = Circuit(2, 3)
    circuit.add_gate("X", 0)
    circuit.add_gate("M", 0)
    program = Program(circuit)
    assert program.simulate() == [MeasurementResult(0, True, 1)]

def test_qubit_deutsch():
    # Create circuit
    circuit = Circuit(2, 2)

    # Put qudits into |+> and |-> states
    circuit.add_gate("H", 0)
    circuit.add_gate("X", 1)
    circuit.add_gate("H", 1)

    secret_function = [random.randint(0, 1) for _ in range(2)]

    if secret_function[0]:  # pragma: no cover
        circuit.add_gate("CNOT", 0, 1)
        circuit.add_gate("X", 1)

    if secret_function[1]:  # pragma: no cover
        circuit.add_gate("CNOT", 0, 1)

    circuit.add_gate("H", 0)

    circuit.add_gate("M", 0)

    program = Program(circuit)

    if secret_function[0] == secret_function[1]:
        expected_result = 0
    else:
        expected_result = 1
    
    assert program.simulate() == [MeasurementResult(0, True, expected_result)]

def test_deutsch():
    # input the dimension here
    d = 3
    
    # Create circuit
    circuit = Circuit(2, d)

    # Put qudits into |+> and |-> states
    circuit.add_gate("H", 0)
    circuit.add_gate("X", 1)
    circuit.add_gate("H", 1)

    is_constant = random.choice([True, False])

    if is_constant:
        # constant function is a random constant between 0 and d - 1 inclusive
        function_constant = random.choice([i for i in range(d)])
        for i in range(function_constant):
            circuit.add_gate("X", 1)
    else:
        # identity function
        circuit.add_gate("CNOT", 0, 1)

    circuit.add_gate("H", 0)

    circuit.add_gate("M", 0)

    program = Program(circuit)

    if is_constant:
        expected_result = 0
    else:
        expected_result = 1
    
    assert program.simulate() == [MeasurementResult(0, True, expected_result)]
