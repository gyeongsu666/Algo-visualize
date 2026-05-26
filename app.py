from flask import Flask, jsonify, render_template, request

from algorithms import run_algorithm, run_structure_action, serialize_algorithms


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", algorithms=serialize_algorithms())


@app.route("/compare")
def compare():
    return render_template("compare.html", algorithms=serialize_algorithms())


@app.route("/input")
def input_page():
    return render_template("input.html", algorithms=serialize_algorithms())


@app.post("/api/run")
def run_visualization():
    payload = request.get_json(silent=True) or {}
    key = (payload.get("algorithmKey") or "").strip()
    raw_input = payload.get("rawInput") or ""

    if not key:
        return jsonify({"ok": False, "error": "알고리즘 키가 비어 있습니다."}), 400

    try:
        result = run_algorithm(key, raw_input)
    except KeyError:
        return jsonify({"ok": False, "error": "지원하지 않는 알고리즘입니다."}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, **result})


@app.post("/api/structure-action")
def run_structure_visualization():
    payload = request.get_json(silent=True) or {}
    key = (payload.get("algorithmKey") or "").strip()
    action = (payload.get("action") or "").strip()
    raw_value = payload.get("value") or ""
    structure_state = payload.get("structureState") or {}

    if not key or not action:
        return jsonify({"ok": False, "error": "자료구조 키 또는 동작이 비어 있습니다."}), 400

    try:
        result = run_structure_action(key, structure_state, action, raw_value)
    except KeyError:
        return jsonify({"ok": False, "error": "지원하지 않는 자료구조입니다."}), 404
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    return jsonify({"ok": True, **result})


if __name__ == "__main__":
    app.run(debug=True)
