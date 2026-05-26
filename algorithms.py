from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any
import inspect
import math
import random
import re
import textwrap
import time


@dataclass(frozen=True)
class AlgorithmDefinition:
    key: str
    title: str
    category: str
    subcategory: str
    badge: str
    compare_text: str
    input_label: str
    input_description: str
    example: str
    python_code: list[str]
    renderer: str


def _normalize_text(raw: str) -> str:
    return (
        raw.replace("，", ",")
        .replace("、", ",")
        .replace("；", ";")
        .replace("｜", "|")
        .replace("→", ">")
        .replace("–", "-")
        .replace("—", "-")
        .replace("(", " ")
        .replace(")", " ")
        .replace("{", " ")
        .replace("}", " ")
        .replace("[", " ")
        .replace("]", " ")
        .replace("\n", " ")
        .strip()
    )


def _split_tokens(raw: str, pattern: str = r"[\s,]+") -> list[str]:
    normalized = _normalize_text(raw)
    return [token.strip() for token in re.split(pattern, normalized) if token.strip()]


def _split_numeric_or_string_list(raw: str) -> list[str]:
    normalized = _normalize_text(raw)
    if "," in normalized:
        return [token.strip() for token in normalized.split(",") if token.strip()]
    return [token.strip() for token in normalized.split() if token.strip()]


def _as_number(token: str) -> float:
    return float(token)


