import sqlite3


class MeetingNotes:
    def __init__(self) -> None:
        self.connection = sqlite3.connect('writers.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS writers(
            id_meeting INTEGER PRIMARY KEY,
            name TEXT,
            day TEXT,
            time DATETIME
        )
        """
        )
        self.connection.commit()

    def add_writer(self, name, day, time) -> None:
        self.cursor.execute('INSERT INTO writers VALUES(NOT NULL,?,?,?);', (name, day, time))
        self.connection.commit()

    def get_table(self) -> list:
        result = self.cursor.execute('SELECT * FROM writers ORDER BY time DESC;').fetchall()
        return result

    def update(self, id_meeting, name, day, time) -> None:
        self.cursor.execute(
            'UPDATE writers SET name=?, day=?, time=? WHERE id_meeting=?;',
            (name, day, time, id_meeting),
        )
        self.connection.commit()

    def delete(self, id_meeting) -> None:
        self.cursor.execute('DELETE FROM writers WHERE id_meeting=?;', (id_meeting,))
        self.connection.commit()
