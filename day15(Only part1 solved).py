import dataclasses
import enum
import typing


TEST_FILENAME = "day15_testdata.txt"
FILENAME = "day15_data.txt"

SPLITTER: typing.Final[str] = "S"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            if line == "\n":
                yield LocationType.SPLITTER.value
            yield line.strip()


class LocationType(enum.Enum):
    ROBOT = "@"
    EMPTY = "."
    BOX = "O"
    WALL = "#"
    OUT_OF_BOUNDS = "X"
    SPLITTER = "S"
    BOX_LEFT = "["
    BOX_RIGHT = "]"


@dataclasses.dataclass(slots=True, frozen=True)
class Location:
    x: int
    y: int

    # def differance(self, other: "Location") -> "Location":
    #     return Location(self.x - other.x, self.y - other.y)

    # def offset_by(self, differance: "Location") -> "Location":
    #     return Location(self.x + differance.x, self.y + differance.y)

    def neighbour_location(self, location_direction: "LocationDirection") -> "Location":
        other_location: "Location" = location_direction.value
        return Location(self.x + other_location.x, self.y + other_location.y)


@enum.unique
class LocationDirection(enum.Enum):
    UP = Location(0, -1)
    RIGHT = Location(1, 0)
    DOWN = Location(0, 1)
    LEFT = Location(-1, 0)


DIRECTION: dict[str, LocationDirection] = {
    "^": LocationDirection.UP,
    ">": LocationDirection.RIGHT,
    "v": LocationDirection.DOWN,
    "<": LocationDirection.LEFT,
}


@dataclasses.dataclass(slots=True)
class GridLocation:
    location: Location
    location_type: LocationType

    @property
    def label(self) -> str:
        match self.location_type:
            case LocationType.ROBOT:
                return LocationType.ROBOT.value
            case LocationType.EMPTY:
                return LocationType.EMPTY.value
            case LocationType.BOX:
                return LocationType.BOX.value
            case LocationType.BOX_LEFT:
                return LocationType.BOX_LEFT.value
            case LocationType.BOX_RIGHT:
                return LocationType.BOX_RIGHT.value
            case LocationType.WALL:
                return LocationType.WALL.value
            case LocationType.OUT_OF_BOUNDS:
                return LocationType.OUT_OF_BOUNDS.value
            case _:
                raise ValueError(f"Invalid location type: {self.location_type}")

    # @property
    # def can_move(self) -> bool:
    #     return self.location_type in (LocationType.ROBOT, LocationType.BOX)

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
    robot_location: typing.Optional[Location] = None

    def add_grid_location(self, grid_location: GridLocation) -> None:
        if (grid_location.x, grid_location.y) in self.grid_locations:
            raise ValueError("Grid location is already occupied")

        if grid_location.location_type in (
            LocationType.ROBOT,
            LocationType.BOX,
            LocationType.WALL,
            LocationType.BOX_LEFT,
            LocationType.BOX_RIGHT,
        ):
            self.grid_locations[(grid_location.x, grid_location.y)] = grid_location
            if grid_location.location_type == LocationType.ROBOT:
                self.robot_location = grid_location.location
        self.update_max_values(grid_location.location)

        return None

    def remove_grid_location(self, grid_location: GridLocation) -> None:
        if (grid_location.x, grid_location.y) in self.grid_locations:
            del self.grid_locations[(grid_location.x, grid_location.y)]
            if grid_location.location_type == LocationType.ROBOT:
                self.robot_location = None

        return None

    def get_grid_location(self, location: Location) -> GridLocation:
        if not self.location_in_grid(location):
            return GridLocation(location, LocationType.OUT_OF_BOUNDS)
        grid_location = self.grid_locations.get(
            (location.x, location.y), GridLocation(location, LocationType.EMPTY)
        )

        return grid_location
    
    def gps_score(self) -> int:
        score = 0
        for grid_location in self.grid_locations.values():
            if grid_location.location_type == LocationType.BOX:

                score += 100 * grid_location.y + grid_location.x

        return score

    # def get_row(
    #     self,
    #     y_index: int,
    #     include_blanks: bool = True,
    #     x_start: typing.Optional[int] = None,
    #     x_end: typing.Optional[int] = None,
    # ) -> list[GridLocation]:
    #     row: list[GridLocation] = []
    #     x_start = 0 if x_start is None else x_start
    #     x_end = self.max_x_location if x_end is None else x_end
    #     for x_index in range(x_start, x_end + 1):
    #         location = Location(x_index, y_index)
    #         grid_location = self.get_grid_location(location)
    #         if not include_blanks and grid_location.location_type == LocationType.EMPTY:
    #             continue
    #         row.append(grid_location)
    #     return row

    # def get_column(
    #     self,
    #     x_index: int,
    #     include_blanks: bool = True,
    #     y_start: typing.Optional[int] = None,
    #     y_end: typing.Optional[int] = None,
    # ) -> list[GridLocation]:
    #     column: list[GridLocation] = []
    #     y_start = 0 if y_start is None else y_start
    #     y_end = self.max_y_location if y_end is None else y_end
    #     for y_index in range(y_start, y_end + 1):
    #         location = Location(x_index, y_index)
    #         grid_location = self.get_grid_location(location)
    #         if not include_blanks and grid_location.location_type == LocationType.EMPTY:
    #             continue
    #         column.append(grid_location)
    #     return column

    # def get_next_location_type_grid_location(
    #     self,
    #     location: Location,
    #     location_direction: LocationDirection,
    #     location_type: LocationType,
    # ) -> typing.Optional[GridLocation]:
    #     while True:
    #         location = location.neighbour_location(location_direction)
    #         grid_location = self.get_grid_location(location)
    #         print(
    #             f"Grid location: {grid_location} {grid_location.location_type == location_type}"
    #         )
    #         if grid_location.location_type == location_type:
    #             return grid_location
    #         elif grid_location.location_type == LocationType.OUT_OF_BOUNDS:
    #             return None

    def update_max_values(self, location: Location) -> None:
        self.max_x_location = max(self.max_x_location, location.x)
        self.max_y_location = max(self.max_y_location, location.y)

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


