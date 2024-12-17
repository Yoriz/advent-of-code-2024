import dataclasses
import enum
import typing
import collections


TEST_FILENAME = "day12_testdata.txt"
FILENAME = "day12_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


class LocationType(enum.Enum):
    PLANT = enum.auto()
    OUT_OF_BOUNDS = enum.auto()


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


@dataclasses.dataclass(slots=True, frozen=True)
class GridLocation:
    location: Location
    label: str
    location_type: LocationType

    @property
    def x(self) -> int:
        return self.location.x

    @property
    def y(self) -> int:
        return self.location.y


@dataclasses.dataclass
class Grid:
    grid_locations: dict[tuple[int, int], GridLocation] = dataclasses.field(
        default_factory=dict
    )
    max_x_location: int = 0
    max_y_location: int = 0

    def add_grid_location(self, grid_location: GridLocation) -> None:
        self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
        self.update_max_values(grid_location.location)

        return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)
        return None

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, "@", LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get((location.x, location.y))
        if not grid_location:
            raise ValueError("GridLocation not found")

        return grid_location

    def location_in_grid(self, location: Location) -> bool:
        return all(
            (
                location.x > -1,
                location.x < self.max_x_location + 1,
                location.y > -1,
                location.y < self.max_y_location + 1,
            )
        )

    def __str__(self) -> str:
        rows: list[str] = []
        for y_index in range(self.max_y_location + 1):
            row = ""
            for x_index in range(self.max_x_location + 1):
                location = Location(x_index, y_index)
                grid_location = self.get_grid_location(location)
                row = f"{row}{grid_location.label}"
            rows.append(row)
        return "\n".join(rows)


def create_grid(data: typing.Iterator[str]) -> Grid:
    grid = Grid()
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            location_type = LocationType.PLANT
            grid_location = GridLocation(location, character, location_type)
            grid.add_grid_location(grid_location)

    return grid


@dataclasses.dataclass
class Region:
    grid: Grid
    grid_locations: list[GridLocation] = dataclasses.field(default_factory=list)
    bulk_discount: bool = False

    @property
    def label(self) -> str:
        return self.grid_locations[0].label if self.grid_locations else ""

    @property
    def area(self) -> int:
        return len(self.grid_locations)

    @property
    def perimeter(self) -> int:
        score = 0
        for grid_location in self.grid_locations:
            for location_direction in LocationDirection:
                location = grid_location.location
                neighbour_location = location.neighbour_location(location_direction)
                neighbour_grid_location = self.grid.get_grid_location(
                    neighbour_location
                )
                if neighbour_grid_location.label != self.label:
                    score += 1
        return score
    
    @property
    def number_of_sides(self) -> int:
        return 4

    @property
    def fence_price(self) -> int:
        if self.bulk_discount:
            return self.area * self.number_of_sides
        return self.area * self.perimeter

    @property
    def locations(self) -> set[Location]:
        return {grid_location.location for grid_location in self.grid_locations}

    def find_grid_locations(self, start_location: Location) -> None:
        grid_location = self.grid.get_grid_location(start_location)
        self.grid_locations.append(grid_location)
        queue = collections.deque([grid_location])
        while queue:
            grid_location = queue.popleft()
            location = grid_location.location
            for location_direction in LocationDirection:
                neighbour_location = location.neighbour_location(location_direction)
                neighbour_grid_location = self.grid.get_grid_location(
                    neighbour_location
                )
                if neighbour_grid_location in self.grid_locations:
                    continue
                if neighbour_grid_location.label == self.label:
                    self.grid_locations.append(neighbour_grid_location)
                    queue.append(neighbour_grid_location)

    def __str__(self) -> str:
        return f"Label: {self.label}, Area: {self.area}, Perimeter: {self.perimeter}, Fence Price: {self.fence_price}"



@dataclasses.dataclass
class Regions:
    grid: Grid
    regions: list[Region] = dataclasses.field(default_factory=list)
    visited_locations: set[Location] = dataclasses.field(default_factory=set)

    @property
    def total_fence_price(self) -> int:
        return sum(region.fence_price for region in self.regions)

    def find_regions(self) -> None:
        for y_index in range(self.grid.max_y_location + 1):
            for x_index in range(self.grid.max_x_location + 1):
                location = Location(x_index, y_index)
                print(location)
                if location in self.visited_locations:
                    continue

                region = Region(self.grid)
                region.find_grid_locations(location)
                self.regions.append(region)
                self.visited_locations.update(region.locations)


def part_one() -> int:
    data = yield_data(FILENAME)
    grid = create_grid(data)
    regions = Regions(grid)
    regions.find_regions()
    return regions.total_fence_price


def part_two() -> int:
    data = yield_data(TEST_FILENAME)
    grid = create_grid(data)
    regions = Regions(grid)
    regions.find_regions()

    return 0


def main() -> None:
    # print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
