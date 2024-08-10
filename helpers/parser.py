import json

from abc import ABC, abstractmethod


class Parser(ABC):
    @staticmethod
    @abstractmethod
    def run(file):
        pass


class ParseJson(Parser):
    @staticmethod
    def run(file) -> list | None:
        try:
            file_data = file.read().decode('utf-8')
            unescaped_json = file_data.replace('\\"', '"')
            json_data = json.loads(unescaped_json)
            if isinstance(json_data, list):
                return json_data
            else:
                raise ValueError("JSON data should be a list of objects.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {str(e)}")