def create_grid(data: typing.Iterator[str]) -> tuple[Grid, typing.Iterator[str]]:
    grid = Grid()
    found_blank_line = False
    for y_index, line in enumerate(data):
        for x_index, character in enumerate(line):
            location = Location(x_index, y_index)
            match character:
                case LocationType.EMPTY.value:
                    continue
                case LocationType.ROBOT.value:
                    location_type = LocationType.ROBOT
                    grid.robot_location = location
                case LocationType.BOX.value:
                    location_type = LocationType.BOX
                case LocationType.WALL.value:
                    location_type = LocationType.WALL
                case LocationType.SPLITTER.value:
                    found_blank_line = True
                    break
                case _:
                    raise ValueError(f"Invalid character: {character}")
            grid_location = GridLocation(location, location_type)
            grid.add_grid_location(grid_location)

        if found_blank_line:
            break

    return grid, data

def create_grid_new(data: typing.Iterator[str], wide_warehouse: bool = False) -> tuple[Grid, typing.Iterator[str]]:
    grid = Grid()
    found_blank_line = False
    for y_index, line in enumerate(data):
        x_index = 0
        # for x_index, character in enumerate(line):
        for character in line:
            location = Location(x_index, y_index)
            new_grid_locations: list[GridLocation] = []
            match character:
                case LocationType.EMPTY.value if not wide_warehouse:
                    x_index += 1
                    continue
                case LocationType.EMPTY.value if wide_warehouse:
                    x_index += 2
                    continue
                case LocationType.ROBOT.value if not wide_warehouse:
                    new_grid_locations.append(GridLocation(location, LocationType.ROBOT))
                    x_index += 1
                    grid.robot_location = location
                case LocationType.ROBOT.value if wide_warehouse:
                    new_grid_locations.append(GridLocation(location, LocationType.ROBOT))
                    x_index += 2
                    grid.robot_location = location
                case LocationType.BOX.value if not wide_warehouse:
                    new_grid_locations.append(GridLocation(location, LocationType.BOX))
                    x_index += 1
                case LocationType.BOX.value if wide_warehouse:
                    new_grid_locations.append(GridLocation(location, LocationType.BOX_LEFT))
                    x_index += 1
                    location = Location(x_index, y_index)
                    new_grid_locations.append(GridLocation(location, LocationType.BOX_RIGHT))
                    x_index += 1
                case LocationType.WALL.value if not wide_warehouse:
                    new_grid_locations.append(GridLocation(location, LocationType.WALL))
                    x_index += 1
                case LocationType.WALL.value if wide_warehouse:
                    new_grid_locations.append(GridLocation(location, LocationType.WALL))
                    x_index += 1
                    location = Location(x_index, y_index)
                    new_grid_locations.append(GridLocation(location, LocationType.WALL))
                    x_index += 1
                case LocationType.SPLITTER.value:
                    found_blank_line = True
                    break
                case _:
                    raise ValueError(f"Invalid character: {character}")

            for grid_location in new_grid_locations:
                grid.add_grid_location(grid_location)


        if found_blank_line:
            break

    return grid, data

@dataclasses.dataclass
class Movements:
    movement_lines: list[str] = dataclasses.field(default_factory=list)

    def add_movement_line(self, movement_line: str) -> None:
        self.movement_lines.append(movement_line)

    def yield_movements(self) -> typing.Iterator[LocationDirection]:
        for movements in self.movement_lines:
            for movement in movements:
                location_direction = DIRECTION[movement]
                # print(f"Move {movement}:")
                yield location_direction


def create_movements(data: typing.Iterator[str]) -> Movements:
    movements = Movements()
    for line in data:
        if not line:
            continue
        movements.add_movement_line(line)

    return movements


