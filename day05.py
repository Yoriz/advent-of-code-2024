from typing import Iterator
import dataclasses
from collections import Counter


FILENAME = "day05_data.txt"


def yield_data(filename: str) -> Iterator[str]:
    with open(file=filename, mode="r") as read_file:
        for line in read_file:
            yield line.strip()


Pages = list[int]


def middle_page_number(pages: Pages) -> int:
    middle_index = len(pages) // 2
    return pages[middle_index]


@dataclasses.dataclass
class UpdateRule:
    number_before: int
    number_after: int

    def rule_applies(self, update: "Update") -> bool:
        return self.number_before in update.pages and self.number_after in update.pages

    def update_passes_rule(self, update: "Update") -> bool:
        after_pages = update.pages_after_page(self.number_before)
        return self.number_after in after_pages


@dataclasses.dataclass
class Update:
    pages: Pages = dataclasses.field(default_factory=list)

    def pages_after_page(self, page: int) -> Pages:
        page_index = self.pages.index(page)
        return self.pages[page_index + 1 :]

    def middle_page_number(self) -> int:
        return middle_page_number(self.pages)


@dataclasses.dataclass
class SaftyManual:
    update_rules: list[UpdateRule] = dataclasses.field(default_factory=list)
    updates: list[Update] = dataclasses.field(default_factory=list)
    fixed_updates: list[Update] = dataclasses.field(default_factory=list)

    def updates_in_correct_order(self) -> list[Update]:
        correct_update: list[Update] = []
        for update in self.updates:
            for update_rule in self.update_rules:
                if update_rule.rule_applies(update):
                    if not update_rule.update_passes_rule(update):
                        break
            else:
                correct_update.append(update)
        return correct_update

    def updates_not_in_correct_order(self) -> list[Update]:
        correct_updates = self.updates_in_correct_order()
        return [update for update in self.updates if update not in correct_updates]

    def fix_updates(self) -> None:
        for update in self.updates_not_in_correct_order():
            self.fix_update(update)

    def fix_update(self, update: Update) -> None:
        page_after_counter = Counter()
        for page in update.pages:
            for update_rule in self.update_rules:
                if update_rule.rule_applies(update):
                    if update_rule.number_before == page:
                        page_after_counter[update_rule.number_before] += 1

        fixed_pages = [page for page, _ in page_after_counter.most_common()]
        for page in update.pages:
            if not page in fixed_pages:
                fixed_pages.append(page)
                break

        self.fixed_updates.append(Update(pages=fixed_pages))


def create_safty_manual(data: Iterator[str]) -> SaftyManual:
    found_splitter: bool = False
    safty_manual = SaftyManual()
    for line in data:
        if not found_splitter and line == "":
            found_splitter = True
            continue

        if not found_splitter:
            before, after = map(int, line.split("|"))
            update_rule = UpdateRule(number_before=before, number_after=after)
            safty_manual.update_rules.append(update_rule)
        else:
            update = Update(pages=list(map(int, line.split(","))))
            safty_manual.updates.append(update)

    return safty_manual


def part_one() -> int:
    data = yield_data(FILENAME)
    safty_manual = create_safty_manual(data)
    score = 0
    for update in safty_manual.updates_in_correct_order():
        score += update.middle_page_number()

    return score


def part_two() -> int:
    data = yield_data(FILENAME)
    safty_manual = create_safty_manual(data)
    safty_manual.fix_updates()
    score = 0
    for update in safty_manual.fixed_updates:
        score += update.middle_page_number()

    return score


def main() -> None:
    print(f"Part one: {part_one()}")
    print(f"Part two: {part_two()}")


if __name__ == "__main__":
    main()
