from dataclasses import dataclass, field
import re
from typing import List, Tuple, Optional

@dataclass
class PauliString:
    num_qudits: int
    dimension: int = 2
    xpow: List[int] = field(default_factory=list)
    zpow: List[int] = field(default_factory=list)
    phase: int = 0

    def __post_init__(self):
        if not self.xpow:
            self.xpow = [0 for _ in range(self.num_qudits)]
        if not self.zpow:
            self.zpow = [0 for _ in range(self.num_qudits)]

    def __setitem__(self, index: int, new_pauli: str) -> None:
        if index < 0 or index >= self.num_qudits:
            raise IndexError("Index out of range.")
        if isinstance(new_pauli, str):
            match = re.match(r"([A-Z][\-?\d!]*)", new_pauli)
            if match:
                pauli_term = match.group()
                pauli_char = pauli_term[0]
                number_match = re.search(r"-?\d+", pauli_term) 
                number = None
                if number_match:
                    number_str = number_match.group()
                    number = int(number_str)
                    if number < 0:
                        raise ValueError("Pauli operator has power negative value.")
                    if number >= self.dimension:
                        raise ValueError("Pauli operator has power greater than or equal to the dimension.")
                if pauli_char == "X":
                    self.xpow[index] = self.dimension - 1 if "!" in pauli_term else number if number is not None else 1
                    self.zpow[index] = 0
                elif pauli_char == "Z":
                    self.zpow[index] = self.dimension - 1 if "!" in pauli_term else number if number is not None else 1
                    self.xpow[index] = 0
                elif pauli_char == "I":
                    self.xpow[index] = 0
                    self.zpow[index] = 0
                else:
                    raise ValueError("Error with regex finding Pauli term.")
            else:
                raise ValueError("Invalid Pauli operator.")
        else:
            raise ValueError("Invalid object types given.")

    def __str__(self) -> str:
        pauli_string = f"w{self.phase}" if self.phase != 0 else ""
        for i in range(self.num_qudits):
            term = ""
            if self.xpow[i] != 0:
                term += f"X{self.xpow[i]}" if self.xpow[i] != self.dimension - 1 else "X!"
            if self.zpow[i] != 0:
                term += f"Z{self.zpow[i]}" if self.zpow[i] != self.dimension - 1 else "Z!"
            if term == "":
                term = "I"
            pauli_string += f"({term})"
        return pauli_string

    def from_str(self, pauli_string: str):
        """
        Converts a string representation of a Pauli string to its xpow, zpow, and phase representation.
        Expects every qudit to be explicitly represented in the string within its own parentheses.

        Examples:
        "(X2)(X3Z4)" -> ([2, 3], [0, 4], 0) for xpow, zpow, and phase, respectively.
        Similarly,
        "w2(X)(I)(XZ)" -> ([1, 0, 1], [0, 0, 1], 2) with w being the primitive root of unity.
        Finally,
        "(X!)" -> ([d-1], [0], 1) for d being the dimension of the qudits (2 for qubits, 3 for qutrits, etc.)
        Args:
            string (str): The string representation of the Pauli string.
        """
        if pauli_string[0] == "w":
            if self.dimension % 2 == 0:
                self.phase = (int(pauli_string[1]) * 2) % self.dimension
            else:
                self.phase = int(pauli_string[1])
            pauli_string = pauli_string[2:]
        else:
            self.phase = 0

        pauli_terms = get_list_paulis(pauli_string, self.dimension)
        for i, (x, z) in enumerate(pauli_terms):
            if x:
                if "!" in x[1]:
                    self.xpow[i] = self.dimension - 1
                else:
                    x_value = int(x[1])
                    if x_value < 0:
                        raise ValueError("Pauli operator has a negative power value.")
                    if x_value >= self.dimension:
                        raise ValueError("Pauli operator power value is greater than or equal to the dimension.")
                    self.xpow[i] = x_value
            else:
                self.xpow[i] = 0

            if z:
                if "!" in z[1]:
                    self.zpow[i] = self.dimension - 1
                else:
                    z_value = int(z[1])
                    if z_value < 0:
                        raise ValueError("Pauli operator has a negative power value.")
                    if z_value >= self.dimension:
                        raise ValueError("Pauli operator power value is greater than or equal to the dimension.")
                    self.zpow[i] = z_value
            else:
                self.zpow[i] = 0

def get_list_paulis(pauli_string: str, dimension: int) -> List[Tuple[Optional[Tuple[str, str]], Optional[Tuple[str, str]]]]:
    """
    Returns a list of Pauli terms in the Pauli string.
    It first separates it by parentheses and then creates tuples in (X,Z) ordering.
    It requires dimension so that the inverse contains the correct number.
    Examples:
    "(X2)(X3Z4)" -> [(('X', '2'), None), (('X', '3'), ('Z', '4'))]
    "(X!)(Z)" -> [(('X', 'd-1'), None), (None, ('Z', 1))]
    """
    pauli_terms = []
    substring_list = re.findall(r"\((.*?)\)", pauli_string)
    for s in substring_list:
        match = re.match(r"([A-Z][\d!]*)((?:[A-Z][\d!]*)?)", s)
        if not match:
            raise ValueError(f"Invalid Pauli term: {s}")
        groups = match.groups()
        x_term = None
        z_term = None
        for group in groups:
            if group:
                if group[0] == "X":
                    x_term = (group[0], str(dimension - 1)) if "!" in group else (group[0], group[1:] if len(group) > 1 else "1")
                elif group[0] == "Z":
                    z_term = (group[0], str(dimension - 1)) if "!" in group else (group[0], group[1:] if len(group) > 1 else "1")
                elif group[0] == "I":
                    continue
                else:
                    raise ValueError(f"Invalid Pauli operator: {group[0]}")
        pauli_terms.append((x_term, z_term))
    return pauli_terms