def _fmt(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def parse_number_list(raw: str) -> list[float]:
    stripped = raw.strip()
    # random:N 형식 — N개의 랜덤 정수를 생성
    if stripped.lower().startswith("random:"):
        try:
            count = int(stripped.split(":", 1)[1].strip())
        except ValueError as exc:
            raise ValueError("random:N 형식에서 N은 정수여야 합니다.") from exc
        if count < 1:
            raise ValueError("생성 개수는 1 이상이어야 합니다.")
        if count > 50:
            raise ValueError("생성 개수는 최대 50개까지 허용됩니다.")
        return [float(random.randint(1, 999)) for _ in range(count)]
    tokens = _split_numeric_or_string_list(raw)
    if not tokens:
        raise ValueError("숫자 목록이 비어 있습니다.")
    if len(tokens) > 50:
        raise ValueError("입력 값은 최대 50개까지 허용됩니다.")
    try:
        return [_as_number(token) for token in tokens]
    except ValueError as exc:
        raise ValueError("모든 값은 숫자여야 합니다.") from exc



def parse_search_payload(raw: str) -> dict[str, Any]:
    normalized = _normalize_text(raw)
    parts = [part.strip() for part in normalized.split("|") if part.strip()]
    if len(parts) != 2:
        raise ValueError("`목록 | 찾을 값` 형식으로 입력해 주세요.")
    values = parse_number_list(parts[0])
    try:
        target = float(parts[1])
    except ValueError as exc:
        raise ValueError("찾을 값은 숫자여야 합니다.") from exc
    return {"values": values, "target": target}


def parse_binary_search_payload(raw: str) -> dict[str, Any]:
    payload = parse_search_payload(raw)
    payload["values"] = sorted(payload["values"])
    return payload


def parse_stack_commands(raw: str) -> list[tuple[str, float | None]]:
    commands: list[tuple[str, float | None]] = []
    for line in [item.strip() for item in re.split(r"[;,\n]+", _normalize_text(raw)) if item.strip()]:
        parts = line.split()
        action = parts[0].lower()
        if action == "push":
            if len(parts) != 2:
                raise ValueError("push는 `push 숫자` 형식이어야 합니다.")
            commands.append(("push", float(parts[1])))
        elif action == "pop":
            if len(parts) != 1:
                raise ValueError("pop에는 추가 값이 필요하지 않습니다.")
            commands.append(("pop", None))
        else:
            raise ValueError("지원 명령은 push, pop 입니다.")
    if not commands:
        raise ValueError("명령 목록이 비어 있습니다.")
    return commands


def parse_queue_commands(raw: str) -> list[tuple[str, float | None]]:
    commands: list[tuple[str, float | None]] = []
    for line in [item.strip() for item in re.split(r"[;,\n]+", _normalize_text(raw)) if item.strip()]:
        parts = line.split()
        action = parts[0].lower()
        if action == "enqueue":
            if len(parts) != 2:
                raise ValueError("enqueue는 `enqueue 숫자` 형식이어야 합니다.")
            commands.append(("enqueue", float(parts[1])))
        elif action == "dequeue":
            if len(parts) != 1:
                raise ValueError("dequeue에는 추가 값이 필요하지 않습니다.")
            commands.append(("dequeue", None))
        else:
            raise ValueError("지원 명령은 enqueue, dequeue 입니다.")
    if not commands:
        raise ValueError("명령 목록이 비어 있습니다.")
    return commands



def parse_tree_edges(raw: str) -> dict[str, Any]:
    edges: list[tuple[str, str]] = []
    tokens = [item.strip() for item in _normalize_text(raw).split(",") if item.strip()]
    if not tokens:
        raise ValueError("트리 간선 입력이 비어 있습니다.")
    for token in tokens:
        if ">" not in token:
            raise ValueError("트리는 `부모>자식` 형식으로 입력해 주세요.")
        parent, child = [item.strip() for item in token.split(">", 1)]
        if not parent or not child:
            raise ValueError("트리 간선은 `부모>자식` 형식이어야 합니다.")
        edges.append((parent, child))
    return {"edges": edges}


def parse_binary_tree_level(raw: str) -> list[str | None]:
    tokens = _split_numeric_or_string_list(raw)
    if not tokens:
        raise ValueError("레벨 순회 값이 비어 있습니다.")
    result: list[str | None] = []
    for token in tokens:
        lowered = token.lower()
        result.append(None if lowered in {"null", "none", "_"} else token)
    return result


def parse_graph_payload(raw: str) -> dict[str, Any]:
    normalized = _normalize_text(raw)
    parts = [part.strip() for part in normalized.split("|") if part.strip()]
    if not parts:
        raise ValueError("그래프 입력이 비어 있습니다.")
    edge_text = parts[0]
    start = parts[1] if len(parts) > 1 else None
    edges: list[tuple[str, str]] = []
    for token in [item.strip() for item in edge_text.split(",") if item.strip()]:
        if "-" not in token:
            raise ValueError("그래프는 `A-B, A-C | 시작노드` 형식으로 입력해 주세요.")
        left, right = [item.strip() for item in token.split("-", 1)]
        if not left or not right:
            raise ValueError("간선은 `A-B` 형식이어야 합니다.")
        edges.append((left, right))
    if not edges:
        raise ValueError("그래프 간선이 비어 있습니다.")
    if start is None:
        start = edges[0][0]
    return {"edges": edges, "start": start}



def _tree_state_from_binary(values: list[str | None], highlight: list[int] | None = None) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    non_null_indices = {idx for idx, value in enumerate(values) if value is not None}
    if not non_null_indices:
        return {"nodes": [], "edges": []}
    width = 640
    vertical_gap = 84
    highlight = highlight or []
    for idx, value in enumerate(values):
        if value is None:
            continue
        level = int(math.log2(idx + 1))
        pos_in_level = idx - (2**level - 1)
        nodes_in_level = 2**level
        x = width / (nodes_in_level + 1) * (pos_in_level + 1)
        y = 56 + level * vertical_gap
        nodes.append({"id": idx, "label": _fmt(value), "x": x, "y": y, "highlight": idx in highlight})
        if idx > 0:
            parent = (idx - 1) // 2
            if parent in non_null_indices:
                edges.append({"from": parent, "to": idx})
    return {"nodes": nodes, "edges": edges}


def _tree_state_from_edges(edges: list[tuple[str, str]], highlight_nodes: list[str] | None = None) -> dict[str, Any]:
    if not edges:
        return {"nodes": [], "edges": []}
    parents = {child: parent for parent, child in edges}
    children: dict[str, list[str]] = {}
    labels = set()
    for parent, child in edges:
        labels.add(parent)
        labels.add(child)
        children.setdefault(parent, []).append(child)
    roots = [node for node in labels if node not in parents]
    root = roots[0] if roots else edges[0][0]
    levels: list[list[str]] = []
    queue = deque([(root, 0)])
    visited = set()
    while queue:
        node, depth = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        if len(levels) <= depth:
            levels.append([])
        levels[depth].append(node)
        for child in children.get(node, []):
            queue.append((child, depth + 1))
    nodes: list[dict[str, Any]] = []
    highlight_nodes = highlight_nodes or []
    for depth, row in enumerate(levels):
        for idx, label in enumerate(row):
            x = 640 / (len(row) + 1) * (idx + 1)
            y = 56 + depth * 84
            nodes.append({"id": label, "label": label, "x": x, "y": y, "highlight": label in highlight_nodes})
    graph_edges = [{"from": parent, "to": child} for parent, child in edges]
    return {"nodes": nodes, "edges": graph_edges}


def _build_graph_nodes_and_edges(
    all_labels: list[str],
    node_pos: dict[str, tuple[float, float]],
    edges: list[tuple[str, str]],
    current: str | None,
    visited: list[str],
    frontier: list[str],
    order: dict[str, int],
    current_edge: tuple[str, str] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """공통 노드/엣지 데이터 빌더 — _graph_state 계열 함수에서 공유."""
    nodes = []
    for label in all_labels:
        x, y = node_pos[label]
        nodes.append({
            "id": label,
            "label": label,
            "x": x,
            "y": y,
            "current": label == current,
            "visited": label in visited,
            "frontier": label in frontier,
            "order": order.get(label),
        })
    edge_data = []
    for left, right in edges:
        is_active = current_edge in {(left, right), (right, left)}
        is_traversed = left in visited and right in visited
        edge_data.append({"from": left, "to": right, "label": "", "active": is_active, "traversed": is_traversed})
    return nodes, edge_data


def _graph_state(
    edges: list[tuple[str, str]],
    current: str | None = None,
    visited: list[str] | None = None,
    frontier: list[str] | None = None,
    frontier_label: str | None = None,
    current_edge: tuple[str, str] | None = None,
    order: dict[str, int] | None = None,
) -> dict[str, Any]:
    """원형 레이아웃 — graph 자료구조 표시 및 graph 액션에 사용."""
    labels = sorted({item for edge in edges for item in edge})
    radius, center_x, center_y = 150, 320, 150
    visited = visited or []
    frontier = frontier or []
    order = order or {}
    node_pos = {
        label: (
            center_x + radius * math.cos((2 * math.pi * idx) / max(len(labels), 1)),
            center_y + radius * math.sin((2 * math.pi * idx) / max(len(labels), 1)),
        )
        for idx, label in enumerate(labels)
    }
    nodes, edge_data = _build_graph_nodes_and_edges(
        labels, node_pos, edges, current, visited, frontier, order, current_edge
    )
    return {"nodes": nodes, "edges": edge_data, "frontier": frontier, "frontierLabel": frontier_label}


def _graph_state_tree_layout(
    edges: list[tuple[str, str]],
    start: str | None = None,
    current: str | None = None,
    visited: list[str] | None = None,
    frontier: list[str] | None = None,
    frontier_label: str | None = None,
    current_edge: tuple[str, str] | None = None,
    order: dict[str, int] | None = None,
) -> dict[str, Any]:
    """트리 레벨 레이아웃 — BFS/DFS 순회 시각화에 사용."""
    all_labels = sorted({item for edge in edges for item in edge})
    adjacency: dict[str, list[str]] = {}
    for left, right in edges:
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)

    root = start or (all_labels[0] if all_labels else None)
    levels: list[list[str]] = []
    bfs_q: deque[tuple[str, int]] = deque([(root, 0)])
    visited_layout: set[str] = set()
    while bfs_q:
        node, depth = bfs_q.popleft()
        if node in visited_layout:
            continue
        visited_layout.add(node)
        while len(levels) <= depth:
            levels.append([])
        levels[depth].append(node)
        for neighbor in sorted(adjacency.get(node, [])):
            if neighbor not in visited_layout:
                bfs_q.append((neighbor, depth + 1))

    node_pos: dict[str, tuple[float, float]] = {
        label: (640 / (len(row) + 1) * (idx + 1), 56 + depth * 84)
        for depth, row in enumerate(levels)
        for idx, label in enumerate(row)
    }

    visited = visited or []
    frontier = frontier or []
    order = order or {}
    nodes, edge_data = _build_graph_nodes_and_edges(
        all_labels, node_pos, edges, current, visited, frontier, order, current_edge
    )
    return {"nodes": nodes, "edges": edge_data, "frontier": frontier, "frontierLabel": frontier_label}

def build_array_steps(values: list[float]) -> list[dict[str, Any]]:
    # code_array 줄 번호 기준:
    # 2: arr=[] / 3: for value in values / 4: arr.append(value) / 5: return
    steps: list[dict[str, Any]] = [{
        "state": {"values": [], "compare": []},
        "message": "빈 배열 arr을 만듭니다.",
        "activeLines": [2],
    }]
    current: list[float] = []
    for index, value in enumerate(values):
        steps.append({
            "state": {"values": current[:], "compare": []},
            "message": f"value = {_fmt(value)} — 다음 값을 읽습니다.",
            "activeLines": [3],
        })
        current.append(value)
        steps.append({
            "state": {"values": current[:], "compare": [index]},
            "message": f"arr.append({_fmt(value)}) — 인덱스 {index}에 추가합니다.",
            "activeLines": [4],
        })
    steps.append({
        "state": {"values": current[:], "compare": []},
        "message": f"배열 완성. 길이: {len(current)}",
        "activeLines": [5],
    })
    return steps


def build_list_steps(values: list[float]) -> list[dict[str, Any]]:
    # code_list 줄 번호 기준:
    # 2~5: class Node / 6: head=None / 7: for / 8: node=Node(value)
    # 9: if head is None / 10: head=node / 11: else / 12: cur=head
    # 13: while cur.next / 14: cur=cur.next / 15: cur.next=node
    steps: list[dict[str, Any]] = [{
        "state": {"values": [], "compare": []},
        "message": "head = None, 빈 연결 리스트에서 시작합니다.",
        "activeLines": [6],
    }]
    current: list[float] = []
    for index, value in enumerate(values):
        steps.append({
            "state": {"values": current[:], "compare": [], "incoming": value},
            "message": f"node = Node({_fmt(value)}) — 새 노드를 생성합니다.",
            "activeLines": [8],
        })
        if index == 0:
            current.append(value)
            steps.append({
                "state": {"values": current[:], "compare": [0]},
                "message": f"head가 None이므로 head = node. {_fmt(value)}가 첫 노드입니다.",
                "activeLines": [9, 10],
            })
        else:
            steps.append({
                "state": {"values": current[:], "compare": [0]},
                "message": "head가 있으므로 cur = head에서 시작합니다.",
                "activeLines": [11, 12],
            })
            steps.append({
                "state": {"values": current[:], "compare": [len(current) - 1]},
                "message": "cur.next가 None이 될 때까지 이동합니다.",
                "activeLines": [13, 14],
            })
            current.append(value)
            steps.append({
                "state": {"values": current[:], "compare": [len(current) - 1]},
                "message": f"cur.next = node — {_fmt(value)}를 마지막 노드에 연결합니다.",
                "activeLines": [15],
            })
    return steps


def build_stack_steps(commands: list[tuple[str, float | None]]) -> list[dict[str, Any]]:
    # code_stack_ops 줄 번호 기준:
    # 2: stack=[] / 3: for / 4: if push / 5: stack.append(value)
    # 6: elif stack / 7: stack.pop()
    stack: list[float] = []
    steps = [{"state": {"stack": [], "action": "idle", "incoming": None, "removed": None}, "message": "stack=[]. 빈 스택에서 시작합니다.", "activeLines": [2]}]
    for command, value in commands:
        if command == "push":
            steps.append({"state": {"stack": stack[:], "action": "push", "incoming": value, "removed": None}, "message": f"stack.append({_fmt(value)}) — {_fmt(value)}를 스택에 올립니다.", "activeLines": [4, 5]})
            stack.append(value if value is not None else 0)
            steps.append({"state": {"stack": stack[:], "action": "push-done", "incoming": None, "removed": None}, "message": f"push 완료. 현재 top = {_fmt(stack[-1])}", "activeLines": [5]})
        else:
            if not stack:
                raise ValueError("빈 스택에서는 pop을 실행할 수 없습니다.")
            removed = stack[-1]
            steps.append({"state": {"stack": stack[:], "action": "pop", "incoming": None, "removed": removed}, "message": f"stack.pop() — top 값 {_fmt(removed)}를 꺼냅니다.", "activeLines": [6, 7]})
            stack.pop()
            steps.append({"state": {"stack": stack[:], "action": "pop-done", "incoming": None, "removed": removed}, "message": f"pop 완료. {'스택이 비었습니다.' if not stack else f'현재 top = {_fmt(stack[-1])}'}", "activeLines": [7]})
    return steps


def build_queue_steps(commands: list[tuple[str, float | None]]) -> list[dict[str, Any]]:
    # code_queue_ops 줄 번호 기준:
    # 2: queue=deque() / 3: for / 4: if enqueue / 5: queue.append(value)
    # 6: elif queue / 7: queue.popleft()
    queue: list[float] = []
    steps = [{"state": {"queue": [], "action": "idle", "incoming": None, "removed": None}, "message": "queue=deque(). 빈 큐에서 시작합니다.", "activeLines": [2]}]
    for command, value in commands:
        if command == "enqueue":
            steps.append({"state": {"queue": queue[:], "action": "enqueue", "incoming": value, "removed": None}, "message": f"queue.append({_fmt(value)}) — {_fmt(value)}를 rear에 추가합니다.", "activeLines": [4, 5]})
            queue.append(value if value is not None else 0)
            steps.append({"state": {"queue": queue[:], "action": "enqueue-done", "incoming": None, "removed": None}, "message": f"enqueue 완료. 큐 크기: {len(queue)}", "activeLines": [5]})
        else:
            if not queue:
                raise ValueError("빈 큐에서는 dequeue를 실행할 수 없습니다.")
            removed = queue[0]
            steps.append({"state": {"queue": queue[:], "action": "dequeue", "incoming": None, "removed": removed}, "message": f"queue.popleft() — front 값 {_fmt(removed)}를 꺼냅니다.", "activeLines": [6, 7]})
            queue.pop(0)
            steps.append({"state": {"queue": queue[:], "action": "dequeue-done", "incoming": None, "removed": removed}, "message": f"dequeue 완료. {'큐가 비었습니다.' if not queue else f'현재 front = {_fmt(queue[0])}'}", "activeLines": [7]})
    return steps


def build_tree_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    edges = payload["edges"]
    steps = []
    built: list[tuple[str, str]] = []
    for parent, child in edges:
        built.append((parent, child))
        steps.append({"state": _tree_state_from_edges(built, [parent, child]), "message": f"{parent}와 {child}를 연결했습니다.", "activeLines": [3, 4]})
    return steps



def build_graph_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    edges = payload["edges"]
    start = payload["start"]
    return [{"state": _graph_state(edges, current=start), "message": f"그래프와 시작 노드 {start}를 표시했습니다.", "activeLines": [3, 4, 5]}]


def build_bubble_sort_steps(values: list[float]) -> list[dict[str, Any]]:
    # code_bubble_sort 줄 번호 기준:
    # 2: arr=values[:] / 3: n=len(arr) / 4: for i in range(n)
    # 5: swapped=False / 6: for j in range(n-i-1) / 7: if arr[j]>arr[j+1]
    # 8: swap / 9: swapped=True / 10: if not swapped / 11: break
    arr = values[:]
    steps = [{"state": {"values": arr[:], "sorted": []}, "message": "초기 배열 상태입니다.", "activeLines": [2, 3]}]
    for i in range(len(arr)):
        swapped = False
        for j in range(len(arr) - i - 1):
            steps.append({"state": {"values": arr[:], "compare": [j, j + 1], "sorted": list(range(len(arr) - i, len(arr)))}, "message": f"{_fmt(arr[j])}와 {_fmt(arr[j + 1])}를 비교합니다.", "activeLines": [6, 7]})
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
                steps.append({"state": {"values": arr[:], "swap": [j, j + 1], "sorted": list(range(len(arr) - i, len(arr)))}, "message": "두 값을 교환했습니다.", "activeLines": [8, 9]})
        if not swapped:
            steps.append({"state": {"values": arr[:], "sorted": list(range(len(arr)))}, "message": "교환이 없어 조기 종료합니다.", "activeLines": [10, 11]})
            break
    return steps


def build_selection_sort_steps(values: list[float]) -> list[dict[str, Any]]:
    arr = values[:]
    steps = [{"state": {"values": arr[:], "sorted": []}, "message": "초기 배열 상태입니다.", "activeLines": [1]}]
    for i in range(len(arr)):
        min_index = i
        for j in range(i + 1, len(arr)):
            steps.append({"state": {"values": arr[:], "compare": [min_index, j], "sorted": list(range(i))}, "message": f"{_fmt(arr[min_index])}와 {_fmt(arr[j])}를 비교합니다.", "activeLines": [6, 7]})
            if arr[j] < arr[min_index]:
                min_index = j
                steps.append({"state": {"values": arr[:], "compare": [min_index], "sorted": list(range(i))}, "message": f"최솟값 후보가 {_fmt(arr[min_index])}로 바뀌었습니다.", "activeLines": [8]})
        if i != min_index:
            arr[i], arr[min_index] = arr[min_index], arr[i]
        steps.append({"state": {"values": arr[:], "swap": [i, min_index] if i != min_index else [], "sorted": list(range(i + 1))}, "message": f"{i}번 위치에 최소값을 놓았습니다.", "activeLines": [9]})
    return steps


def build_insertion_sort_steps(values: list[float]) -> list[dict[str, Any]]:
    arr = values[:]
    steps = [{"state": {"values": arr[:], "sorted": [0] if arr else []}, "message": "첫 번째 원소를 정렬된 구간으로 봅니다.", "activeLines": [3]}]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            steps.append({"state": {"values": arr[:], "swap": [j, j + 1], "sorted": list(range(i + 1))}, "message": f"{_fmt(arr[j + 1])}를 오른쪽으로 이동합니다.", "activeLines": [6, 7]})
            j -= 1
        arr[j + 1] = key
        steps.append({"state": {"values": arr[:], "compare": [j + 1], "sorted": list(range(i + 1))}, "message": f"{_fmt(key)}를 {_fmt(j + 1)} 위치에 삽입했습니다.", "activeLines": [9]})
    return steps


def build_quick_sort_steps(values: list[float]) -> list[dict[str, Any]]:
    arr = values[:]
    steps = [{"state": {"values": arr[:]}, "message": "초기 배열 상태입니다.", "activeLines": [1]}]

    def quicksort(left: int, right: int) -> None:
        if left >= right:
            return
        pivot = arr[right]
        i = left
        steps.append({"state": {"values": arr[:], "compare": [right]}, "message": f"피벗으로 {_fmt(pivot)}를 선택합니다.", "activeLines": [4]})
        for j in range(left, right):
            steps.append({"state": {"values": arr[:], "compare": [j, right]}, "message": f"{_fmt(arr[j])}와 피벗 {_fmt(pivot)}를 비교합니다.", "activeLines": [5]})
            if arr[j] <= pivot:
                arr[i], arr[j] = arr[j], arr[i]
                steps.append({"state": {"values": arr[:], "swap": [i, j]}, "message": f"{_fmt(arr[i])}를 피벗 왼쪽 구간으로 보냅니다.", "activeLines": [5]})
                i += 1
        arr[i], arr[right] = arr[right], arr[i]
        steps.append({"state": {"values": arr[:], "swap": [i, right]}, "message": f"피벗 {_fmt(arr[i])}를 제자리로 이동합니다.", "activeLines": [4]})
        quicksort(left, i - 1)
        quicksort(i + 1, right)

    quicksort(0, len(arr) - 1)
    steps.append({"state": {"values": arr[:], "sorted": list(range(len(arr)))}, "message": "퀵 정렬이 완료되었습니다.", "activeLines": [7]})
    return steps


def build_merge_sort_steps(values: list[float]) -> list[dict[str, Any]]:
    # code_merge_sort 줄 번호 기준:
    # 2: if len<=1 / 3: return / 4: mid=... / 5: left=... / 6: right=...
    # 7: merged=[] / 8: i=j=0 / 9: while i<len(left) and j<len(right)
    # 10: if left[i]<=right[j] / 11: merged.append(left[i]) / 12: i+=1
    # 13: else / 14: merged.append(right[j]) / 15: j+=1
    # 16: return merged+left[i:]+right[j:]
    arr = values[:]
    steps = [{"state": {"values": arr[:]}, "message": "초기 배열 상태입니다.", "activeLines": [1]}]

    def mergesort(left: int, right: int) -> None:
        if left >= right:
            return
        mid = (left + right) // 2
        steps.append({"state": {"values": arr[:], "compare": list(range(left, right + 1))}, "message": f"{left}~{right} 구간을 둘로 나눕니다.", "activeLines": [4, 5, 6]})
        mergesort(left, mid)
        mergesort(mid + 1, right)
        merged = []
        i, j = left, mid + 1
        while i <= mid and j <= right:
            if arr[i] <= arr[j]:
                merged.append(arr[i])
                i += 1
            else:
                merged.append(arr[j])
                j += 1
        merged.extend(arr[i:mid + 1])
        merged.extend(arr[j:right + 1])
        arr[left:right + 1] = merged
        steps.append({"state": {"values": arr[:], "swap": list(range(left, right + 1))}, "message": f"{left}~{right} 구간을 병합했습니다.", "activeLines": [9, 10, 11, 12, 13, 14, 15, 16]})

    mergesort(0, len(arr) - 1)
    steps.append({"state": {"values": arr[:], "sorted": list(range(len(arr)))}, "message": "병합 정렬이 완료되었습니다.", "activeLines": [16]})
    return steps


def build_linear_search_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    values = payload["values"]
    target = payload["target"]
    steps = []
    for idx, value in enumerate(values):
        found = value == target
        steps.append({"state": {"values": values, "current": idx, "found": idx if found else None, "target": target}, "message": f"{idx}번 값을 확인했습니다.", "activeLines": [2, 3]})
        if found:
            steps.append({"state": {"values": values, "current": idx, "found": idx, "target": target}, "message": f"{_fmt(target)}을(를) 찾았습니다.", "activeLines": [5, 6]})
            return steps
    steps.append({"state": {"values": values, "current": None, "found": None, "target": target}, "message": f"{_fmt(target)}은(는) 목록에 없습니다.", "activeLines": [5]})
    return steps


def build_binary_search_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    values = payload["values"]
    target = payload["target"]
    low, high = 0, len(values) - 1
    steps = [{"state": {"values": values, "low": low, "high": high, "mid": None, "target": target}, "message": "정렬된 목록에서 범위를 시작합니다.", "activeLines": [2]}]
    while low <= high:
        mid = (low + high) // 2
        steps.append({"state": {"values": values, "low": low, "high": high, "mid": mid, "target": target}, "message": f"중간값 {_fmt(values[mid])}를 봅니다.", "activeLines": [4]})
        if values[mid] == target:
            steps.append({"state": {"values": values, "low": low, "high": high, "mid": mid, "found": mid, "target": target}, "message": f"{_fmt(target)}을(를) 찾았습니다.", "activeLines": [5, 6]})
            return steps
        if values[mid] < target:
            low = mid + 1
            steps.append({"state": {"values": values, "low": low, "high": high, "mid": mid, "target": target}, "message": "오른쪽 절반만 남깁니다.", "activeLines": [7, 8]})
        else:
            high = mid - 1
            steps.append({"state": {"values": values, "low": low, "high": high, "mid": mid, "target": target}, "message": "왼쪽 절반만 남깁니다.", "activeLines": [9, 10]})
    steps.append({"state": {"values": values, "low": low, "high": high, "mid": None, "target": target}, "message": f"{_fmt(target)}은(는) 목록에 없습니다.", "activeLines": [11]})
    return steps


def _add_frontier_chips(state: dict[str, Any], frontier: list[str], frontier_label: str, visited: list[str]) -> dict[str, Any]:
    """state 딕셔너리에 frontier_chips(큐/스택 칩 데이터)와 visited_chips를 추가한다."""
    state = dict(state)
    state["frontier_chips"] = list(frontier)
    state["frontier_label"] = frontier_label
    state["visited_chips"] = list(visited)
    return state


def build_dfs_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    # code_dfs 줄 번호 기준:
    # 1: def / 2: stack=[start] / 3: visited=[] / 4: while stack
    # 5: node=stack.pop() / 6: if node in visited / 7: continue
    # 8: visited.append / 9: for next_node in reversed(...) / 10: if not visited / 11: stack.append / 12: return
    edges = payload["edges"]
    start = payload["start"]
    adjacency: dict[str, list[str]] = {}
    for left, right in edges:
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)
    for key in adjacency:
        adjacency[key].sort()

    stack: list[str] = [start]
    visited: list[str] = []
    steps: list[dict[str, Any]] = []

    steps.append({
        "state": _add_frontier_chips(
            _graph_state_tree_layout(edges, start=start, current=None, visited=[], frontier=stack[:], frontier_label="스택", order={}),
            stack[:], "스택", [],
        ),
        "message": f"스택에 시작 노드 {start}를 넣습니다.",
        "activeLines": [2, 3],
    })

    while stack:
        node = stack.pop()
        order = {label: index + 1 for index, label in enumerate(visited)}

        if node in visited:
            steps.append({
                "state": _add_frontier_chips(
                    _graph_state_tree_layout(edges, start=start, current=node, visited=visited[:], frontier=stack[:], frontier_label="스택", order=order),
                    stack[:], "스택", visited[:],
                ),
                "message": f"{node}는 이미 방문했습니다 — 건너뜁니다.",
                "activeLines": [6, 7],
            })
            continue

        visited.append(node)
        order = {label: index + 1 for index, label in enumerate(visited)}
        steps.append({
            "state": _add_frontier_chips(
                _graph_state_tree_layout(edges, start=start, current=node, visited=visited[:], frontier=stack[:], frontier_label="스택", order=order),
                stack[:], "스택", visited[:],
            ),
            "message": f"{node}를 방문합니다. 방문 순서: {' → '.join(visited)}",
            "activeLines": [8],
        })

        neighbors = list(reversed(adjacency.get(node, [])))
        pushed = []
        for next_node in neighbors:
            if next_node not in visited:
                # 각 이웃 노드마다 확인 간선 애니메이션 추가 (BFS처럼)
                steps.append({
                    "state": _add_frontier_chips(
                        _graph_state_tree_layout(edges, start=start, current=node, visited=visited[:], frontier=stack[:], frontier_label="스택", order=order, current_edge=(node, next_node)),
                        stack[:], "스택", visited[:],
                    ),
                    "message": f"'{node}' → '{next_node}' 간선 확인. 스택에 추가합니다.",
                    "activeLines": [9, 10, 11],
                })
                stack.append(next_node)
                pushed.append(next_node)

        if pushed:
            steps.append({
                "state": _add_frontier_chips(
                    _graph_state_tree_layout(edges, start=start, current=node, visited=visited[:], frontier=stack[:], frontier_label="스택", order=order),
                    stack[:], "스택", visited[:],
                ),
                "message": f"스택에 {', '.join(pushed)} 추가. 현재 스택(top→): {list(reversed(stack))}",
                "activeLines": [9, 10, 11],
            })

    order = {label: index + 1 for index, label in enumerate(visited)}
    steps.append({
        "state": _add_frontier_chips(
            _graph_state_tree_layout(edges, start=start, current=None, visited=visited[:], frontier=[], frontier_label="스택", order=order),
            [], "스택", visited[:],
        ),
        "message": f"탐색 완료. 방문 순서: {' → '.join(visited)}",
        "activeLines": [12],
    })
    return steps