@dataclasses.dataclass
class RobotMovement:
    grid: Grid = dataclasses.field(default_factory=Grid)

    def move_robot(self, location_direction: LocationDirection) -> None:
        robot_location = self.grid.robot_location
        if not robot_location:
            raise ValueError("No robot location found")

        current_location = robot_location
        locations_to_move: list[Location] = [current_location]
        while True:
            current_location = current_location.neighbour_location(location_direction)
            grid_location = self.grid.get_grid_location(current_location)
            match grid_location.location_type:
                case LocationType.WALL:
                    return
                case LocationType.BOX:
                    locations_to_move.append(current_location)
                case LocationType.EMPTY:
                    break

        for location in locations_to_move[::-1]:
            grid_location = self.grid.get_grid_location(location)
            self.grid.remove_grid_location(grid_location)
            match location_direction:
                case LocationDirection.UP:
                    new_location = Location(grid_location.x, grid_location.y - 1)
                case LocationDirection.DOWN:
                    new_location = Location(grid_location.x, grid_location.y + 1)
                case LocationDirection.LEFT:
                    new_location = Location(grid_location.x - 1, grid_location.y)
                case LocationDirection.RIGHT:
                    new_location = Location(grid_location.x + 1, grid_location.y)
            grid_location.location = new_location
            self.grid.add_grid_location(grid_location)

    # def move_robot_push_to_wall(
    #     self, location_direction: LocationDirection, to_location_type: LocationType
    # ) -> None:
    #     robot_location = self.grid.robot_location
    #     if not robot_location:
    #         raise ValueError("No robot location found")
    #     to_grid_location = self.grid.get_next_location_type_grid_location(
    #         robot_location, location_direction, to_location_type
    #     )
    #     if not to_grid_location:
    #         print(f"No {to_location_type.value} location found")
    #         return

    #     match location_direction:
    #         case LocationDirection.LEFT:
    #             grid_locations = self.grid.get_row(
    #                 robot_location.y,
    #                 include_blanks=False,
    #                 x_start=to_grid_location.x,
    #                 x_end=robot_location.x,
    #             )
    #             current_x = to_grid_location.x + 1
    #             for grid_location in grid_locations[1:]:
    #                 if grid_location.x != current_x:
    #                     self.grid.remove_grid_location(grid_location)
    #                     new_location = Location(current_x, robot_location.y)
    #                     grid_location.location = new_location
    #                     self.grid.add_grid_location(grid_location)
    #                 current_x += 1
    #         case LocationDirection.RIGHT:
    #             grid_locations = self.grid.get_row(
    #                 robot_location.y,
    #                 include_blanks=False,
    #                 x_start=robot_location.x,
    #                 x_end=to_grid_location.x,
    #             )
    #             current_x = to_grid_location.x - 1
    #             for grid_location in grid_locations[-2::-1]:
    #                 if grid_location.x != current_x:
    #                     self.grid.remove_grid_location(grid_location)
    #                     new_location = Location(current_x, robot_location.y)
    #                     grid_location.location = new_location
    #                     self.grid.add_grid_location(grid_location)
    #                 current_x -= 1
    #         case LocationDirection.UP:
    #             grid_locations = self.grid.get_column(
    #                 robot_location.x,
    #                 include_blanks=False,
    #                 y_start=to_grid_location.y,
    #                 y_end=robot_location.y,
    #             )
    #             print(grid_locations)
    #             current_y = to_grid_location.y + 1
    #             for grid_location in grid_locations[1:]:
    #                 if grid_location.y != current_y:
    #                     self.grid.remove_grid_location(grid_location)
    #                     new_location = Location(robot_location.x, current_y)
    #                     grid_location.location = new_location
    #                     self.grid.add_grid_location(grid_location)
    #                 current_y += 1
    #         case LocationDirection.DOWN:
    #             grid_locations = self.grid.get_column(
    #                 robot_location.x,
    #                 include_blanks=False,
    #                 y_start=robot_location.y,
    #                 y_end=to_grid_location.y,
    #             )
    #             current_y = to_grid_location.y - 1
    #             for grid_location in grid_locations[-2::-1]:
    #                 if grid_location.y != current_y:
    #                     self.grid.remove_grid_location(grid_location)
    #                     new_location = Location(robot_location.x, current_y)
    #                     grid_location.location = new_location
    #                     self.grid.add_grid_location(grid_location)
    #                 current_y -= 1


def part_one() -> int:
    data = yield_data(FILENAME)
    grid, data = create_grid(data)
    movements = create_movements(data)
    # print("Initial state:")
    # print(grid)

    robot_movement = RobotMovement(grid)
    for movement in movements.yield_movements():
        robot_movement.move_robot(movement)

        # print(grid)
        # print()
    # print(grid)
    return grid.gps_score()


def part_two() -> int:
    data = yield_data(TEST_FILENAME)
    grid, data = create_grid_new(data, True)
    movements = create_movements(data)
    print("Initial state:")
    print(grid)

    return 0


def main() -> None:
    # print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
