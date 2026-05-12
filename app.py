from flask import Flask, request, jsonify
from flask_cors import CORS
from ortools.sat.python import cp_model

app = Flask(__name__)
CORS(app)

# ─── Timetable Generator (OR-Tools CP-SAT) ────────────────────────────────────

def generate_timetable(teachers, subjects, rooms, slots_per_day=6, days=5, sections=None):
    model = cp_model.CpModel()

    days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"][:days]
    slots_list = [f"Period {i+1}" for i in range(slots_per_day)]
    all_slots = [(d, s) for d in days_list for s in slots_list]

    if not sections:
        sections = [{"name": "Section A"}]

    assign = {}
    for sec in sections:
        for t in teachers:
            for sub in subjects:
                if sub["teacher"] != t["name"]:
                    continue
                for r in rooms:
                    for d, sl in all_slots:
                        key = (sec["name"], t["name"], sub["name"], r["name"], d, sl)
                        safe = "_".join(k.replace(" ", "_").replace(".", "") for k in key)
                        assign[key] = model.NewBoolVar(f"a_{safe}")

    # C1: Teacher in one place per slot across all sections
    for t in teachers:
        for d, sl in all_slots:
            v = [assign[k] for k in assign if k[1] == t["name"] and k[4] == d and k[5] == sl]
            if v: model.AddAtMostOne(v)

    # C2: Room used once per slot
    for r in rooms:
        for d, sl in all_slots:
            v = [assign[k] for k in assign if k[3] == r["name"] and k[4] == d and k[5] == sl]
            if v: model.AddAtMostOne(v)

    # C3: Each section has at most one class per slot
    for sec in sections:
        for d, sl in all_slots:
            v = [assign[k] for k in assign if k[0] == sec["name"] and k[4] == d and k[5] == sl]
            if v: model.AddAtMostOne(v)

    # C4: Each subject gets required hours per section
    for sec in sections:
        for sub in subjects:
            t_name = sub["teacher"]
            required = sub.get("hours_per_week", 3)
            v = [assign[k] for k in assign if k[0] == sec["name"] and k[2] == sub["name"]]
            if v: model.Add(sum(v) == min(required, len(v)))

    model.Maximize(sum(assign.values()))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 15.0
    status = solver.Solve(model)

    section_timetables = {sec["name"]: {d: {sl: None for sl in slots_list} for d in days_list} for sec in sections}

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for key, var in assign.items():
            if solver.Value(var):
                sec_name, t_name, sub_name, r_name, d, sl = key
                section_timetables[sec_name][d][sl] = {"subject": sub_name, "teacher": t_name, "room": r_name}

    workload = {t["name"]: 0 for t in teachers}
    for sec_name, tt in section_timetables.items():
        for d in days_list:
            for sl in slots_list:
                e = tt[d][sl]
                if e: workload[e["teacher"]] = workload.get(e["teacher"], 0) + 1

    total = sum(1 for tt in section_timetables.values() for d in days_list for sl in slots_list if tt[d][sl])

    return {
        "timetable": section_timetables[sections[0]["name"]],
        "section_timetables": section_timetables,
        "sections": [s["name"] for s in sections],
        "days": days_list, "slots": slots_list,
        "workload": workload, "total_classes": total,
        "status": "optimal" if status == cp_model.OPTIMAL else "feasible" if status == cp_model.FEASIBLE else "infeasible",
        "clashes": 0 if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else -1
    }


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "SmartSchedule AI API", "version": "2.0", "status": "online"})

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    teachers = data.get("teachers", [])
    subjects = data.get("subjects", [])
    rooms = data.get("rooms", [])
    sections = data.get("sections", None)
    if not teachers or not subjects or not rooms:
        return jsonify({"error": "teachers, subjects, and rooms are required"}), 400
    result = generate_timetable(teachers, subjects, rooms,
                                data.get("slots_per_day", 6), data.get("days", 5), sections)
    return jsonify(result)

@app.route("/api/demo", methods=["GET"])
def demo():
    teachers = [{"name": "Dr. Priya"}, {"name": "Prof. Ramesh"}, {"name": "Ms. Kavitha"}, {"name": "Mr. Suresh"}]
    subjects = [
        {"name": "Mathematics",     "teacher": "Dr. Priya",    "hours_per_week": 5},
        {"name": "Physics",          "teacher": "Prof. Ramesh", "hours_per_week": 4},
        {"name": "Computer Science", "teacher": "Ms. Kavitha",  "hours_per_week": 4},
        {"name": "English",          "teacher": "Mr. Suresh",   "hours_per_week": 3},
    ]
    rooms = [{"name": "Room 101", "capacity": 60}, {"name": "Room 102", "capacity": 60}, {"name": "Lab 1", "capacity": 30}]
    sections = [{"name": "Section A"}, {"name": "Section B"}]
    return jsonify(generate_timetable(teachers, subjects, rooms, 6, 5, sections))

@app.route("/api/validate", methods=["POST"])
def validate():
    data = request.json
    timetable = data.get("timetable", {})
    clashes = []
    teacher_slots, room_slots = {}, {}
    for day, slots in timetable.items():
        for slot, entry in slots.items():
            if not entry: continue
            tk = (entry["teacher"], day, slot)
            rk = (entry["room"], day, slot)
            if tk in teacher_slots: clashes.append(f"Teacher clash: {entry['teacher']} on {day} {slot}")
            else: teacher_slots[tk] = True
            if rk in room_slots: clashes.append(f"Room clash: {entry['room']} on {day} {slot}")
            else: room_slots[rk] = True
    return jsonify({"clashes": clashes, "valid": len(clashes) == 0})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
