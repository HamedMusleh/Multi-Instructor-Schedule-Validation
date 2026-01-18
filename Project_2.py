class Instructor:
    def __init__(self, id, f_name, l_name):
        self.id = id
        self.f_name = f_name
        self.l_name = l_name
        self.items = []
    def __str__(self):
        return f'Instructor {self.id}: {self.f_name} {self.l_name}'

    def add_item(self, item):
        if item.day not in {"S", "M", "T", "W", "Th"}:
            raise ValueError("Invalid day")
        self.items.append(item)


class ScheduleItem:
    def __init__(self, day, time_range, code):
        self.day = day              # S, M, T, W, Th
        self.time_range = time_range
        self.code = code            # ENCS334 or OH

    def is_office_hour(self):
        return self.code == "OH"

    def is_teaching(self):
        return self.code != "OH"

class TimeRange:
    def __init__(self, start, end):
        self.start = start      #min
        self.end = end

    def duration_hours(self):
        return (self.end - self.start) / 60

    def overlaps(self, other):
        return self.start < other.end and other.start < self.end



def read_Inst(filename):
    instructors = []
    current = None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if "," in line and "|" not in line:
                ins_id, f_name, l_name = [x.strip() for x in line.split(",")]
                current = Instructor(ins_id, f_name, l_name)
                instructors.append(current)

            elif "|" in line and current is not None:
                parse_schedule_line(line, current)

    return instructors


def read_codes(filename):
    """
    Reads valid course/lab codes from a text file (one code per line).
    Returns a set of codes.
    """
    codes = set()
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            code = line.strip()
            if code:               # ignore empty lines
                codes.add(code)
    return codes

def check_valid_codes(schedule_lines, valid_codes):
    for line in schedule_lines:
        right = line.split("|")[1]     # everything after day

        parts = right.split(";") # split all activity base on ( ; )

        for p in parts:
            code = p.strip().split("]")[1]  # extract code

            if code not in valid_codes:
                if code == "OH":
                    continue
                print("Invalid course/lab code:", code)
                exit(1)



def parse_schedule_line(line, instructor):
    day, right = line.split("|")
    day = day.strip()

    activities = right.split(";")

    for act in activities:
        act = act.strip()
        if not act:
            continue

        # liek = [9:30–11]ENCS432
        time_part, code = act.split("]")
        time_part = time_part.strip("[")
        start, end = time_part.replace("–", "-").split("-")

        start_min = time_to_minutes(start.strip())
        end_min = time_to_minutes(end.strip())

        # like 12-1
        if end_min <= start_min:
            end_min += 12 * 60

        tr = TimeRange(start_min, end_min)
        item = ScheduleItem(day, tr, code.strip())

        instructor.add_item(item)

def time_to_minutes(t):
    if ":" in t:
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    return int(t) * 60


def read_pref(filename):
    prefs = {}

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            ins_id, right = line.split(":")
            ins_id = ins_id.strip()

            codes = set()
            for c in right.split(";"):
                c = c.strip()
                if c:
                    codes.add(c)

            prefs[ins_id] = codes

    return prefs

if __name__ == "__main__":
    valid_codes = read_codes("valid_codes.txt")
    Instructor = read_Inst("instructors_schedule.txt")
    preferences = read_pref("instructor_preferences.txt")

    for ins in Instructor:
        print(ins)
        prefs = preferences.get(ins.id, set())
        for item in ins.items:
            if item.is_teaching() and item.code not in prefs:
                print(f"Preference violation for {ins.id}: {item.code}")
        for item in ins.items:
            print(item.day, item.code, item.time_range.start, item.time_range.end)





