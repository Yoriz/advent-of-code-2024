import typing
import dataclasses
import enum
import collections


TEST_FILENAME = "day24_testdata.txt"
FILENAME = "day24_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


Value = str | None


class LogicGateType(enum.Enum):
    AND = enum.auto()
    OR = enum.auto()
    XOR = enum.auto()


@dataclasses.dataclass(slots=True)
class Wire:
    name: str
    value: Value = None
    output_gates: list["LogicGate"] = dataclasses.field(default_factory=list)
    input_gate: typing.Optional["LogicGate"] = None

    def add_output_gate(self, gate: "LogicGate") -> None:
        self.output_gates.append(gate)

    def add_input_gate(self, gate: "LogicGate") -> None:
        self.input_gate = gate

    def set_value(self, value: Value) -> None:
        self.value = value
        # print(f"Wire: {self.name}: {self.value}")
        for gate in self.output_gates:
            gate.change_notification(self)

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


@dataclasses.dataclass(slots=True)
class LogicGate:
    type_: LogicGateType
    input_wire1: Wire
    input_wire2: Wire
    output_wire: Wire


    def change_notification(self, wire: Wire) -> None:
        input1 = str(self.input_wire1.value)
        input2 = str(self.input_wire2.value)
        # print(self)
        # print(f"{input1: ^3}{"": ^4} {input2: ^3}")

        if self.input_wire1.value is None or self.input_wire2.value is None:
            return None

        output_value = self.output_value()
        # print(f"{output_value: >17}")
        self.output_wire.set_value(output_value)

        return None

    def output_value(self) -> Value:
        match self.type_:
            case LogicGateType.AND:
                return self.and_output()
            case LogicGateType.OR:
                return self.or_output()
            case LogicGateType.XOR:
                return self.xor_output()

    def and_output(self) -> Value:
        match (self.input_wire1.value, self.input_wire2.value):
            case ("1", "1"):
                return "1"
            case ("0", _) | (_, "0"):
                return "0"
            case _:
                return None

    def or_output(self) -> Value:
        match (self.input_wire1.value, self.input_wire2.value):
            case ("1", _) | (_, "1"):
                return "1"
            case ("0", "0"):
                return "0"
            case _:
                return None

    def xor_output(self) -> Value:
        match (self.input_wire1.value, self.input_wire2.value):
            case ("0", "1") | ("1", "0"):
                return "1"
            case ("1", "1") | ("0", "0"):
                return "0"
            case _:
                return None

    def __str__(self) -> str:
        return f"{self.input_wire1.name} {self.type_.name: <3} {self.input_wire2.name} -> {self.output_wire.name}"


@dataclasses.dataclass(slots=True)
class Connection:
    connection_str: str
    input1_wire_name: str = dataclasses.field(init=False)
    type_: LogicGateType = dataclasses.field(init=False)
    input2_wire_name: str = dataclasses.field(init=False)
    output_wire_name: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        split_string = self.connection_str.split()
        self.input1_wire_name = split_string[0]
        self.type_ = LogicGateType[split_string[1]]
        self.input2_wire_name = split_string[2]
        self.output_wire_name = split_string[4]


@dataclasses.dataclass(slots=True)
class Circuit:
    wires: collections.OrderedDict[str, Wire] = dataclasses.field(
        default_factory=collections.OrderedDict
    )
    initial_wire_names: list[str] = dataclasses.field(default_factory=list)
    gates: list[LogicGate] = dataclasses.field(default_factory=list)

    def add_wire(self, wire: Wire) -> None:
        self.wires[wire.name] = wire

    def add_gate(self, gate: LogicGate) -> None:
        self.gates.append(gate)

    def add_connection(self, connection: Connection) -> None:
        input_wire1 = self.wires.get(
            connection.input1_wire_name, Wire(name=connection.input1_wire_name)
        )
        input_wire2 = self.wires.get(
            connection.input2_wire_name, Wire(name=connection.input2_wire_name)
        )
        output_wire = self.wires.get(
            connection.output_wire_name, Wire(name=connection.output_wire_name)
        )
        gate = LogicGate(connection.type_, input_wire1, input_wire2, output_wire)
        self.gates.append(gate)
        input_wire1.add_output_gate(gate)
        input_wire2.add_output_gate(gate)
        output_wire.add_input_gate(gate)
        self.add_wire(input_wire1)
        self.add_wire(input_wire2)
        self.add_wire(output_wire)

    def trigger_initial_wire_values(self) -> None:
        for wire_name in self.initial_wire_names:
            self.wires[wire_name].set_value(self.wires[wire_name].value)

    def binary_number(self) -> int:
        wires_starting_with_z = [
            wire for wire in self.wires.values() if wire.name.startswith("z")
        ]
        wires_starting_with_z.sort(key=lambda wire: wire.name, reverse=True)
        binary_str = "".join(str(wire.value) for wire in wires_starting_with_z)
        return int(binary_str, 2)


def create_circuit(data: typing.Iterator[str]) -> Circuit:
    circuit = Circuit()
    found_empty_line = False
    for line in data:
        if not line:
            found_empty_line = True
            continue
        if found_empty_line:
            connection = Connection(line)
            circuit.add_connection(connection)
        else:
            name, value = line.split(": ")
            wire = Wire(name, value)
            circuit.add_wire(wire)
            circuit.initial_wire_names.append(name)

    return circuit


def part_one() -> int:
    data = yield_data(FILENAME)
    circuit = create_circuit(data)
    circuit.trigger_initial_wire_values()

    return circuit.binary_number()


def part_two() -> int:
    data = yield_data(TEST_FILENAME)

    return 0


def main() -> None:
    print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
