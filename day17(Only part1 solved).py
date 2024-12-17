import typing
import dataclasses
import operator


TEST_FILENAME = "day17_testdata.txt"
FILENAME = "day17_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Computer:
    register_a: int
    register_b: int
    register_c: int
    program: list[int] = dataclasses.field(default_factory=list)
    instruction_pointer: int = 0
    out: list[int] = dataclasses.field(default_factory=list)

    @property
    def has_instruction(self) -> bool:
        return self.instruction_pointer < len(self.program)

    def run_instruction(self):
        if not self.has_instruction:
            return None
        instruction = self.program[self.instruction_pointer]
        self.instruction_pointer += 1
        literal_operand = self.program[self.instruction_pointer]
        self.instruction_pointer += 1
        match instruction:
            case 0:
                numerator = self.register_a
                combo_operand = self.combo_operand(literal_operand)
                denominator = 2**combo_operand
                self.register_a = numerator // denominator
            case 1:
                self.register_b = operator.xor(self.register_b, literal_operand)
            case 2:
                combo_operand = self.combo_operand(literal_operand)
                self.register_b = combo_operand % 8
            case 3:
                if self.register_a == 0:
                    return None
                self.instruction_pointer = literal_operand
            case 4:
                self.register_b = operator.xor(self.register_b, self.register_c)
            case 5:
                combo_operand = self.combo_operand(literal_operand)
                self.out.append(combo_operand % 8)
            case 6:
                numerator = self.register_a
                combo_operand = self.combo_operand(literal_operand)
                denominator = 2**combo_operand
                self.register_b = numerator // denominator
            case 7:
                numerator = self.register_a
                combo_operand = self.combo_operand(literal_operand)
                denominator = 2**combo_operand
                self.register_c = numerator // denominator

    def combo_operand(self, instruction: int) -> int:
        match instruction:
            case instruction if instruction in (0, 1, 2, 3):
                return instruction
            case 4:
                return self.register_a
            case 5:
                return self.register_b
            case 6:
                return self.register_c
            case _:
                raise ValueError(f"Invalid instruction: {instruction}")

    def output(self) -> str:
        return ",".join([str(x) for x in self.out])


def create_computer(data: typing.Iterator[str]) -> Computer:
    for line in data:
        if not line:
            continue
        label, value = line.split(":")
        match label:
            case "Register A":
                register_a = int(value)
            case "Register B":
                register_b = int(value)
            case "Register C":
                register_c = int(value)
            case "Program":
                program = [int(x) for x in value.split(",")]

    return Computer(register_a, register_b, register_c, program)


def part_one() -> str:
    data = yield_data(FILENAME)
    computer = create_computer(data)
    print(computer)
    while computer.has_instruction:
        computer.run_instruction()
    print(computer)
    return computer.output()


def part_two() -> int:
    data = yield_data(FILENAME)
    orginal_computer = create_computer(data)

    # print(computer)
    register_a = 0
    while True:
        computer = Computer(
            register_a,
            orginal_computer.register_b,
            orginal_computer.register_c,
            orginal_computer.program,
        )

        print(f"In loop: {register_a}")
        while computer.has_instruction:
            computer.run_instruction()
        if computer.out == computer.program:
            print(f"Found match")
            break

        register_a += 1

    return register_a


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")

    return None


if __name__ == "__main__":
    main()
