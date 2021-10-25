"""
James Gough coding challenge.
24/10/2021

Robots module that interprets JSON from a text file in order to provide the final coordinates of the robot's position
and bearing
"""
import json
from itertools import cycle
import re
import sys
import logging


class TextToDictConverter:
    """
    Extracts the instructions from the .txt file and converts them to valid Python dictionaries.
    """

    def __init__(self, _file_name: str):
        self.file_name = _file_name

        self.json_text = None
        self.parsed_data = {}

    def read_file(self):
        """
        Simply reads the input text file as a string.
        :return:
        """
        with open(self.file_name) as file:
            self.json_text = file.read()

    def convert_to_list_of_dicts(self):
        """
        Converts the list of json strings into dictionaries.
        :return:
        """
        self.json_text = self.json_text.split("\n")
        self.json_text = [i for i in self.json_text if i]
        self.parsed_data = [json.loads(i) for i in self.json_text]

    def convert_file_to_json(self):
        """
        Runs all class methods and outputs parsed data.
        :return:
        """
        self.read_file()
        self.convert_to_list_of_dicts()
        return self.parsed_data


class Robot:
    """
    Robot object that updates the position of the robot based on movement data received.
    Movement is updated through a class variable to allow for different bearing, axis and movement options.
    """

    bearings = ["north", "east", "south", "west"]
    movement_num_ref_list = list(range(len(bearings)))

    bearing_to_num_dict = dict(zip(bearings, movement_num_ref_list))
    turn_right = cycle(movement_num_ref_list)
    turn_left = cycle(movement_num_ref_list[::-1])

    movement_lookup_dict = {
        0: {"bearing": "north", "axis": "y", "movement": 1},
        1: {"bearing": "east", "axis": "x", "movement": 1},
        2: {"bearing": "south", "axis": "y", "movement": -1},
        3: {"bearing": "west", "axis": "x", "movement": -1},
    }

    def __init__(self, new_robot_json: dict):
        self.new_robot_json = new_robot_json

        self.current_robot_position = None
        self.bearing = None

        self.bearing_num = int()
        self.movement_key = int()
        self.y = int()
        self.x = int()

        self.robot_output_dict = dict()

    def add_initial_data(self):
        self.current_robot_position = self.new_robot_json["position"]
        self.x = self.current_robot_position["x"]
        self.y = self.current_robot_position["y"]

        self.bearing = self.new_robot_json["bearing"]
        self.bearing_num = self.bearing_to_num_dict[self.bearing]

    def cycle_to_initial_bearing_num(self):
        for i in self.turn_right:
            if i == self.bearing_num:
                break
        for i in self.turn_left:
            if i == self.bearing_num:
                break

    def change_direction(self, movement):
        """The momvement_key uses the movement_lookup_dict to determine how to update the robot's position"""
        direction = movement.split("-")[-1]
        if direction == "right":
            self.bearing_num = next(self.turn_right)
        else:
            self.bearing_num = next(self.turn_left)

    def move_forward(self):
        """Updates the coordinates via the movement_lookup_dict"""
        lookup_data = self.movement_lookup_dict[self.bearing_num]
        movement_value = lookup_data["movement"]
        axis = lookup_data["axis"]
        if axis == "x":
            self.x += movement_value
        else:
            self.y += movement_value

    def update_movement(self, move_command: dict):
        """
        Updates the current_status with the data contained in the move_command.
        :return:
        """

        movement = move_command.get("movement")
        if re.fullmatch(r"turn-\w+", movement):
            self.change_direction(movement)
        elif movement == "move-forward":
            self.move_forward()

    def provide_final_position(self):
        self.robot_output_dict = {
            "type": "robot",
            "position": {"x": self.x, "y": self.y},
            "bearing": self.movement_lookup_dict[self.bearing_num]["bearing"]
        }
        return self.robot_output_dict


class Asteroid:
    """
    Utilises the Robot and TextToDictConverter classes to loop through the entire text, allowing for multiple
    instances of Robot on the asteroid.
    """

    def __init__(self, new_asteroid_dict: dict):
        self.new_asteroid_dict = new_asteroid_dict
        self.asteroid_size_x = self.new_asteroid_dict["size"]["x"]
        self.asteroid_size_y = self.new_asteroid_dict["size"]["y"]

        self.asteroid_boundary = dict()

        self.robot_final_positions_list = []

        self.asteroid_boundary_warning = False

    def construct_asteroid_boundary(self):
        self.asteroid_boundary = {
            "x": {"max": self.asteroid_size_x, "min": self.asteroid_size_x * -1},
            "y": {"max": self.asteroid_size_y, "min": self.asteroid_size_y * -1}
        }

    def check_robot_within_boundary(self, _x, _y):
        if any([
            abs(_x) > self.asteroid_size_x,
            abs(_y) > self.asteroid_size_y
        ]):
            self.asteroid_boundary_warning = True


class AsteroidRobotDataParser:

    def __init__(self, _file_name):
        self.file_name = _file_name

        self.converted_data = []

        self.current_asteroid = None
        self.current_robot = None

        self.robot_output_data = []

        self.boundary_warning = False

    def convert_text_to_dict(self):
        text_to_dict = TextToDictConverter(self.file_name)
        self.converted_data = text_to_dict.convert_file_to_json()

    def initialise_new_robot(self, data_line):
        self.current_robot = Robot(data_line)
        self.current_robot.add_initial_data()
        self.current_robot.cycle_to_initial_bearing_num()

    def parse_data(self, data_line):
        data_type = data_line["type"]
        if data_type == "asteroid":
            self.current_asteroid = Asteroid(data_line)
        elif data_type == "new-robot":
            if self.current_robot:
                self.robot_output_data.append(self.current_robot.provide_final_position())
            self.initialise_new_robot(data_line)
        elif data_type == "move":
            self.current_robot.update_movement(data_line)
            self.current_asteroid.check_robot_within_boundary(self.current_robot.x, self.current_robot.y)
            if self.current_asteroid.asteroid_boundary_warning:
                logging.warning(f"""Robot has gone beyond the bounds of the asteroid! 
                Current coordinates are: {self.current_robot.x}, {self.current_robot.y}
                """)

    def print_out_robot_output_data(self):
        for data in self.robot_output_data:
            print(data)

    def run_data_parser(self):
        self.convert_text_to_dict()
        for data_line in self.converted_data:
            self.parse_data(data_line)
        self.robot_output_data.append(self.current_robot.provide_final_position())
        self.print_out_robot_output_data()


if __name__ == "__main__":
    file_name = sys.argv[-1]
    if not re.fullmatch(r".*.txt", file_name):
        file_name = "instructions"
    file_name = file_name.split(".")[0]
    data_parser = AsteroidRobotDataParser(file_name)
    data_parser.run_data_parser()