def build_bfs_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    edges = payload["edges"]
    start = payload["start"]
    adjacency: dict[str, list[str]] = {}
    for left, right in edges:
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)
    for key in adjacency:
        adjacency[key].sort()
    queue = deque([start])
    visited = [start]
    order = {start: 1}
    steps = [{
        "state": _add_frontier_chips(
            _graph_state_tree_layout(edges, start=start, current=start, visited=visited[:], frontier=list(queue), frontier_label="큐", order=order),
            list(queue), "큐", visited[:],
        ),
        "message": f"{start}에서 시작합니다.",
        "activeLines": [2, 3],
    }]
    while queue:
        node = queue.popleft()
        order = {label: index + 1 for index, label in enumerate(visited)}
        steps.append({
            "state": _add_frontier_chips(
                _graph_state_tree_layout(edges, start=start, current=node, visited=visited[:], frontier=list(queue), frontier_label="큐", order=order),
                list(queue), "큐", visited[:],
            ),
            "message": f"{node}를 꺼내 이웃을 확인합니다.",
            "activeLines": [5],
        })
        for next_node in adjacency.get(node, []):
            if next_node not in visited:
                visited.append(next_node)
                queue.append(next_node)
                order = {label: index + 1 for index, label in enumerate(visited)}
                steps.append({
                    "state": _add_frontier_chips(
                        _graph_state_tree_layout(edges, start=start, current=node, visited=visited[:], frontier=list(queue), frontier_label="큐", current_edge=(node, next_node), order=order),
                        list(queue), "큐", visited[:],
                    ),
                    "message": f"{next_node}를 큐에 추가했습니다.",
                    "activeLines": [7, 8, 9],
                })
    order = {label: index + 1 for index, label in enumerate(visited)}
    steps.append({
        "state": _add_frontier_chips(
            _graph_state_tree_layout(edges, start=start, current=None, visited=visited[:], frontier=[], frontier_label="큐", order=order),
            [], "큐", visited[:],
        ),
        "message": f"탐색 완료. 방문 순서: {' → '.join(visited)}",
        "activeLines": [10],
    })
    return steps


