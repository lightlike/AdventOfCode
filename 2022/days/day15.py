from __future__ import annotations
from dataclasses import dataclass, field
import re
from typing import Iterator
from enum import Enum, unique
import math

from . import helper

@unique
class Block(Enum):
    sensor = 0
    beacon = 1
    nothing = 2

@dataclass
class Vector2D:
    x: int
    y: int

    @classmethod
    def from_tuple(cls: Vector2D, point: tuple[int, int]) -> Vector2D:
        return Vector2D(point[0], point[1])

    def __sub__(self: Vector2D, other: Vector2D) -> Vector2D:
        x = self.x - other.x
        y = self.y - other.y
        return Vector2D(x, y)

    def __add__(self: Vector2D, other: Vector2D) -> Vector2D:
        x = self.x + other.x
        y = self.y + other.y
        return Vector2D(x, y)

    def manhattan_distance(self: Vector2D):
        return abs(self.x) + abs(self.y)

    def __hash__(self: Vector2D) -> int:
        return hash((self.x, self.y))


@dataclass
class Graph:
    sensors: list[tuple[Vector2D, Vector2D, Vector2D]] = field(default_factory=list)
    min: Vector2D = None
    max: Vector2D = None

    def update_max_min(self: Graph, vector: Vector2D):
        if self.min is None or self.max is None:
            self.min = Vector2D(vector.x, vector.y)
            self.max = Vector2D(vector.x, vector.y)

        if self.min.x > vector.x:
            self.min.x = vector.x
        if self.min.y > vector.y:
            self.min.y = vector.y

        if self.max.x < vector.x:
            self.max.x = vector.x
        if self.max.y < vector.y:
            self.max.y = vector.y

    def append(self: Graph, sensor: Vector2D, beacon: Vector2D):
        self.sensors.append((sensor, beacon, beacon - sensor))
        self.update_max_min(sensor)
        self.update_max_min(beacon)

    def draw(self: Graph):
        grid: list[list[str]] = []
        y_offset = self.min.y * -1
        x_offset = self.min.x * -1

        for y in range(self.min.y + y_offset, self.max.y + y_offset + 1):
            grid.append([])
            for x in range(self.min.x + x_offset, self.max.x + x_offset + 1):
                grid[y].append('.')

        for sensor, beacon, diff in self.sensors:
            grid[sensor.y][sensor.x] = 'S'
            grid[beacon.y][beacon.x] = 'B'

        for y in range(len(grid)):
            for x in range(len(grid[0])):
                print(grid[y][x], end='')
            print('')

    @staticmethod
    def is_relevant(sensor: Vector2D, diff: Vector2D, target_y: int):
        if ((sensor.y <= target_y and sensor.y + diff.manhattan_distance() >= target_y)
                or (sensor.y >= target_y and sensor.y - diff.manhattan_distance() <= target_y)):
            return True
        else:
            return False

    def find_blocked_in_row(self: Graph, row: int, remove_beacons: bool = True) -> set[Vector2D]:
        result: list[Vector2D] = []
        for sensor, beacon, diff in self.sensors:
            if not Graph.is_relevant(sensor, diff, row):
                continue
            y_bias = 1 if sensor.y < row else -1
            number_of_points = abs(sensor.y + (diff.manhattan_distance() * y_bias) - row) * 2 + 1
            radius = int(number_of_points / 2)

            for x in range(sensor.x - radius, sensor.x + radius + 1):
                result.append(Vector2D(x, row))

        if remove_beacons:
            for sensor, beacon, diff in self.sensors:
                if beacon.y == row:
                    result.remove(Vector2D(beacon.x, row))

        return set(result)

    def generate_blocked_fields(self: Graph, p_min: Vector2D = Vector2D(-math.inf, -math.inf), p_max: Vector2D = Vector2D(math.inf, math.inf)) -> dict[Vector2D, Block]:
        result: dict[Vector2D, Block] = {}
        for sensor, beacon, diff in self.sensors:
            dist = diff.manhattan_distance()
            
            for x in range(max(sensor.x - dist, p_min.x), min(sensor.x + dist, p_max.x) + 1):
                bias = 1 if sensor.x < x else -1
                number_of_points = abs(sensor.x + (dist * bias) - x) * 2 + 1
                radius = int(number_of_points / 2)

                for y in range(max(sensor.y - radius, p_min.y), min(sensor.y + radius, p_max.y) + 1):
                    result[Vector2D(x, y)] = Block.nothing
            
            for y in range(max(sensor.y - dist, p_min.y), min(sensor.y + dist, p_max.y) + 1):
                bias = 1 if sensor.y < y else -1
                number_of_points = abs(sensor.y + (dist * bias) - y) * 2 + 1
                radius = int(number_of_points / 2)

                for x in range(max(sensor.x - radius, p_min.x), min(sensor.x + radius, p_max.x) + 1):
                    result[Vector2D(x, y)] = Block.nothing

        for sensor, beacon, diff in self.sensors:
            result[sensor] = Block.sensor
            result[beacon] = Block.beacon

        return result


def parse_input(file: Iterator[str]) -> Graph:
    graph = Graph()
    for line in file:
        found = re.findall(r'=-?[0-9]+', line)
        sensor = Vector2D(int(found[0][1:]), int(found[1][1:]))
        beacon = Vector2D(int(found[2][1:]), int(found[3][1:]))
        graph.append(sensor, beacon)

    return graph


def run():
    # Round 1
    print("Round 1:")

    file: Iterator[str] = helper.load_file("input/day15.txt")

    graph = parse_input(file)

    #result = graph.find_blocked_in_row(2000000)
    #print(f"Number of blocked spaces: {len(result)}")
    
    # Round 2
    print("Round 2:")

    p_min = Vector2D(0, 0)
    p_max = Vector2D(4000000, 4000000)

    result = graph.generate_blocked_fields(p_min, p_max)
    item = find_free(result, p_min.x, p_min.y, p_max.x, p_max.y)
    print(item)
    score = item.x * 4000000 + item.y
    #print(f"Free position in area: {result}")
    print(f"Score: {score}")

def find_free(items: dict, x_min: int, y_min: int, x_max: int, y_max: int):
    for x in range(x_min, x_max):
        for y in range(y_min, y_max):
            item = items.get(Vector2D(x, y), None)
            if item == None:
                return Vector2D(x, y)
