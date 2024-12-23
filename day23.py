import cProfile
import typing
import dataclasses


FILENAME = "day23_data.txt"


def yield_data(filename: str) -> typing.Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


@dataclasses.dataclass
class Network:
    computers: set[str] = dataclasses.field(default_factory=set)
    connections: set[frozenset[str]] = dataclasses.field(default_factory=set)
    inter_connections: dict[int, set[frozenset[str]]] = dataclasses.field(
        default_factory=dict
    )
    _index: int = 0

    def create_first_inter_connections(self):
        self._index = 2
        self.inter_connections[self._index] = self.connections

    def add_level_of_inter_connections(self):
        new_inter_connections: set[frozenset[str]] = set()
        for computer in self.computers:
            for inter_connection in self.inter_connections[self._index]:
                if computer in inter_connection:
                    continue
                for inter_computer in inter_connection:
                    if not set((computer, inter_computer)) in self.connections:
                        break
                else:
                    new_inter_connection = frozenset((*inter_connection, computer))
                    new_inter_connections.add(new_inter_connection)

        self._index += 1
        self.inter_connections[self._index] = new_inter_connections

    def add_all_levels_of_inter_connections(self):
        while True:
            self.add_level_of_inter_connections()
            print(f"Added level: {self._index}")
            if len(self.inter_connections[self._index]) == 0:
                break


def filter_starts_with_t(items: set[frozenset[str]]) -> set[frozenset[str]]:
    return {fset for fset in items if any(item.startswith("t") for item in fset)}


def create_network(data: typing.Iterator[str]) -> Network:
    network = Network()
    for line in data:
        computers = line.split("-")
        for computer in computers:
            network.computers.add(computer)
        network.connections.add(frozenset(computers))

    return network


def part_one() -> int:
    data = yield_data(FILENAME)
    network = create_network(data)
    network.create_first_inter_connections()
    network.add_level_of_inter_connections()
    current_index = network._index
    connections = network.inter_connections[current_index]
    filtered_connections = filter_starts_with_t(connections)
    return len(filtered_connections)


def part_two() -> str:
    data = yield_data(FILENAME)
    network = create_network(data)
    network.create_first_inter_connections()
    network.add_all_levels_of_inter_connections()
    current_index = network._index - 1
    connections = network.inter_connections[current_index]
    print(f"{connections=}")
    password = ",".join(sorted(list(connections)[0]))
    return password


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")
    return None


if __name__ == "__main__":
    main()