def build_preorder_steps(values: list[str | None]) -> list[dict[str, Any]]:
    # code_preorder 줄 번호 기준:
    # 1: def / 2: stack=[0] / 3: result=[] / 4: while stack / 5: idx=stack.pop()
    # 6: if ... continue / 7: result.append / 8: stack.append(right) / 9: stack.append(left) / 10: return
    stack: list[int] = [0]
    result: list[int] = []
    steps: list[dict[str, Any]] = []

    def _state(highlight: list[int]) -> dict[str, Any]:
        base = _tree_state_from_binary(values, highlight)
        base["stack_labels"] = [str(values[i]) for i in stack if i < len(values) and values[i] is not None]
        base["result_labels"] = [str(values[i]) for i in result]
        return base

    steps.append({
        "state": _state([]),
        "message": "스택에 루트(인덱스 0)를 넣고 시작합니다.",
        "activeLines": [2],
    })

    while stack:
        idx = stack.pop()

        if idx >= len(values) or values[idx] is None:
            steps.append({
                "state": _state([]),
                "message": f"인덱스 {idx}는 None — 건너뜁니다.",
                "activeLines": [5, 6],
            })
            continue

        result.append(idx)
        visited_labels = [str(values[i]) for i in result]
        steps.append({
            "state": _state([idx]),
            "message": f"{values[idx]}를 방문합니다. 순서: {' > '.join(visited_labels)}",
            "activeLines": [7],
        })

        right, left = idx * 2 + 2, idx * 2 + 1
        children_pushed = []
        if right < len(values) and values[right] is not None:
            stack.append(right)
            children_pushed.append(str(values[right]))
        if left < len(values) and values[left] is not None:
            stack.append(left)
            children_pushed.append(str(values[left]))
        if children_pushed:
            steps.append({
                "state": _state([idx]),
                "message": f"스택에 {', '.join(children_pushed)} 추가. 스택: {[str(values[i]) for i in stack]}",
                "activeLines": [8, 9],
            })

    steps.append({
        "state": _state([]),
        "message": f"순회 완료. 결과: {' > '.join(str(values[i]) for i in result)}",
        "activeLines": [10],
    })
    return steps


def build_inorder_steps(values: list[str | None]) -> list[dict[str, Any]]:
    # code_inorder 줄 번호 기준:
    # 1: def / 2: stack=[] / 3: result=[] / 4: idx=0 / 5: while stack or ...
    # 6: while idx ... / 7: stack.append(idx) / 8: idx=left / 9: idx=stack.pop()
    # 10: result.append / 11: idx=right / 12: return
    stack: list[int] = []
    result: list[int] = []
    steps: list[dict[str, Any]] = []
    idx = 0

    def _state(highlight: list[int]) -> dict[str, Any]:
        base = _tree_state_from_binary(values, highlight)
        base["stack_labels"] = [str(values[i]) for i in stack if i < len(values) and values[i] is not None]
        base["result_labels"] = [str(values[i]) for i in result]
        return base

    steps.append({
        "state": _state([]),
        "message": "빈 스택과 idx=0(루트)으로 시작합니다.",
        "activeLines": [2, 3, 4],
    })

    while stack or (idx < len(values) and values[idx] is not None):
        while idx < len(values) and values[idx] is not None:
            stack.append(idx)
            steps.append({
                "state": _state([idx]),
                "message": f"{values[idx]}를 스택에 쌓고 왼쪽으로 내려갑니다. 스택: {[str(values[i]) for i in stack]}",
                "activeLines": [7, 8],
            })
            idx = idx * 2 + 1

        idx = stack.pop()
        result.append(idx)
        visited_labels = [str(values[i]) for i in result]
        steps.append({
            "state": _state([idx]),
            "message": f"{values[idx]}를 방문합니다. 순서: {' > '.join(visited_labels)}",
            "activeLines": [9, 10],
        })
        right_idx = idx * 2 + 2
        if right_idx < len(values) and values[right_idx] is not None:
            steps.append({
                "state": _state([right_idx]),
                "message": f"오른쪽 자식 {values[right_idx]}로 이동합니다.",
                "activeLines": [11],
            })
        else:
            steps.append({
                "state": _state([]),
                "message": "오른쪽 자식이 없습니다. 스택에서 다음 노드를 꺼냅니다.",
                "activeLines": [11],
            })
        idx = right_idx

    steps.append({
        "state": _state([]),
        "message": f"순회 완료. 결과: {' > '.join(str(values[i]) for i in result)}",
        "activeLines": [12],
    })
    return steps


def build_postorder_steps(values: list[str | None]) -> list[dict[str, Any]]:
    # code_postorder 줄 번호 기준:
    # 1: def / 2: stack=[0] / 3: result=[] / 4: while stack / 5: idx=stack.pop()
    # 6: if ... continue / 7: result.append / 8: stack.append(left) / 9: stack.append(right) / 10: return result[::-1]
    stack: list[int] = [0]
    result: list[int] = []
    steps: list[dict[str, Any]] = []

    def _state(highlight: list[int]) -> dict[str, Any]:
        base = _tree_state_from_binary(values, highlight)
        base["stack_labels"] = [str(values[i]) for i in stack if i < len(values) and values[i] is not None]
        # postorder는 result를 뒤집어서 표시
        base["result_labels"] = list(reversed([str(values[i]) for i in result]))
        return base

    steps.append({
        "state": _state([]),
        "message": "스택에 루트(인덱스 0)를 넣고 시작합니다. 결과는 마지막에 뒤집습니다.",
        "activeLines": [2],
    })

    while stack:
        idx = stack.pop()

        if idx >= len(values) or values[idx] is None:
            steps.append({
                "state": _state([]),
                "message": f"인덱스 {idx}는 None — 건너뜁니다.",
                "activeLines": [5, 6],
            })
            continue

        result.append(idx)
        steps.append({
            "state": _state([idx]),
            "message": f"{values[idx]}를 역순 버퍼에 추가합니다. 현재 버퍼(뒤집기 전): {[str(values[i]) for i in result]}",
            "activeLines": [7],
        })

        children_pushed = []
        left, right = idx * 2 + 1, idx * 2 + 2
        if left < len(values) and values[left] is not None:
            stack.append(left)
            children_pushed.append(str(values[left]))
        if right < len(values) and values[right] is not None:
            stack.append(right)
            children_pushed.append(str(values[right]))
        if children_pushed:
            steps.append({
                "state": _state([idx]),
                "message": f"스택에 {', '.join(children_pushed)} 추가. 스택: {[str(values[i]) for i in stack]}",
                "activeLines": [8, 9],
            })

    final = list(reversed([str(values[i]) for i in result]))
    steps.append({
        "state": _state([]),
        "message": f"버퍼를 뒤집어 완성. 결과: {' > '.join(final)}",
        "activeLines": [10],
    })
    return steps


def code_array(values: list[float]) -> list[float]:
    arr = []
    for value in values:
        arr.append(value)
    return arr


def code_list(values: list[float]) -> None:
    class Node:
        def __init__(self, val):
            self.val = val
            self.next = None
    head = None
    for value in values:
        node = Node(value)
        if head is None:
            head = node
        else:
            cur = head
            while cur.next:
                cur = cur.next
            cur.next = node


def code_stack_ops(commands: list[tuple[str, float | None]]) -> list[float]:
    stack = []
    for action, value in commands:
        if action == "push":
            stack.append(value)
        elif stack:           # pop: 스택이 비어 있지 않을 때만
            stack.pop()
    return stack


def code_queue_ops(commands: list[tuple[str, float | None]]) -> list[float]:
    queue = deque()
    for action, value in commands:
        if action == "enqueue":
            queue.append(value)       # rear에 추가
        elif queue:                   # dequeue: 큐가 비어 있지 않을 때만
            queue.popleft()           # front에서 제거
    return list(queue)


