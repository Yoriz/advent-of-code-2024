from typing import Iterator
import dataclasses
import enum
import itertools
import functools


FILENAME = "day07_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class OperatorType(enum.Enum):
    ADD = "+"
    MULTIPLY = "*"
    CONCATENATE = "||"


@functools.cache
def operator_combinations(
    operators: list[OperatorType], repeat: int
) -> tuple[tuple[OperatorType, ...], ...]:
    return tuple(itertools.product(operators, repeat=repeat))


@dataclasses.dataclass
class Equation:
    equation_string: str
    total: int


@dataclasses.dataclass
class EquationLine:
    total: int
    operator_types: tuple[OperatorType, ...]
    numbers: list[str] = dataclasses.field(default_factory=list)

    def equation_combinations(self) -> list[Equation]:
        combinations: list[Equation] = []

        for operator_list in operator_combinations(
            self.operator_types, repeat=len(self.numbers) - 1
        ):
            equation_string = self.numbers[0]
            score = int(self.numbers[0])
            for number, operator in zip(self.numbers[1:], operator_list):
                equation_string = f"{operator.value}".join([equation_string, number])
                match operator:
                    case OperatorType.ADD:
                        score = score + int(number)
                    case OperatorType.MULTIPLY:
                        score = score * int(number)
                    case OperatorType.CONCATENATE:
                        score = int(str(score) + number)
            equation = Equation(equation_string, total=score)
            combinations.append(equation)
        return combinations


@dataclasses.dataclass
class CalibrationEquations:
    equation_lines: list[EquationLine] = dataclasses.field(default_factory=list)

    def add_equation(self, equation: EquationLine) -> None:
        self.equation_lines.append(equation)

    def total_calibration_result(self) -> int:
        score = 0
        for equation_line in self.equation_lines:
            for equation in equation_line.equation_combinations():
                if equation.total == equation_line.total:
                    print(f"Found equation: {equation_line.total=} {equation}")
                    score += equation.total
                    break

        return score


def create_calibration_equations(
    data: Iterator[str], operator_types: tuple[OperatorType, ...]
) -> CalibrationEquations:
    calibration_equations = CalibrationEquations()

    for line in data:
        result, number_sequence = line.split(":")
        numbers = number_sequence.strip().split(" ")
        total = int(result)
        equation_line = EquationLine(
            total=total, operator_types=operator_types, numbers=numbers
        )
        calibration_equations.add_equation(equation_line)
    return calibration_equations


def part_one() -> int:
    data = yield_data(FILENAME)
    calibration_equations = create_calibration_equations(
        data, (OperatorType.ADD, OperatorType.MULTIPLY)
    )
    return calibration_equations.total_calibration_result()


def part_two() -> int:
    data = yield_data(FILENAME)
    calibration_equations = create_calibration_equations(
        data, (OperatorType.ADD, OperatorType.MULTIPLY, OperatorType.CONCATENATE)
    )
    return calibration_equations.total_calibration_result()


def main() -> None:
    # print(f"Part one: {part_one()}")
    # print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
