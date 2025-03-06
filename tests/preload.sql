INSERT INTO command (name, scpi, delay) VALUES
    ('name_1', '*IDN?', 0.0);
INSERT INTO instrument (name, host, port) VALUES
    ('name_1', '127.0.0.1', 5025);
INSERT INTO measurement (name, precision, units, lower_limit, upper_limit) VALUES
    ('name_1', 3, 'units_1', 0.0, 1.0);
INSERT INTO part (name, global_trade_item_number, number, revision) VALUES
    ("part_1", "gtin_1", "number_1", "A");
INSERT INTO phase (name) VALUES
    ("name_1");
INSERT INTO procedure (name, pid) VALUES
    ("name_1", "pid_1");
INSERT INTO recipe (command_id, instrument_id, measurement_id, part_id, procedure_id, phase_id) VALUES
    (1, 1, 1, 1, 1);