def code_tree(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for parent, child in edges:
        graph.setdefault(parent, []).append(child)
    return graph



def code_graph(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    graph: dict[str, list[str]] = {}
    for left, right in edges:
        graph.setdefault(left, []).append(right)
        graph.setdefault(right, []).append(left)
    return graph


def code_bubble_sort(values: list[float]) -> list[float]:
    arr = values[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def code_selection_sort(values: list[float]) -> list[float]:
    arr = values[:]
    n = len(arr)
    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr


def code_insertion_sort(values: list[float]) -> list[float]:
    arr = values[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def code_quick_sort(values: list[float]) -> list[float]:
    if len(values) <= 1:
        return values[:]
    pivot = values[-1]
    left = [value for value in values[:-1] if value <= pivot]
    right = [value for value in values[:-1] if value > pivot]
    return code_quick_sort(left) + [pivot] + code_quick_sort(right)


def code_merge_sort(values: list[float]) -> list[float]:
    if len(values) <= 1:
        return values[:]
    mid = len(values) // 2
    left = code_merge_sort(values[:mid])
    right = code_merge_sort(values[mid:])
    merged: list[float] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    return merged + left[i:] + right[j:]


def code_linear_search(values: list[float], target: float) -> int:
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def code_binary_search(values: list[float], target: float) -> int:
    low, high = 0, len(values) - 1
    while low <= high:
        mid = (low + high) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def code_dfs(graph: dict[str, list[str]], start: str) -> list[str]:
    stack = [start]
    visited = []
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.append(node)
        for next_node in reversed(graph.get(node, [])):
            if next_node not in visited:
                stack.append(next_node)
    return visited


def code_bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    queue = deque([start])
    visited = [start]
    while queue:
        node = queue.popleft()
        for next_node in graph.get(node, []):
            if next_node not in visited:
                visited.append(next_node)
                queue.append(next_node)
    return visited


def code_preorder(values: list[str | None]) -> list[str]:
    stack = [0]
    result = []
    while stack:
        idx = stack.pop()
        if idx >= len(values) or values[idx] is None:
            continue
        result.append(str(values[idx]))
        stack.append(idx * 2 + 2)
        stack.append(idx * 2 + 1)
    return result


def code_inorder(values: list[str | None]) -> list[str]:
    stack = []
    result = []
    idx = 0
    while stack or (idx < len(values) and values[idx] is not None):
        while idx < len(values) and values[idx] is not None:
            stack.append(idx)
            idx = idx * 2 + 1
        idx = stack.pop()
        result.append(str(values[idx]))
        idx = idx * 2 + 2
    return result


def code_postorder(values: list[str | None]) -> list[str]:
    stack = [0]
    result = []
    while stack:
        idx = stack.pop()
        if idx >= len(values) or values[idx] is None:
            continue
        result.append(str(values[idx]))
        stack.append(idx * 2 + 1)
        stack.append(idx * 2 + 2)
    return result[::-1]


CODE_FUNCTIONS = {
    "array": code_array,
    "list": code_list,
    "stackOps": code_stack_ops,
    "queueOps": code_queue_ops,
    "tree": code_tree,
    "graph": code_graph,
    "bubbleSort": code_bubble_sort,
    "selectionSort": code_selection_sort,
    "insertionSort": code_insertion_sort,
    "quickSort": code_quick_sort,
    "mergeSort": code_merge_sort,
    "linearSearch": code_linear_search,
    "binarySearch": code_binary_search,
    "dfs": code_dfs,
    "bfs": code_bfs,
    "preorder": code_preorder,
    "inorder": code_inorder,
    "postorder": code_postorder,
}


def _code_lines(key: str) -> list[str]:
    source = textwrap.dedent(inspect.getsource(CODE_FUNCTIONS[key])).strip("\n")
    return source.splitlines()


ALGORITHMS: dict[str, AlgorithmDefinition] = {
    "array": AlgorithmDefinition(
        key="array",
        title="배열",
        category="자료구조",
        subcategory="선형 자료구조",
        badge="DS · 선형",
        compare_text="배열은 같은 타입의 데이터를 연속된 메모리처럼 다루는 구조로 이해하면 좋습니다. 인덱스로 바로 접근할 수 있다는 점이 핵심입니다.",
        input_label="입력 형식: 쉼표로 구분된 숫자 목록",
        input_description="예시: 8, 3, 5, 1",
        example="8, 3, 5, 1",
        python_code=_code_lines("array"),
        renderer="sequence",
    ),
    "list": AlgorithmDefinition(
        key="list",
        title="리스트",
        category="자료구조",
        subcategory="선형 자료구조",
        badge="DS · 선형",
        compare_text="리스트는 값이 순서대로 연결되어 있다고 생각하며 보면 이해가 쉽습니다. 노드와 다음 위치의 연결을 따라가며 삽입과 삭제가 일어나는 과정을 시각적으로 살펴보기에 좋습니다.",
        input_label="입력 형식: 쉼표로 구분된 숫자 목록",
        input_description="예시: 4, 9, 1, 7",
        example="4, 9, 1, 7",
        python_code=_code_lines("list"),
        renderer="sequence",
    ),
    "stackOps": AlgorithmDefinition(
        key="stackOps",
        title="스택",
        category="자료구조",
        subcategory="선형 자료구조",
        badge="DS · 선형",
        compare_text="스택은 가장 나중에 들어온 값이 가장 먼저 나오는 후입선출 구조입니다. 함수 호출 스택이나 되돌리기 기능처럼 최근 작업부터 꺼내는 흐름을 설명할 때 적합합니다.",
        input_label="입력 형식: push/pop 명령",
        input_description="예시: push 10; push 20; pop; push 30",
        example="push 10; push 20; pop; push 30",
        python_code=_code_lines("stackOps"),
        renderer="stack",
    ),
    "queueOps": AlgorithmDefinition(
        key="queueOps",
        title="큐",
        category="자료구조",
        subcategory="선형 자료구조",
        badge="DS · 선형",
        compare_text="큐는 먼저 들어온 데이터가 먼저 나가는 선입선출 구조입니다. 대기열, 작업 스케줄링 같은 흐름을 설명할 때 적합합니다.",
        input_label="입력 형식: enqueue/dequeue 명령",
        input_description="예시: enqueue 10; enqueue 20; dequeue; enqueue 30",
        example="enqueue 10; enqueue 20; dequeue; enqueue 30",
        python_code=_code_lines("queueOps"),
        renderer="queue",
    ),
    "tree": AlgorithmDefinition(
        key="tree",
        title="트리",
        category="자료구조",
        subcategory="비선형 자료구조",
        badge="DS · 비선형",
        compare_text="트리는 부모와 자식 관계로 계층을 표현하는 구조입니다. 폴더 구조처럼 위에서 아래로 퍼지는 개념을 이해하기 좋습니다.",
        input_label="입력 형식: 부모>자식 간선 목록",
        input_description="예시: A>B, A>C, B>D, B>E, C>F",
        example="A>B, A>C, B>D, B>E, C>F",
        python_code=_code_lines("tree"),
        renderer="tree",
    ),
    "graph": AlgorithmDefinition(
        key="graph",
        title="그래프",
        category="자료구조",
        subcategory="비선형 자료구조",
        badge="DS · 비선형",
        compare_text="그래프는 노드와 간선으로 관계를 표현하는 구조입니다. 트리보다 일반적이며, 순환과 복잡한 연결을 다룰 수 있습니다.",
        input_label="입력 형식: 간선 목록 | 시작 노드",
        input_description="예시: A-B, A-C, B-D, C-D | A",
        example="A-B, A-C, B-D, C-D | A",
        python_code=_code_lines("graph"),
        renderer="graph",
    ),
    "bubbleSort": AlgorithmDefinition(
        key="bubbleSort",
        title="버블 정렬",
        category="알고리즘",
        subcategory="정렬 알고리즘",
        badge="ALGO · 정렬",
        compare_text="버블 정렬은 인접한 두 원소를 반복 비교하며 큰 값을 뒤로 보내는 방식입니다. 교환이 자주 일어나 정렬의 기초 동작을 눈으로 이해하기 좋습니다.",
        input_label="입력 형식: 숫자 목록",
        input_description="예시: 7, 2, 9, 1, 4",
        example="7, 2, 9, 1, 4",
        python_code=_code_lines("bubbleSort"),
        renderer="sequence",
    ),
    "selectionSort": AlgorithmDefinition(
        key="selectionSort",
        title="선택 정렬",
        category="알고리즘",
        subcategory="정렬 알고리즘",
        badge="ALGO · 정렬",
        compare_text="선택 정렬은 남아 있는 구간에서 최솟값을 골라 앞쪽에 놓는 방식입니다. 매 단계의 목표가 분명해 정렬의 전략을 설명하기 좋습니다.",
        input_label="입력 형식: 숫자 목록",
        input_description="예시: 7, 2, 9, 1, 4",
        example="7, 2, 9, 1, 4",
        python_code=_code_lines("selectionSort"),
        renderer="sequence",
    ),
    "insertionSort": AlgorithmDefinition(
        key="insertionSort",
        title="삽입 정렬",
        category="알고리즘",
        subcategory="정렬 알고리즘",
        badge="ALGO · 정렬",
        compare_text="삽입 정렬은 이미 정렬된 구간에 새 값을 끼워 넣는 방식입니다. 손으로 카드를 정리하는 감각과 비슷해 직관적으로 이해하기 쉽습니다.",
        input_label="입력 형식: 숫자 목록",
        input_description="예시: 7, 2, 9, 1, 4",
        example="7, 2, 9, 1, 4",
        python_code=_code_lines("insertionSort"),
        renderer="sequence",
    ),
    "quickSort": AlgorithmDefinition(
        key="quickSort",
        title="퀵 정렬",
        category="알고리즘",
        subcategory="정렬 알고리즘",
        badge="ALGO · 정렬",
        compare_text="퀵 정렬은 피벗을 기준으로 작은 값과 큰 값을 나누는 분할 방식입니다. 평균적으로 매우 빠르며, 정렬 알고리즘 비교에서 대표적으로 다룹니다.",
        input_label="입력 형식: 숫자 목록",
        input_description="예시: 7, 2, 9, 1, 4, 6",
        example="7, 2, 9, 1, 4, 6",
        python_code=_code_lines("quickSort"),
        renderer="sequence",
    ),
    "mergeSort": AlgorithmDefinition(
        key="mergeSort",
        title="병합 정렬",
        category="알고리즘",
        subcategory="정렬 알고리즘",
        badge="ALGO · 정렬",
        compare_text="병합 정렬은 구간을 계속 반으로 나눈 뒤 정렬된 결과를 다시 합치는 방식입니다. 분할 정복의 전형적인 예시로 설명하기 좋습니다.",
        input_label="입력 형식: 숫자 목록",
        input_description="예시: 7, 2, 9, 1, 4, 6",
        example="7, 2, 9, 1, 4, 6",
        python_code=_code_lines("mergeSort"),
        renderer="sequence",
    ),
    "linearSearch": AlgorithmDefinition(
        key="linearSearch",
        title="순차 탐색",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 탐색",
        compare_text="선형 탐색은 처음부터 끝까지 하나씩 확인하는 가장 단순한 탐색입니다. 정렬 여부와 상관없이 적용된다는 점이 핵심입니다.",
        input_label="입력 형식: 목록 | 찾을 값",
        input_description="예시: 4, 7, 1, 9, 5 | 9",
        example="4, 7, 1, 9, 5 | 9",
        python_code=_code_lines("linearSearch"),
        renderer="search",
    ),
    "binarySearch": AlgorithmDefinition(
        key="binarySearch",
        title="이진 탐색",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 탐색",
        compare_text="이진 탐색은 정렬된 데이터에서 범위를 절반씩 줄이며 찾는 방식입니다. 조건이 맞으면 매우 빠르게 탐색할 수 있습니다.",
        input_label="입력 형식: 목록 | 찾을 값",
        input_description="예시: 7, 2, 9, 1, 4 | 4  (자동으로 정렬 후 탐색)",
        example="7, 2, 9, 1, 4 | 4",
        python_code=_code_lines("binarySearch"),
        renderer="search",
    ),
    "dfs": AlgorithmDefinition(
        key="dfs",
        title="DFS",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 그래프",
        compare_text="깊이 우선 탐색은 한 경로를 끝까지 내려간 뒤 되돌아오는 방식입니다. 재귀와 스택 개념을 연결해 설명하기 좋습니다.",
        input_label="입력 형식: 간선 목록 | 시작 노드",
        input_description="예시: A-B, A-C, B-D, C-E | A",
        example="A-B, A-C, B-D, D-E | A",
        python_code=_code_lines("dfs"),
        renderer="graph",
    ),
    "bfs": AlgorithmDefinition(
        key="bfs",
        title="BFS",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 그래프",
        compare_text="너비 우선 탐색은 가까운 노드부터 차례로 방문하는 방식입니다. 큐를 이용한 레벨 탐색 개념을 이해하기 좋습니다.",
        input_label="입력 형식: 간선 목록 | 시작 노드",
        input_description="예시: A-B, A-C, B-D, C-E | A",
        example="A-B, A-C, B-D, D-E | A",
        python_code=_code_lines("bfs"),
        renderer="graph",
    ),
    "preorder": AlgorithmDefinition(
        key="preorder",
        title="Preorder",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 트리",
        compare_text="루트-왼쪽-오른쪽 순으로 방문하는 트리 순회입니다.",
        input_label="입력 형식: 레벨 순회 값 목록",
        input_description="예시: A, B, C, D, E, null, F",
        example="A, B, C, D, E, null, F",
        python_code=_code_lines("preorder"),
        renderer="tree",
    ),
    "inorder": AlgorithmDefinition(
        key="inorder",
        title="Inorder",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 트리",
        compare_text="왼쪽-루트-오른쪽 순으로 방문하는 트리 순회입니다.",
        input_label="입력 형식: 레벨 순회 값 목록",
        input_description="예시: A, B, C, D, E, null, F",
        example="A, B, C, D, E, null, F",
        python_code=_code_lines("inorder"),
        renderer="tree",
    ),
    "postorder": AlgorithmDefinition(
        key="postorder",
        title="Postorder",
        category="알고리즘",
        subcategory="탐색 알고리즘",
        badge="ALGO · 트리",
        compare_text="왼쪽-오른쪽-루트 순으로 방문하는 트리 순회입니다.",
        input_label="입력 형식: 레벨 순회 값 목록",
        input_description="예시: A, B, C, D, E, null, F",
        example="A, B, C, D, E, null, F",
        python_code=_code_lines("postorder"),
        renderer="tree",
    ),
}


STEP_BUILDERS = {
    "array": (parse_number_list, build_array_steps),
    "list": (parse_number_list, build_list_steps),
    "stackOps": (parse_stack_commands, build_stack_steps),
    "queueOps": (parse_queue_commands, build_queue_steps),
    "tree": (parse_tree_edges, build_tree_steps),
    "graph": (parse_graph_payload, build_graph_steps),
    "bubbleSort": (parse_number_list, build_bubble_sort_steps),
    "selectionSort": (parse_number_list, build_selection_sort_steps),
    "insertionSort": (parse_number_list, build_insertion_sort_steps),
    "quickSort": (parse_number_list, build_quick_sort_steps),
    "mergeSort": (parse_number_list, build_merge_sort_steps),
    "linearSearch": (parse_search_payload, build_linear_search_steps),
    "binarySearch": (parse_binary_search_payload, build_binary_search_steps),
    "dfs": (parse_graph_payload, build_dfs_steps),
    "bfs": (parse_graph_payload, build_bfs_steps),
    "preorder": (parse_binary_tree_level, build_preorder_steps),
    "inorder": (parse_binary_tree_level, build_inorder_steps),
    "postorder": (parse_binary_tree_level, build_postorder_steps),
}


def serialize_algorithms() -> list[dict[str, Any]]:
    return [
        {
            "key": item.key,
            "title": item.title,
            "category": item.category,
            "subcategory": item.subcategory,
            "badge": item.badge,
            "compareText": item.compare_text,
            "inputLabel": item.input_label,
            "inputDescription": item.input_description,
            "example": item.example,
            "pythonCode": item.python_code,
            "renderer": item.renderer,
        }
        for item in ALGORITHMS.values()
    ]


_NO_TIMING_KEYS: frozenset = frozenset({"bfs", "dfs", "preorder", "inorder", "postorder"})


def run_algorithm(key: str, raw_input: str) -> dict[str, Any]:
    if key not in STEP_BUILDERS:
        raise KeyError(key)
    parser, builder = STEP_BUILDERS[key]
    parsed = parser(raw_input)

    # BFS·DFS·순회 3종은 시간 실측 제외
    if key in _NO_TIMING_KEYS:
        elapsed_ms = None
    else:
        # 알고리즘 자체 실행 시간만 측정 (시각화 스텝 생성 제외)
        algo_fn = CODE_FUNCTIONS.get(key)
        if algo_fn is not None:
            if isinstance(parsed, dict):
                # 탐색/그래프: 딕셔너리 언패킹
                algo_args: tuple = tuple(parsed.values())
            elif isinstance(parsed, list):
                algo_args = (parsed,)
            else:
                algo_args = (parsed,)
            t_start = time.perf_counter()
            try:
                algo_fn(*algo_args)
            except Exception:
                pass  # 실행 시간 측정 목적이므로 예외는 무시
            elapsed_ms = round((time.perf_counter() - t_start) * 1000, 4)
        else:
            elapsed_ms = 0.0

    steps = builder(parsed)

    return {
        "steps": steps,
        "pythonCode": ALGORITHMS[key].python_code,
        "renderer": ALGORITHMS[key].renderer,
        "executionTimeMs": elapsed_ms,
        "inputCount": len(parsed) if isinstance(parsed, list) else None,
    }


STRUCTURE_ACTIONS: dict[str, list[str]] = {
    "array": ["insert", "delete"],
    "list": ["insert", "delete"],
    "stackOps": ["push", "pop"],
    "queueOps": ["enqueue", "dequeue"],
    "tree": ["insert", "delete"],
    "graph": ["insert", "delete"],
}


def _to_number(value: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError("숫자 값을 입력해 주세요.") from exc


def _split_action_input(raw_value: str) -> list[str]:
    if not raw_value.strip():
        return []
    return [token.strip() for token in re.split(r"[|,]", raw_value) if token.strip()]


def _parse_array_insert_input(raw_value: str, size: int) -> tuple[int, float]:
    tokens = _split_action_input(raw_value)
    if len(tokens) == 1:
        return size, _to_number(tokens[0])
    if len(tokens) != 2:
        raise ValueError("배열 삽입은 `index, value` 또는 `value` 형식으로 입력해 주세요.")
    index = int(tokens[0])
    if index < 0 or index > size:
        raise ValueError("배열 삽입 위치가 범위를 벗어났습니다.")
    return index, _to_number(tokens[1])


def _parse_list_insert_input(raw_value: str, size: int) -> tuple[int, str]:
    tokens = _split_action_input(raw_value)
    if len(tokens) == 1:
        return size, tokens[0]
    if len(tokens) < 2:
        raise ValueError("리스트 삽입은 `index, value` 또는 `value` 형식으로 입력해 주세요.")
    index = int(tokens[0])
    if index < 0 or index > size:
        raise ValueError("리스트 삽입 위치가 범위를 벗어났습니다.")
    return index, ",".join(tokens[1:]).strip()


def _parse_delete_index(raw_value: str, size: int) -> int:
    tokens = _split_action_input(raw_value)
    if not tokens:
        return size - 1
    if len(tokens) != 1:
        raise ValueError("삭제는 비우거나 `index` 하나만 입력해 주세요.")
    index = int(tokens[0])
    if index < 0 or index >= size:
        raise ValueError("삭제 위치가 범위를 벗어났습니다.")
    return index


def _structure_code(key: str, action: str) -> list[str]:
    mapping = {
        ("array", "insert"): [
            "def array_insert(arr, index, value):",
            "    arr.append(None)          # 공간 확보",
            "    i = len(arr) - 1",
            "    while i > index:          # 뒤로 shift",
            "        arr[i] = arr[i - 1]",
            "        i -= 1",
            "    arr[index] = value        # 삽입",
            "    return arr",
        ],
        ("array", "delete"): [
            "def array_delete(arr, index):",
            "    i = index",
            "    while i < len(arr) - 1:   # 앞으로 shift",
            "        arr[i] = arr[i + 1]",
            "        i += 1",
            "    arr.pop()                 # 마지막 빈 칸 제거",
            "    return arr",
        ],
        ("list", "insert"): [
            "def list_insert(head, index, value):",
            "    node = Node(value)        # 새 노드 생성",
            "    if index == 0:",
            "        node.next = head      # 새 노드가 head 가리킴",
            "        head = node",
            "        return head",
            "    cur = head",
            "    for _ in range(index - 1):  # 삽입 위치까지 이동",
            "        cur = cur.next",
            "    node.next = cur.next      # 포인터 교체",
            "    cur.next = node",
            "    return head",
        ],
        ("list", "delete"): [
            "def list_delete(head, index):",
            "    if index == 0:",
            "        head = head.next      # head 포인터만 이동",
            "        return head",
            "    cur = head",
            "    for _ in range(index - 1):  # 삭제 위치 직전까지 이동",
            "        cur = cur.next",
            "    cur.next = cur.next.next  # 포인터 건너뜀",
            "    return head",
        ],
        ("stackOps", "push"): [
            "def stack_push(stack, top, value):",
            "    top += 1              # top 포인터 증가",
            "    stack[top] = value    # top 위치에 저장",
            "    return top",
        ],
        ("stackOps", "pop"): [
            "def stack_pop(stack, top):",
            "    if top < 0:           # 스택이 비어 있음",
            "        return top",
            "    value = stack[top]    # top 값 읽기",
            "    top -= 1              # top 포인터 감소",
            "    return top, value",
        ],
        ("queueOps", "enqueue"): [
            "def queue_enqueue(queue, rear, value):",
            "    rear += 1             # rear 포인터 증가",
            "    queue[rear] = value   # rear 위치에 저장",
            "    return rear",
        ],
        ("queueOps", "dequeue"): [
            "def queue_dequeue(queue, front, rear):",
            "    if front > rear:      # 큐가 비어 있음",
            "        return front",
            "    value = queue[front]  # front 값 읽기",
            "    front += 1            # front 포인터 증가",
            "    return front, value",
        ],
        ("tree", "insert"): [
            "def tree_insert(edges, parent, child):",
            "    queue = deque([root])",
            "    while queue:",
            "        node = queue.popleft()",
            "        if node == parent:",
            "            edges.append((parent, child))",
            "            return edges",
            "        queue.extend(children[node])",
        ],
        ("tree", "delete"): [
            "def tree_delete(edges, target):",
            "    queue = deque([root])",
            "    while queue:",
            "        node = queue.popleft()",
            "        if node == target: break",
            "    parent = parents_map[target]",
            "    new_edges = [(p,c) for p,c in edges",
            "                 if p != target and c != target]",
            "    for ch in children_map[target]:",
            "        new_edges.append((parent, ch))",
            "    return new_edges",
        ],
        ("graph", "insert"): [
            "def graph_add_vertex(nodes, label):",
            "    nodes.append(label)",
            "",
            "def graph_add_edge(nodes, edges, u, v):",
            "    if u not in nodes: nodes.append(u)",
            "    if v not in nodes: nodes.append(v)",
            "    edges.append((u, v))",
        ],
        ("graph", "delete"): [
            "def graph_del_vertex(nodes, edges, v):",
            "    nodes.remove(v)",
            "    edges[:] = [e for e in edges",
            "                if v not in e]",
            "",
            "def graph_del_edge(edges, u, v):",
            "    edges[:] = [e for e in edges",
            "                if e != (u,v) and e != (v,u)]",
        ],
    }
    return mapping[(key, action)]


def _array_action_mod(state: dict[str, Any], action: str, raw_value: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    values = [float(value) for value in state.get("values", [])]
    if action == "insert":
        # array insert 코드: 1:def / 2:arr.append(None) / 3:i=len-1 / 4:while i>index
        # 5:arr[i]=arr[i-1] / 6:i-=1 / 7:arr[index]=value / 8:return
        index, value = _parse_array_insert_input(raw_value, len(values))
        next_values = values[:index] + [value] + values[index:]
        return [
            {"state": {"values": values[:], "incoming": value, "insertIndex": index, "layout": "array"}, "message": f"arr.append(None) — 공간을 확보합니다.", "activeLines": [2]},
            {"state": {"values": values[:], "incoming": value, "insertIndex": index, "shiftFrom": index, "layout": "array"}, "message": f"i={len(values)} → {index}까지 원소를 한 칸씩 뒤로 shift합니다.", "activeLines": [3, 4, 5, 6]},
            {"state": {"values": next_values[:], "compare": [index], "layout": "array"}, "message": f"arr[{index}] = {_fmt(value)}. 삽입 완료.", "activeLines": [7]},
        ], {"values": next_values}

    if not values:
        raise ValueError("삭제할 값이 없습니다.")
    # array delete 코드: 1:def / 2:i=index / 3:while i<len-1
    # 4:arr[i]=arr[i+1] / 5:i+=1 / 6:arr.pop() / 7:return
    index = _parse_delete_index(raw_value, len(values))
    next_values = values[:index] + values[index + 1:]
    return [
        {"state": {"values": values[:], "compare": [index], "layout": "array"}, "message": f"i={index}. {index}번 이후 원소를 앞으로 shift합니다.", "activeLines": [2, 3, 4, 5]},
        {"state": {"values": next_values[:], "layout": "array"}, "message": "arr.pop() — 마지막 빈 칸을 제거합니다.", "activeLines": [6]},
    ], {"values": next_values}


def _list_action_mod(state: dict[str, Any], action: str, raw_value: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    values = [str(value) for value in state.get("values", [])]
    if action == "insert":
        # list insert 코드: 1:def / 2:node=Node(value) / 3:if index==0
        # 4:node.next=head / 5:head=node / 6:return / 7:cur=head
        # 8:for range(index-1) / 9:cur=cur.next / 10:node.next=cur.next / 11:cur.next=node / 12:return
        index, value = _parse_list_insert_input(raw_value, len(values))
        next_values = values[:index] + [value] + values[index:]
        if index == 0:
            return [
                {"state": {"values": values[:], "incoming": value, "insertIndex": index, "previewInsert": True, "layout": "linked"}, "message": f"node = Node({value}) — 새 노드를 생성합니다.", "activeLines": [2]},
                {"state": {"values": next_values[:], "compare": [0], "layout": "linked"}, "message": f"index==0이므로 node.next=head, head=node. head를 교체합니다.", "activeLines": [3, 4, 5]},
            ], {"values": next_values}
        return [
            {"state": {"values": values[:], "incoming": value, "insertIndex": index, "previewInsert": True, "layout": "linked"}, "message": f"node = Node({value}) — 새 노드를 생성합니다.", "activeLines": [2]},
            {"state": {"values": values[:], "compare": [index - 1], "layout": "linked"}, "message": f"cur을 {index - 1}번 노드까지 이동합니다.", "activeLines": [7, 8, 9]},
            {"state": {"values": next_values[:], "compare": [index], "layout": "linked"}, "message": f"node.next=cur.next, cur.next=node — 포인터를 교체합니다.", "activeLines": [10, 11]},
        ], {"values": next_values}

    if not values:
        raise ValueError("삭제할 노드가 없습니다.")
    # list delete 코드: 1:def / 2:if index==0 / 3:head=head.next / 4:return
    # 5:cur=head / 6:for range(index-1) / 7:cur=cur.next / 8:cur.next=cur.next.next / 9:return
    index = _parse_delete_index(raw_value, len(values))
    next_values = values[:index] + values[index + 1:]
    if index == 0:
        return [
            {"state": {"values": values[:], "compare": [0], "layout": "linked"}, "message": "index==0이므로 head=head.next. head 포인터만 이동합니다.", "activeLines": [2, 3]},
            {"state": {"values": next_values[:], "layout": "linked"}, "message": "head 교체 완료.", "activeLines": [4]},
        ], {"values": next_values}
    return [
        {"state": {"values": values[:], "compare": [index - 1], "layout": "linked"}, "message": f"cur을 {index - 1}번 노드까지 이동합니다.", "activeLines": [5, 6, 7]},
        {"state": {"values": next_values[:], "layout": "linked"}, "message": f"cur.next=cur.next.next — {index}번 노드를 건너뜁니다.", "activeLines": [8]},
    ], {"values": next_values}


def _stack_action(state: dict[str, Any], action: str, raw_value: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stack = [float(value) for value in state.get("values", [])]
    if action == "push":
        value = _to_number(raw_value)
        next_stack = stack[:] + [value]
        return [
            # push 코드: 1:def / 2:top+=1 / 3:stack[top]=value / 4:return
            {"state": {"stack": stack[:], "action": "push", "incoming": value}, "message": f"top += 1. {_fmt(value)}를 올릴 자리를 만듭니다.", "activeLines": [2]},
            {"state": {"stack": next_stack[:], "action": "push-done"}, "message": f"stack[top] = {_fmt(value)}. push 완료.", "activeLines": [3]},
        ], {"values": next_stack}

    if not stack:
        raise ValueError("pop 할 값이 없습니다.")
    removed = stack[-1]
    next_stack = stack[:-1]
    return [
        # pop 코드: 1:def / 2:if top<0 / 3:return / 4:value=stack[top] / 5:top-=1 / 6:return
        {"state": {"stack": stack[:], "action": "pop", "removed": removed}, "message": f"stack[top] = {_fmt(removed)}를 읽습니다.", "activeLines": [4]},
        {"state": {"stack": next_stack[:], "action": "pop-done", "removed": removed}, "message": "top -= 1. pop 완료.", "activeLines": [5]},
    ], {"values": next_stack}


def _queue_action_mod(state: dict[str, Any], action: str, raw_value: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    queue = [float(value) for value in state.get("values", [])]
    if action == "enqueue":
        value = _to_number(raw_value)
        next_queue = queue[:] + [value]
        return [
            # enqueue 코드: 1:def / 2:rear+=1 / 3:queue[rear]=value / 4:return
            {"state": {"queue": queue[:], "action": "enqueue", "incoming": value}, "message": f"rear += 1. {_fmt(value)}를 넣을 자리를 만듭니다.", "activeLines": [2]},
            {"state": {"queue": next_queue[:], "action": "enqueue-done"}, "message": f"queue[rear] = {_fmt(value)}. enqueue 완료.", "activeLines": [3]},
        ], {"values": next_queue}

    if not queue:
        raise ValueError("dequeue 할 값이 없습니다.")
    removed = queue[0]
    next_queue = queue[1:]
    return [
        # dequeue 코드: 1:def / 2:if front>rear / 3:return / 4:value=queue[front] / 5:front+=1 / 6:return
        {"state": {"queue": queue[:], "action": "dequeue", "removed": removed, "compare": [0]}, "message": f"queue[front] = {_fmt(removed)}를 읽습니다.", "activeLines": [4]},
        {"state": {"queue": next_queue[:], "action": "dequeue-done"}, "message": "front += 1. dequeue 완료.", "activeLines": [5]},
    ], {"values": next_queue}


def _tree_action(state: dict[str, Any], action: str, raw_value: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    # 상태는 edges 기반: {"edges": [["A","B"], ...]}
    # 이전 values 기반 상태와 호환: values가 있으면 edges로 변환
    raw_edges: list[tuple[str, str]] = []
    if state.get("edges"):
        raw_edges = [tuple(e) for e in state["edges"]]  # type: ignore[misc]
    elif state.get("values"):
        # 이전 포맷 호환: values 배열을 완전 이진트리 간선으로 변환
        vals = [_fmt(float(v)) for v in state["values"]]
        for i in range(1, len(vals)):
            raw_edges.append((vals[(i - 1) // 2], vals[i]))

    steps: list[dict[str, Any]] = []

    if action == "insert":
        raw = raw_value.strip()
        if ">" in raw:
            parts = [t.strip() for t in raw.split(">", 1)]
            parent_label, child_label = parts[0], parts[1]
        else:
            child_label = raw
            parent_label = None  # type: ignore[assignment]

        if not child_label:
            raise ValueError("삽입할 노드 값을 입력하세요. 형식: `부모>자식` 또는 루트면 `값`")

        all_nodes: set[str] = set()
        for p, c in raw_edges:
            all_nodes.add(p)
            all_nodes.add(c)

        if child_label in all_nodes:
            raise ValueError(f"'{child_label}' 노드가 이미 존재합니다.")

        if parent_label is None:
            # 루트 삽입 (트리가 비어 있을 때만)
            if all_nodes:
                raise ValueError("트리가 비어 있지 않습니다. `부모>자식` 형식으로 입력하세요.")
            steps.append({
                "state": _tree_state_from_edges([(child_label, "__empty__")], highlight_nodes=[child_label]),
                "message": f"'{child_label}'를 루트 노드로 추가합니다.",
                "activeLines": [1],
            })
            return steps, {"edges": [], "root": child_label}

        # 부모 노드가 트리에 존재하는지 확인
        if state.get("root"):
            all_nodes.add(str(state["root"]))

        # 부모 노드가 트리에 존재하는지 확인
        if parent_label not in all_nodes:
            raise ValueError(f"부모 노드 '{parent_label}'을 찾을 수 없습니다.")

        # ── BFS로 부모 노드 탐색 애니메이션 ──────────────────────────────
        children_map: dict[str, list[str]] = {}
        parents_map: dict[str, str] = {}
        for p, c in raw_edges:
            children_map.setdefault(p, []).append(c)
            parents_map[c] = p
        roots = [n for n in all_nodes if n not in parents_map]
        if not roots and state.get("root"):
            roots = [str(state["root"])]
        bfs_root = roots[0] if roots else (raw_edges[0][0] if raw_edges else parent_label)

        visited_path: list[str] = []
        bfs_q: deque[str] = deque([bfs_root])
        visited_set: set[str] = set()
        while bfs_q:
            node = bfs_q.popleft()
            if node in visited_set:
                continue
            visited_set.add(node)
            visited_path.append(node)
            found_parent = node == parent_label
            current_display = _tree_state_from_edges(raw_edges, highlight_nodes=visited_path[:]) if raw_edges else {"nodes": [{"id": bfs_root, "label": bfs_root, "x": 320, "y": 56, "highlight": True}], "edges": []}
            steps.append({
                "state": current_display,
                "message": (
                    f"부모 '{parent_label}' 발견! 자식 '{child_label}'을 연결합니다."
                    if found_parent
                    else f"'{node}' 방문 중... (BFS 탐색)"
                ),
                "activeLines": [3, 4] if not found_parent else [5],
            })
            if found_parent:
                break
            for ch in children_map.get(node, []):
                bfs_q.append(ch)

        # ── 실제 삽입 ────────────────────────────────────────────────────
        new_edges = raw_edges + [(parent_label, child_label)]
        steps.append({
            "state": _tree_state_from_edges(new_edges, highlight_nodes=[parent_label, child_label]),
            "message": f"'{parent_label}'의 자식으로 '{child_label}'를 삽입했습니다.",
            "activeLines": [6, 7],
        })
        return steps, {"edges": [list(e) for e in new_edges]}

    else:  # delete
        raw = raw_value.strip()
        if not raw:
            raise ValueError("삭제할 노드 이름을 입력하세요.")

        all_nodes = set()
        for p, c in raw_edges:
            all_nodes.add(p)
            all_nodes.add(c)
        # 단독 루트 (간선 없는 경우)
        if not all_nodes and state.get("root"):
            all_nodes.add(str(state["root"]))

        if raw not in all_nodes:
            raise ValueError(f"'{raw}' 노드를 찾을 수 없습니다.")

        # ── BFS로 삭제 노드 탐색 애니메이션 ─────────────────────────────
        children_map = {}
        parents_map = {}
        for p, c in raw_edges:
            children_map.setdefault(p, []).append(c)
            parents_map[c] = p
        roots = [n for n in all_nodes if n not in parents_map]
        bfs_root = roots[0] if roots else (raw_edges[0][0] if raw_edges else raw)

        visited_path = []
        bfs_q = deque([bfs_root])
        visited_set = set()
        while bfs_q:
            node = bfs_q.popleft()
            if node in visited_set:
                continue
            visited_set.add(node)
            visited_path.append(node)
            found_target = node == raw
            steps.append({
                "state": _tree_state_from_edges(raw_edges, highlight_nodes=visited_path[:]) if raw_edges else {"nodes": [], "edges": []},
                "message": (
                    f"삭제 대상 '{raw}' 발견!"
                    if found_target
                    else f"'{node}' 방문 중... (BFS 탐색)"
                ),
                "activeLines": [3, 4] if not found_target else [5],
            })
            if found_target:
                break
            for ch in children_map.get(node, []):
                bfs_q.append(ch)

        # ── 삭제: 자식을 부모 노드에 연결 ────────────────────────────────
        parent_of_del = parents_map.get(raw)
        children_of_del = children_map.get(raw, [])

        # 삭제 노드 관련 간선 제거
        new_edges = [(p, c) for p, c in raw_edges if p != raw and c != raw]

        if parent_of_del:
            # 삭제 노드의 자식들을 부모에 직접 연결 (부모로 올림)
            for ch in children_of_del:
                new_edges.append((parent_of_del, ch))
            child_msg = f", 자식 {children_of_del}을 '{parent_of_del}'에 연결" if children_of_del else ""
            steps.append({
                "state": _tree_state_from_edges(new_edges, highlight_nodes=children_of_del) if new_edges else {"nodes": [], "edges": []},
                "message": f"'{raw}'를 삭제했습니다{child_msg}.",
                "activeLines": [6, 7, 8],
            })
        else:
            # 루트 삭제
            if children_of_del:
                new_root = children_of_del[0]
                # 나머지 자식은 새 루트의 자식으로 재연결
                for ch in children_of_del[1:]:
                    new_edges.append((new_root, ch))
                steps.append({
                    "state": _tree_state_from_edges(new_edges, highlight_nodes=[new_root]) if new_edges else {"nodes": [], "edges": []},
                    "message": f"루트 '{raw}'를 삭제했습니다. '{new_root}'이 새 루트가 됩니다.",
                    "activeLines": [6, 7],
                })
            else:
                steps.append({
                    "state": {"nodes": [], "edges": []},
                    "message": f"'{raw}'를 삭제했습니다. 트리가 비었습니다.",
                    "activeLines": [6],
                })

        return steps, {"edges": [list(e) for e in new_edges]}


def _graph_action(state: dict[str, Any], action: str, raw_value: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    nodes: list[str] = [str(n) for n in state.get("nodes", [])]
    edges: list[tuple[str, str]] = [tuple(e) for e in state.get("edges", [])]  # type: ignore[misc]
    raw = raw_value.strip()
    steps: list[dict[str, Any]] = []

    if action == "insert":
        # 형식: "A"  → 정점만 추가
        #       "A-B"→ 간선 추가 (없는 정점은 자동 생성)
        if "-" in raw:
            # ── 간선 삽입 ────────────────────────────────────────────────
            parts = [t.strip() for t in raw.split("-", 1)]
            u, v = parts[0], parts[1]
            if not u or not v:
                raise ValueError("간선 형식은 `A-B` 입니다.")
            if (u, v) in edges or (v, u) in edges:
                raise ValueError(f"'{u}-{v}' 간선이 이미 존재합니다.")

            added_nodes: list[str] = []
            next_nodes = nodes[:]
            for node in (u, v):
                if node not in next_nodes:
                    next_nodes.append(node)
                    added_nodes.append(node)

            node_msg = f" (정점 {added_nodes} 자동 추가)" if added_nodes else ""
            steps.append({
                "state": _graph_state(edges, current=u),
                "message": f"'{u}-{v}' 간선을 삽입합니다{node_msg}.",
                "activeLines": [1, 2],
            })
            next_edges = edges + [(u, v)]
            steps.append({
                "state": _graph_state(next_edges, current=u, frontier=[v]),
                "message": f"'{u}'와 '{v}'를 연결하는 간선을 추가했습니다.",
                "activeLines": [3, 4],
            })
            return steps, {"nodes": next_nodes, "edges": [list(e) for e in next_edges]}
        else:
            # ── 정점 삽입 ────────────────────────────────────────────────
            label = raw or f"V{len(nodes) + 1}"
            if label in nodes:
                raise ValueError(f"정점 '{label}'이 이미 존재합니다.")
            steps.append({
                "state": _graph_state(edges, current=nodes[-1] if nodes else None),
                "message": f"정점 '{label}'을 그래프에 추가합니다.",
                "activeLines": [1, 2],
            })
            next_nodes = nodes + [label]
            steps.append({
                "state": _graph_state(edges, current=label),
                "message": f"정점 '{label}'을 추가했습니다. (간선 없음 — 고립 정점)",
                "activeLines": [2, 3],
            })
            return steps, {"nodes": next_nodes, "edges": [list(e) for e in edges]}

    else:  # delete
        # 형식: "A"  → 정점 삭제 (연결된 간선 모두 제거)
        #       "A-B"→ 간선만 삭제
        if "-" in raw:
            # ── 간선 삭제 ────────────────────────────────────────────────
            parts = [t.strip() for t in raw.split("-", 1)]
            u, v = parts[0], parts[1]
            if (u, v) not in edges and (v, u) not in edges:
                raise ValueError(f"'{u}-{v}' 간선이 존재하지 않습니다.")
            steps.append({
                "state": _graph_state(edges, current_edge=(u, v)),
                "message": f"'{u}-{v}' 간선을 삭제합니다.",
                "activeLines": [1, 2],
            })
            next_edges = [e for e in edges if e not in {(u, v), (v, u)}]
            steps.append({
                "state": _graph_state(next_edges),
                "message": f"'{u}-{v}' 간선을 제거했습니다. 정점은 유지됩니다.",
                "activeLines": [3, 4],
            })
            return steps, {"nodes": nodes[:], "edges": [list(e) for e in next_edges]}
        else:
            # ── 정점 삭제 ────────────────────────────────────────────────
            if not raw:
                raise ValueError("삭제할 정점 이름을 입력하세요. 형식: `A` 또는 간선은 `A-B`")
            if raw not in nodes:
                raise ValueError(f"정점 '{raw}'이 존재하지 않습니다.")
            related = [(u, v) for u, v in edges if u == raw or v == raw]
            steps.append({
                "state": _graph_state(edges, current=raw),
                "message": f"정점 '{raw}'과 연결된 간선 {len(related)}개를 먼저 제거합니다.",
                "activeLines": [1, 2],
            })
            next_nodes = [n for n in nodes if n != raw]
            next_edges = [e for e in edges if raw not in e]
            steps.append({
                "state": _graph_state(next_edges, current=next_nodes[-1] if next_nodes else None),
                "message": f"정점 '{raw}'과 모든 연결 간선을 삭제했습니다.",
                "activeLines": [3, 4, 5],
            })
            return steps, {"nodes": next_nodes, "edges": [list(e) for e in next_edges]}


def run_structure_action(key: str, structure_state: dict[str, Any] | None, action: str, raw_value: str = "") -> dict[str, Any]:
    if key not in STRUCTURE_ACTIONS:
        raise KeyError(key)
    if action not in STRUCTURE_ACTIONS[key]:
        raise ValueError("지원하지 않는 동작입니다.")
    state = structure_state or {}

    if key == "array":
        steps, next_state = _array_action_mod(state, action, raw_value)
    elif key == "list":
        steps, next_state = _list_action_mod(state, action, raw_value)
    elif key == "stackOps":
        steps, next_state = _stack_action(state, action, raw_value)
    elif key == "queueOps":
        steps, next_state = _queue_action_mod(state, action, raw_value)
    elif key == "tree":
        steps, next_state = _tree_action(state, action, raw_value)
    else:
        steps, next_state = _graph_action(state, action, raw_value)

    renderer = ALGORITHMS[key].renderer
    if key == "array":
        renderer = "array"
    elif key == "list":
        renderer = "linked"

    return {
        "steps": steps,
        "structureState": next_state,
        "pythonCode": _structure_code(key, action),
        "renderer": renderer,
    }