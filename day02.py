from typing import Iterator
import dataclasses
import enum


FILENAME = "day02_data.txt"


class LevelChange(enum.Enum):
    INCREASE = "<"
    DECREASE = ">"
    SAME = "="


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass()
class Report:
    levels: list[int] = dataclasses.field(default_factory=list)

    def distances(self) -> list[int]:
        if not self.levels:
            return []
        current_level = self.levels[0]
        distances: list[int] = []
        for level in self.levels[1:]:
            distances.append(abs(current_level - level))
            current_level = level
        return distances

    def level_changes(self) -> list[LevelChange]:
        if not self.levels:
            return []
        current_level = self.levels[0]
        level_changes: list[LevelChange] = []
        for level in self.levels[1:]:
            if level > current_level:
                level_changes.append(LevelChange.INCREASE)
            elif level < current_level:
                level_changes.append(LevelChange.DECREASE)
            else:
                level_changes.append(LevelChange.SAME)
            current_level = level
        return level_changes

    def is_safe(self) -> bool:
        distances = self.distances()
        level_changes = self.level_changes()
        return all(
            [
                min(distances) >= 1,
                max(distances) <= 3,
                (
                    all(
                        level_change == LevelChange.INCREASE
                        for level_change in level_changes
                    )
                    or all(
                        level_change == LevelChange.DECREASE
                        for level_change in level_changes
                    )
                ),
            ],
        )

    def is_dampened_safe(self) -> bool:
        if self.is_safe():
            # print(f"safe without removing any level: {self.levels}")
            return True
        for location, remove_level in enumerate(self.levels):
            report = Report(self.levels[:location] + self.levels[location + 1 :])
            if report.is_safe():
                # print(f"safe after removing {remove_level}: {report.levels}")
                return True
        # print(f"not safe after removing any level: {self.levels}")
        return False


@dataclasses.dataclass()
class Reports:
    report: list[Report] = dataclasses.field(default_factory=list)

    def safe_report_count(self) -> int:
        return len([report for report in self.report if report.is_safe()])

    def dampened_safe_report_count(self) -> int:
        return len([report for report in self.report if report.is_dampened_safe()])


def create_reports(data: Iterator[str]) -> Reports:
    reports = Reports()
    for report_data in data:
        levels = [int(level) for level in report_data.split()]
        reports.report.append(Report(levels=levels))
    return reports


def part_one():
    data = yield_data(FILENAME)
    reports = create_reports(data)
    return reports.safe_report_count()


def part_two():
    data = yield_data(FILENAME)
    reports = create_reports(data)
    return reports.dampened_safe_report_count()


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
