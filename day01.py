from typing import Iterator
from dataclasses import dataclass


TEST_FILENAME = "day1_testdata.txt"
FILENAME = "day1_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclass(frozen=True, order=True)
class LocationId:
    value: int

    def distance(self, other: "LocationId") -> int:
        return abs(self.value - other.value)


@dataclass()
class LocationIds:
    groups: list[list[LocationId]]

    def sort_groups(self) -> None:
        for group in self.groups:
            group.sort()

    def distances(self) -> Iterator[int]:
        for id1, id2 in zip(*self.groups):
            if isinstance(id1, LocationId) and isinstance(id2, LocationId):
                yield id1.distance(id2)

    def total_distance(self) -> int:
        return sum(self.distances())

    def similarity_score(self) -> int:
        location_ids1, location_ids2 = self.groups
        score: int = 0
        for location_id in location_ids1:
            count = location_ids2.count(location_id)
            score += location_id.value * count
        return score

    def __repr__(self):
        row: list[str] = []
        for location_ids in zip(*self.groups):
            row.append(
                "  ".join(str(location_id.value) for location_id in location_ids)
            )
        return "\n".join(row)


def create_location_ids(data: Iterator[str]) -> "LocationIds":
    group1: list["LocationId"] = []
    group2: list["LocationId"] = []
    for location_data in data:
        group1_id, group2_id = location_data.split()
        group1.append(LocationId(value=int(group1_id)))
        group2.append(LocationId(value=int(group2_id)))
    location_ids = LocationIds(groups=[group1, group2])
    return location_ids


def part_one():
    data = yield_data(FILENAME)
    location_ids = create_location_ids(data)
    location_ids.sort_groups()
    return location_ids.total_distance()


def part_two():
    data = yield_data(FILENAME)
    location_ids = create_location_ids(data)
    return location_ids.similarity_score()


def main():
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
