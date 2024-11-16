import pytest

from lib.util.csv_lookup import CSVLookup


class TestCsvHandler:

    @pytest.mark.parametrize("test_input,expected", [
        (20.59, (20, 17.28)),
        (35, (34, 37.54)),
        (4, (3, 5.99)),
        (17.01, (17, 14.47)),
        (15.99, (15, 12.85))
    ])
    def test_closest_value(self, test_input, expected):
        csv_env_table = CSVLookup("../doc/waterdampspanning.csv")

        # act
        target_value = csv_env_table.get_closest_value(test_input)

        # arrange
        assert target_value == expected