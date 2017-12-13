import csv


def csv_read(case: str, delimiter=',', data_start_row: int=1, header_map: dict=None) -> list:
    collected_data = []

    with open('data/' + case + '.csv', 'r', newline='') as csv_file:
        spam_reader = csv.reader(csv_file, delimiter=delimiter, quotechar='|')
        rows_list = list(spam_reader)
        if data_start_row > 0 and header_map is not None:
            header = rows_list[0]
            # header = [header_map[head] if head in header_map else head for i, head in enumerate(header)]
            for head, mapped in header_map.items():
                i = header.index(head)
                header[i] = mapped
        else:
            return rows_list
        for row in rows_list[data_start_row:]:
            collected_data.append({header[i]: value for i, value in enumerate(row)})

    return collected_data
