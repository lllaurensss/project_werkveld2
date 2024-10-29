import csv


class CSVLookup:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lookup_table = {}
        self._load_data()

    def _load_data(self):
        with open(self.file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Skip header
            next(reader)
            for row in reader:
                gm3, temp = float(row[0]), int(row[1])
                self.lookup_table[temp] = gm3

    def get_closest_value(self, target_temperature):
        """Finds and returns the gm3 value for the closest temperature."""
        closest_temp = min(self.lookup_table.keys(), key=lambda temp: abs(temp - target_temperature))
        return self.lookup_table[closest_temp], closest_temp
