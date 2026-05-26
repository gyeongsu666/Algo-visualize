const algorithms = window.__ALGORITHMS__ || [];
const STORAGE_KEY = "dsv-compare-config";

const setupCatalogKeys = ["array", "list", "stackOps", "queueOps", "tree", "graph"];
const algorithmCatalogKeys = ["selectionSort", "insertionSort", "mergeSort", "quickSort", "bubbleSort", "linearSearch", "binarySearch", "bfs", "dfs", "preorder", "inorder", "postorder"];

const cleanDisplayTitles = {
  array: "배열 (Array)",
  list: "리스트 (List)",
  stackOps: "스택 (Stack)",
  queueOps: "큐 (Queue)",
  tree: "트리 (Tree)",
  graph: "그래프 (Graph)",
  bubbleSort: "버블 정렬 (Bubble Sort)",
  selectionSort: "선택 정렬 (Selection Sort)",
  insertionSort: "삽입 정렬 (Insertion Sort)",
  mergeSort: "병합 정렬 (Merge Sort)",
  quickSort: "퀵 정렬 (Quick Sort)",
  linearSearch: "순차 탐색 (Linear Search)",
  binarySearch: "이진 탐색 (Binary Search)",
  bfs: "너비 우선 탐색 (BFS)",
  dfs: "깊이 우선 탐색 (DFS)",
  preorder: "전위 순회 (Preorder)",
  inorder: "중위 순회 (Inorder)",
  postorder: "후위 순회 (Postorder)",
};

const cleanStructureCardMeta = {
  array: { tags: ["인덱스", "연속 메모리", "시프트"], summary: "인덱스로 빠르게 접근할 수 있는 가장 기본적인 선형 구조" },
  list: { tags: ["노드", "포인터", "연결 변경"], summary: "노드와 연결을 바꾸며 삽입과 삭제를 표현하는 연결 구조" },
  stackOps: { tags: ["LIFO", "top", "되돌리기"], summary: "가장 나중에 들어온 데이터가 먼저 나오는 구조" },
  queueOps: { tags: ["FIFO", "front/rear", "대기열"], summary: "먼저 들어온 데이터가 먼저 처리되는 대기열 구조" },
  tree: { tags: ["계층", "부모/자식", "순회"], summary: "부모와 자식 관계로 계층을 표현하는 비선형 구조" },
  graph: { tags: ["노드", "간선", "네트워크"], summary: "노드와 간선으로 다양한 관계를 표현하는 연결 구조" },
};

const cleanAlgorithmCardMeta = {
  selectionSort: { tags: ["최솟값", "선택", "교환"], summary: "매 단계의 최솟값을 선택해 앞쪽에 배치하는 정렬" },
  insertionSort: { tags: ["삽입", "부분 정렬", "이동"], summary: "정렬된 구간에 값을 끼워 넣으며 완성하는 정렬" },
  mergeSort: { tags: ["분할 정복", "병합", "재귀"], summary: "나누고 합치며 전체를 정렬하는 대표적인 분할 정복" },
  quickSort: { tags: ["피벗", "분할", "재귀"], summary: "피벗 기준으로 작은 값과 큰 값을 나누는 정렬" },
  bubbleSort: { tags: ["인접 비교", "교환", "반복"], summary: "인접 원소를 비교하며 큰 값을 뒤로 보내는 정렬" },
  linearSearch: { tags: ["순차 확인", "비정렬", "기본 탐색"], summary: "앞에서부터 차례대로 값을 확인하는 가장 기본적인 탐색" },
  binarySearch: { tags: ["정렬 필요", "중앙값", "범위 축소"], summary: "탐색 범위를 절반씩 줄여 빠르게 찾는 탐색" },
  bfs: { tags: ["큐", "레벨", "가까운 순서"], summary: "가까운 노드부터 넓게 탐색하는 방식" },
  dfs: { tags: ["스택", "깊이 우선", "되돌아오기"], summary: "한 경로를 깊게 내려간 뒤 되돌아오는 탐색" },
  preorder: { tags: ["루트 먼저", "트리", "순회"], summary: "루트를 먼저 방문하는 트리 순회" },
  inorder: { tags: ["왼쪽-루트-오른쪽", "트리", "순회"], summary: "왼쪽, 루트, 오른쪽 순서의 트리 순회" },
  postorder: { tags: ["자식 먼저", "트리", "순회"], summary: "자식들을 먼저 방문한 뒤 루트를 처리하는 순회" },
};

const cleanDetailMap = {
  array: "배열은 연속된 메모리 공간에 값을 순서대로 저장합니다. 인덱스로 빠르게 접근할 수 있지만, 중간에 값을 넣거나 빼면 뒤쪽 원소들을 다시 정렬해야 합니다.",
  list: "리스트는 노드가 다음 노드를 가리키는 연결 구조입니다. 메모리상 연속적일 필요가 없고, 중간 연결을 바꾸며 삽입과 삭제를 표현하기 좋습니다.",
  stackOps: "스택은 마지막에 들어온 데이터가 가장 먼저 나가는 LIFO 구조입니다. top을 기준으로 push와 pop이 일어나며, 되돌리기나 함수 호출 흐름을 설명하기 좋습니다.",
  queueOps: "큐는 먼저 들어온 데이터가 먼저 나가는 FIFO 구조입니다. front에서 삭제되고 rear에서 삽입되므로 처리 대기열의 흐름을 직관적으로 보여줍니다.",
  tree: "트리는 부모-자식 관계로 계층을 표현하는 구조입니다. 루트에서 시작해 가지를 따라 내려가며 순회와 삽입, 삭제 개념을 설명하기 좋습니다.",
  graph: "그래프는 노드와 간선으로 관계를 표현합니다. 순환, 다대다 연결, 네트워크 구조처럼 트리보다 일반적인 연결을 다룰 때 적합합니다.",
  bubbleSort: "인접한 두 값을 반복 비교하며 큰 값을 뒤로 보내는 정렬입니다. 교환이 여러 번 일어나므로 비교와 스왑의 의미를 이해하기 쉽습니다.",
  selectionSort: "현재 구간에서 가장 작은 값을 찾아 앞쪽과 교환하는 정렬입니다. 매 단계의 목표가 분명해 정렬 과정의 큰 흐름을 파악하기 좋습니다.",
  insertionSort: "이미 정렬된 구간에 새 값을 끼워 넣는 방식의 정렬입니다. 손으로 카드를 정리하는 방식과 비슷해 학습용으로 직관적입니다.",
  mergeSort: "배열을 작은 구간으로 나누고 다시 병합하며 정렬합니다. 분할 정복의 대표 예시로 전체 문제를 작은 문제로 나누는 발상을 보여줍니다.",
  quickSort: "피벗을 기준으로 작은 값과 큰 값을 나누는 정렬입니다. 분할은 빠르지만 피벗 선택에 따라 성능 차이가 생긴다는 점이 핵심입니다.",
  linearSearch: "처음부터 끝까지 하나씩 비교하며 목표값을 찾습니다. 정렬 여부와 관계없이 동작하는 가장 기본적인 탐색입니다.",
  binarySearch: "정렬된 데이터에서 가운데 값을 기준으로 탐색 범위를 절반씩 줄여 나갑니다. 조건만 맞으면 매우 빠르게 탐색할 수 있습니다.",
  bfs: "BFS는 가까운 노드부터 넓게 방문합니다. 큐를 사용해 같은 거리의 노드들을 차례대로 처리하는 흐름이 핵심입니다.",
  dfs: "DFS는 한 경로를 끝까지 내려간 뒤 되돌아옵니다. 스택 또는 재귀 호출 흐름과 함께 생각하면 이해가 쉽습니다.",
  preorder: "루트를 먼저 방문한 뒤 왼쪽, 오른쪽 서브트리를 순서대로 탐색합니다.",
  inorder: "왼쪽 서브트리, 루트, 오른쪽 서브트리 순서로 탐색합니다. 이진 탐색 트리에서는 정렬된 결과를 얻을 수 있습니다.",
  postorder: "왼쪽과 오른쪽 서브트리를 먼저 방문한 뒤 마지막에 루트를 처리합니다.",
};

const cleanApplications = {
  array: "테이블 데이터, 이미지 픽셀 저장, 버퍼, 동적 배열의 기반 구조",
  list: "재생 목록, 메모리 블록 연결, 잦은 중간 삽입/삭제가 필요한 구조",
  stackOps: "미로 탐색, 괄호 검사, 실행 취소, 함수 호출 스택",
  queueOps: "작업 스케줄링, 프린터 대기열, BFS, 메시지 처리 큐",
  tree: "파일 시스템, 조직도, DOM 구조, 의사결정 트리",
  graph: "지도 경로, 소셜 네트워크, 추천 관계, 통신망 모델링",
};

const cleanFunctions = {
  array: [
    "insert(index, value) -> index 위치에 값을 넣고 뒤 원소를 한 칸씩 이동",
    "delete(index) -> index 위치의 값을 삭제하고 뒤 원소를 앞으로 당김",
    "items[index] -> 인덱스로 즉시 접근",
  ],
  list: [
    "insert(index, value) -> index 앞에 새 노드를 연결",
    "delete(index) -> index 위치의 노드를 제거하고 연결을 다시 잇기",
    "node.next -> 다음 노드를 가리키는 참조",
  ],
  stackOps: [
    "append(value) / push(value) -> top에 값 추가",
    "items.pop() -> top 값 제거",
    "items[-1] -> top 값 확인",
  ],
  queueOps: [
    "append(value) -> rear에 값 추가",
    "popleft() / dequeue() -> front 값 제거",
    "queue[0], queue[-1] -> front와 rear 확인",
  ],
  tree: [
    "insert(value) -> 규칙에 따라 새 노드 추가",
    "delete(value) -> 대상 노드 제거 후 구조 재정리",
    "preorder(), inorder(), postorder() -> 순회 방식 선택",
  ],
  graph: [
    "add_node(label) -> 새 노드 추가",
    "add_edge(a, b) -> 노드 사이 간선 연결",
    "neighbors(node) -> 인접 노드 확인",
  ],
};

const cleanComplexity = {
  // 자료구조
  array: {
    best: "접근 O(1) — 인덱스 직접 접근",
    average: "삽입·삭제 O(n) — 뒤 원소 shift 필요",
    worst: "맨 앞 삽입·삭제 O(n) / 공간 O(n)",
  },
  list: {
    best: "포인터 변경 O(1) — 삽입·삭제 위치 참조를 이미 알고 있을 때",
    average: "접근·탐색 O(n) — head부터 순차 이동",
    worst: "맨 끝 접근 O(n) / 공간 O(n)",
  },
  stackOps: {
    best: "Push O(1)",
    average: "Pop O(1)",
    worst: "Peek O(1) / 공간 O(n)",
  },
  queueOps: {
    best: "Enqueue O(1)",
    average: "Dequeue O(1)",
    worst: "Front 확인 O(1) / 공간 O(n)",
  },
  tree: {
    best: "순회 O(n) — 모든 노드 방문",
    average: "삽입·삭제 O(n) — 일반 트리, 탐색 후 연결 변경",
    worst: "편향 트리 탐색 O(n) / 공간 O(n)",
  },
  graph: {
    best: "인접 리스트 탐색 O(V+E)",
    average: "DFS·BFS 모두 O(V+E)",
    worst: "완전 그래프(E=V²) O(V²) / 공간 O(V+E)",
  },
  // 정렬
  bubbleSort: {
    best: "O(n²) — 조기종료 없는 구현, 항상 n² 비교",
    average: "O(n²)",
    worst: "O(n²) / 공간 O(1)",
  },
  selectionSort: {
    best: "O(n²) — 최선도 최솟값 탐색 반복",
    average: "O(n²)",
    worst: "O(n²) / 공간 O(1)",
  },
  insertionSort: {
    best: "O(n) — 이미 정렬된 입력, 비교만 1회씩",
    average: "O(n²)",
    worst: "O(n²) — 역순 입력 / 공간 O(1)",
  },
  mergeSort: {
    best: "O(n log n)",
    average: "O(n log n)",
    worst: "O(n log n) — 항상 동일 / 공간 O(n) 병합 버퍼",
  },
  quickSort: {
    best: "O(n log n) — 피벗이 항상 중앙값일 때",
    average: "O(n log n)",
    worst: "O(n²) — 피벗이 최솟/최댓값일 때 (정렬된 입력) / 공간 O(log n) 재귀 스택",
  },
  // 탐색
  linearSearch: {
    best: "O(1) — 첫 번째 원소가 목표값",
    average: "O(n)",
    worst: "O(n) — 목표값이 맨 끝이거나 없을 때 / 공간 O(1)",
  },
  binarySearch: {
    best: "O(1) — 중앙값이 목표값",
    average: "O(log n)",
    worst: "O(log n) — 정렬된 배열 필수 / 공간 O(1)",
  },
  // 그래프 탐색
  bfs: {
    best: "O(V+E)",
    average: "O(V+E)",
    worst: "O(V+E) / 공간 O(V) — 큐 + 방문 배열",
  },
  dfs: {
    best: "O(V+E)",
    average: "O(V+E)",
    worst: "O(V+E) / 공간 O(V) — 재귀 스택 + 방문 배열",
  },
  // 트리 순회
  preorder: {
    best: "O(n)",
    average: "O(n)",
    worst: "O(n) / 공간 O(n) — 스택 최대 n개",
  },
  inorder: {
    best: "O(n)",
    average: "O(n)",
    worst: "O(n) / 공간 O(n) — 스택 최대 n개",
  },
  postorder: {
    best: "O(n)",
    average: "O(n)",
    worst: "O(n) / 공간 O(n) — 스택 최대 n개",
  },
};

let stepInterval = 1100;

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "setup") initSetupPage();
  if (page === "input") initInputPage();
  if (page === "compare") initComparePage();
});

function getDisplayTitle(itemOrKey) {
  const key = typeof itemOrKey === "string" ? itemOrKey : itemOrKey?.key;
  const fallback = typeof itemOrKey === "string" ? itemOrKey : itemOrKey?.title;
  return cleanDisplayTitles[key] || fallback || "";
}

function getCardMeta(item) {
  return item.category === "알고리즘"
    ? (cleanAlgorithmCardMeta[item.key] || {})
    : (cleanStructureCardMeta[item.key] || {});
}

function getDetailText(key, fallback = "") {
  return cleanDetailMap[key] || fallback || "설명 준비 중";
}

function getComplexityText(key) {
  return cleanComplexity[key] || null;
}

function initSetupPage() {
  const modeButtons = [...document.querySelectorAll("[data-mode]")];
  const topicButtons = [...document.querySelectorAll("[data-topic]")];
  const filterButtons = [...document.querySelectorAll("[data-filter]")];
  const slotElements = [...document.querySelectorAll(".selection-slot")];
  const grid = document.querySelector("#catalog-grid");
  const title = document.querySelector("#catalog-title");
  const description = document.querySelector("#catalog-description");
  const error = document.querySelector("#setup-error");
  const compareBtn = document.querySelector("#go-compare");
  const clearBtn = document.querySelector("#clear-selection");

  const state = {
    mode: "single",
    topic: "자료구조",
    filter: "전체",
    selectedKeys: [],
  };

  const structureItems = setupCatalogKeys.map((key) => getAlgorithm(key)).filter(Boolean);
  const algorithmItems = algorithmCatalogKeys.map((key) => getAlgorithm(key)).filter(Boolean);

  const maxSelectable = () => (state.mode === "compare" ? 2 : 1);

  const syncSlots = () => {
    slotElements.forEach((slot, index) => {
      const value = slot.querySelector(".selection-slot-value");
      const item = getAlgorithm(state.selectedKeys[index]);
      slot.classList.toggle("is-disabled", index === 1 && state.mode === "single");
      const noun = state.topic === "알고리즘" ? "알고리즘" : "자료구조";
      if (item) {
        value.textContent = getDisplayTitle(item);
      } else if (index === 1 && state.mode === "single") {
        value.textContent = "단일보기에서는 첫 번째 항목만 사용합니다";
      } else if (index === 1) {
        value.textContent = `두 번째 ${noun}을 선택해 주세요`;
      } else {
        value.textContent = `${noun}을 선택해 주세요`;
      }
    });
  };

  const renderCards = () => {
    if (state.topic !== "자료구조") {
      title.textContent = "알고리즘";
      description.textContent = "문제를 해결하는 절차와 방법";
      const algoFilterMap = [
        { key: "전체", label: "전체" },
        { key: "정렬 알고리즘", label: "정렬 알고리즘" },
        { key: "탐색 알고리즘", label: "탐색 알고리즘" },
      ];
      filterButtons.forEach((button, index) => {
        const meta = algoFilterMap[index];
        button.disabled = false;
        button.dataset.filter = meta.key;
        button.textContent = meta.label;
        button.classList.toggle("active", state.filter === meta.key);
      });
      const filteredAlgorithms = algorithmItems.filter((item) => (
        (item.subcategory === "정렬 알고리즘" || item.subcategory === "탐색 알고리즘")
        && (state.filter === "전체" || item.subcategory === state.filter)
      ));
      grid.innerHTML = filteredAlgorithms.map((item) => {
        const meta = getCardMeta(item);
        const isSelected = state.selectedKeys.includes(item.key);
        return `
          <article class="catalog-card ${isSelected ? "selected" : ""}" data-key="${item.key}">
            <div class="catalog-card-media" style="background:${meta?.tone || "#eef2ff"}">
              <div class="card-preview">${buildAlgorithmPreview(item.key)}</div>
            </div>
            <div class="catalog-card-body">
              <div class="catalog-card-head">
                <h3>${escapeHtml(getDisplayTitle(item))}</h3>
                <span class="catalog-badge">${escapeHtml(item.subcategory.replace(" 알고리즘", ""))}</span>
              </div>
              <p class="catalog-card-copy">${escapeHtml(meta?.summary || item.compareText)}</p>
              <div class="tag-row">
                ${(meta?.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
              </div>
              <div class="catalog-card-actions">
                <button type="button" class="catalog-select-btn">${isSelected ? "선택됨" : "선택"}</button>
              </div>
            </div>
          </article>
        `;
      }).join("");
      compareBtn.disabled = false;
      grid.querySelectorAll(".catalog-card").forEach((card) => {
        card.addEventListener("click", () => {
          const { key } = card.dataset;
          if (state.selectedKeys.includes(key)) {
            state.selectedKeys = state.selectedKeys.filter((item) => item !== key);
          } else {
            const next = [...state.selectedKeys, key];
            state.selectedKeys = next.slice(-maxSelectable());
          }
          if (state.mode === "single") state.selectedKeys = state.selectedKeys.slice(0, 1);
          syncSlots();
          renderCards();
        });
      });
      return;
    }

    title.textContent = "자료구조";
    description.textContent = "데이터의 효율적인 저장과 관리를 위한 구조";
    const structureFilterMap = [
      { key: "전체", label: "전체" },
      { key: "선형 자료구조", label: "선형 자료구조" },
      { key: "비선형 자료구조", label: "비선형 자료구조" },
    ];
    filterButtons.forEach((button, index) => {
      const meta = structureFilterMap[index];
      button.disabled = false;
      button.dataset.filter = meta.key;
      button.textContent = meta.label;
      button.classList.toggle("active", meta.key === state.filter);
    });
    compareBtn.disabled = false;

    const filtered = structureItems.filter((item) => {
      if (state.filter === "전체") return true;
      return item.subcategory === state.filter;
    });

    grid.innerHTML = filtered.map((item) => {
      const meta = getCardMeta(item);
      const isSelected = state.selectedKeys.includes(item.key);
      return `
        <article class="catalog-card ${isSelected ? "selected" : ""}" data-key="${item.key}">
          <div class="catalog-card-media" style="background:${meta?.tone || "#eef2ff"}">
            <div class="card-preview">${buildCardPreview(item.key)}</div>
          </div>
          <div class="catalog-card-body">
            <div class="catalog-card-head">
              <div>
                <h3>${escapeHtml(getDisplayTitle(item))}</h3>
              </div>
              <span class="catalog-badge">${escapeHtml(item.subcategory.replace(" 자료구조", ""))}</span>
            </div>
            <p class="catalog-card-copy">${escapeHtml(meta?.summary || item.compareText)}</p>
            <div class="tag-row">
              ${(meta?.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
            </div>
            <div class="catalog-card-actions">
              <button type="button" class="catalog-select-btn">${isSelected ? "선택됨" : "선택"}</button>
            </div>
          </div>
        </article>
      `;
    }).join("");

    grid.querySelectorAll(".catalog-card").forEach((card) => {
      card.addEventListener("click", () => {
        const { key } = card.dataset;
        if (state.selectedKeys.includes(key)) {
          state.selectedKeys = state.selectedKeys.filter((item) => item !== key);
        } else {
          const next = [...state.selectedKeys, key];
          state.selectedKeys = next.slice(-maxSelectable());
        }
        if (state.mode === "single") {
          state.selectedKeys = state.selectedKeys.slice(0, 1);
        }
        syncSlots();
        renderCards();
      });
    });
  };

  modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      modeButtons.forEach((item) => item.classList.toggle("active", item === button));
      if (state.mode === "single") {
        state.selectedKeys = state.selectedKeys.slice(0, 1);
      }
      syncSlots();
      renderCards();
    });
  });

  topicButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.topic = button.dataset.topic;
      topicButtons.forEach((item) => item.classList.toggle("active", item === button));
      state.selectedKeys = [];
      state.filter = "전체";
      syncSlots();
      renderCards();
    });
  });

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.filter = button.dataset.filter;
      renderCards();
    });
  });

  clearBtn.addEventListener("click", () => {
    state.selectedKeys = [];
    error.hidden = true;
    error.textContent = "";
    syncSlots();
    renderCards();
  });

  compareBtn.addEventListener("click", () => {
    const selectedKeys = [...new Set(state.selectedKeys.filter(Boolean))];
    if (state.mode === "single" && selectedKeys.length !== 1) {
      error.hidden = false;
      error.textContent = "단일보기에서는 1개를 선택해 주세요.";
      return;
    }
    if (state.mode === "compare" && selectedKeys.length !== 2) {
      error.hidden = false;
      error.textContent = "비교보기에서는 2개를 선택해 주세요.";
      return;
    }
    if (!selectedKeys.length) {
      error.hidden = false;
      error.textContent = "최소 1개의 항목을 선택해 주세요.";
      return;
    }

    if (state.topic === "알고리즘") {
      const inputs = {};
      selectedKeys.forEach((key) => {
        inputs[key] = getAlgorithm(key)?.example || "";
      });
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ selectedKeys, inputs, createdAt: Date.now(), mode: state.mode, topic: state.topic }));
      window.location.href = "/input";
      return;
    }

    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ selectedKeys, createdAt: Date.now(), mode: state.mode, topic: state.topic }));
    window.location.href = "/compare";
  });

  modeButtons[0]?.classList.add("active");
  topicButtons[0]?.classList.add("active");
  state.selectedKeys = [structureItems[0]?.key].filter(Boolean);
  syncSlots();
  renderCards();
}

function initInputPage() {
  const config = readStoredConfig();
  const formRoot = document.querySelector("#input-forms");
  const fillBtn = document.querySelector("#input-fill-example");
  const goCompareBtn = document.querySelector("#go-compare");
  const error = document.querySelector("#input-page-error");
  const guide = document.querySelector("#input-page-guide");

  if (!config?.selectedKeys?.length) {
    window.setTimeout(() => { window.location.href = "/"; }, 700);
    return;
  }

  const selectedItems = config.selectedKeys.map((key) => getAlgorithm(key)).filter(Boolean);
  guide.textContent = selectedItems.length === 1
    ? `${getDisplayTitle(selectedItems[0])}에 맞는 입력을 설정한 뒤 시각화를 시작합니다.`
    : `${getDisplayTitle(selectedItems[0])}와 ${getDisplayTitle(selectedItems[1])}의 입력을 각각 설정한 뒤 비교를 시작합니다.`;

  // 랜덤 생성 불가 알고리즘 (트리 순회 3종 + BFS + DFS)
  const NO_RANDOM_KEYS = new Set(["preorder", "inorder", "postorder", "bfs", "dfs"]);
  // 탐색 알고리즘 (랜덤 시 1~N 수열 + 랜덤 타겟 생성)
  const SEARCH_RANDOM_KEYS = new Set(["linearSearch", "binarySearch"]);

  formRoot.innerHTML = selectedItems.map((item, index) => {
    const noRandom = NO_RANDOM_KEYS.has(item.key);
    const randomRow = noRandom ? "" : `
      <div class="random-input-row">
        <span class="random-input-label">또는 랜덤 생성</span>
        <input type="number" class="random-count-input" data-key="${item.key}" min="1" max="50" placeholder="개수 (1~50)" value="">
        <button type="button" class="random-gen-btn secondary-btn" data-key="${item.key}">랜덤 생성</button>
      </div>
    `;
    return `
    <article class="input-structure-card">
      <div class="input-structure-head">
        <div>
          <p class="panel-index">입력 ${index + 1}</p>
          <h2>${escapeHtml(getDisplayTitle(item))}</h2>
        </div>
        <span class="catalog-badge">${escapeHtml(item.subcategory.replace(" 자료구조", "").replace(" 알고리즘", ""))}</span>
      </div>
      <p class="catalog-card-copy">${escapeHtml(item.compareText)}</p>
      <div class="hint-box">
        <p class="input-format">${escapeHtml(item.inputLabel)}</p>
        <p class="input-description">${escapeHtml(item.inputDescription)}</p>
      </div>
      <label class="field field-wide">
        <span>직접 입력</span>
        <textarea class="structure-input" data-key="${item.key}" rows="5">${escapeHtml(config.inputs?.[item.key] || item.example)}</textarea>
      </label>
      ${randomRow}
    </article>
  `;
  }).join("");

  fillBtn.addEventListener("click", () => {
    selectedItems.forEach((item) => {
      const field = formRoot.querySelector(`[data-key="${item.key}"]`);
      if (field) field.value = item.example;
    });
    error.hidden = true;
    error.textContent = "";
  });

  // 랜덤 생성 버튼
  formRoot.querySelectorAll(".random-gen-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.key;
      const countInput = formRoot.querySelector(`.random-count-input[data-key="${key}"]`);
      const textarea = formRoot.querySelector(`.structure-input[data-key="${key}"]`);
      const count = parseInt(countInput?.value || "", 10);
      if (!count || count < 1 || count > 50) {
        error.hidden = false;
        error.textContent = "생성 개수는 1~50 사이 정수로 입력해 주세요.";
        return;
      }
      error.hidden = true;
      error.textContent = "";
      if (SEARCH_RANDOM_KEYS.has(key)) {
        // 이진/순차 탐색: 1부터 count까지 1씩 증가하는 수열 + 랜덤 타겟
        const values = Array.from({ length: count }, (_, i) => i + 1);
        const target = values[Math.floor(Math.random() * values.length)];
        if (textarea) textarea.value = `${values.join(", ")} | ${target}`;
      } else {
        // 그 외 (정렬 알고리즘 등): random:N 형식으로 저장 (서버에서 실제 랜덤 생성)
        if (textarea) textarea.value = `random:${count}`;
      }
    });
  });

  goCompareBtn.addEventListener("click", () => {
    const inputs = {};
    let hasError = false;
    selectedItems.forEach((item) => {
      const field = formRoot.querySelector(`[data-key="${item.key}"]`);
      const value = field?.value.trim() || "";
      inputs[item.key] = value;
      if (!value) {
        hasError = true;
      }
    });

    if (hasError) {
      error.hidden = false;
      error.textContent = "선택한 모든 자료구조의 입력값을 채워 주세요.";
      return;
    }

    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ ...config, inputs, createdAt: Date.now(), autoRun: true }));
    window.location.href = "/compare";
  });
}

function buildCardPreview(key) {
  if (key === "array") {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <rect x="28" y="40" width="52" height="36" fill="#ffffff" stroke="#334155" stroke-width="2"/>
        <rect x="80" y="40" width="52" height="36" fill="#ffffff" stroke="#334155" stroke-width="2"/>
        <rect x="132" y="40" width="52" height="36" fill="#ffffff" stroke="#334155" stroke-width="2"/>
        <rect x="184" y="40" width="52" height="36" fill="#f8fafc" stroke="#334155" stroke-width="2"/>
        <text x="54" y="63" text-anchor="middle" font-size="18" font-weight="700" fill="#0f172a">2</text>
        <text x="106" y="63" text-anchor="middle" font-size="18" font-weight="700" fill="#0f172a">5</text>
        <text x="158" y="63" text-anchor="middle" font-size="18" font-weight="700" fill="#0f172a">1</text>
        <text x="54" y="98" text-anchor="middle" font-size="18" font-weight="700" fill="#ef4444">0</text>
        <text x="106" y="98" text-anchor="middle" font-size="18" font-weight="700" fill="#ef4444">1</text>
        <text x="158" y="98" text-anchor="middle" font-size="18" font-weight="700" fill="#ef4444">2</text>
        <text x="210" y="98" text-anchor="middle" font-size="18" font-weight="700" fill="#ef4444">3</text>
      </svg>
    `;
  }
  if (key === "list") {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <rect x="20" y="52" width="54" height="28" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="2"/>
        <rect x="102" y="52" width="54" height="28" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="2"/>
        <rect x="184" y="52" width="54" height="28" rx="8" fill="#ffffff" stroke="#2563eb" stroke-width="2"/>
        <text x="47" y="71" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">7</text>
        <text x="129" y="71" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">3</text>
        <text x="211" y="71" text-anchor="middle" font-size="16" font-weight="700" fill="#0f172a">9</text>
        <path d="M74 66 H96" stroke="#2563eb" stroke-width="3" fill="none"/>
        <path d="M156 66 H178" stroke="#2563eb" stroke-width="3" fill="none"/>
        <polygon points="96,66 88,61 88,71" fill="#2563eb"/>
        <polygon points="178,66 170,61 170,71" fill="#2563eb"/>
      </svg>
    `;
  }
  if (key === "stackOps") {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <rect x="98" y="88" width="64" height="24" rx="8" fill="#ffffff" stroke="#ea580c" stroke-width="2"/>
        <rect x="98" y="60" width="64" height="24" rx="8" fill="#ffffff" stroke="#ea580c" stroke-width="2"/>
        <rect x="98" y="32" width="64" height="24" rx="8" fill="#ffffff" stroke="#ea580c" stroke-width="2"/>
        <text x="130" y="49" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">5</text>
        <text x="130" y="77" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">2</text>
        <text x="130" y="105" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">8</text>
        <text x="182" y="45" font-size="13" font-weight="700" fill="#ea580c">top</text>
      </svg>
    `;
  }
  if (key === "queueOps") {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <rect x="32" y="54" width="46" height="34" rx="10" fill="#ffffff" stroke="#4f46e5" stroke-width="2"/>
        <rect x="86" y="54" width="46" height="34" rx="10" fill="#ffffff" stroke="#4f46e5" stroke-width="2"/>
        <rect x="140" y="54" width="46" height="34" rx="10" fill="#ffffff" stroke="#4f46e5" stroke-width="2"/>
        <text x="55" y="76" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">4</text>
        <text x="109" y="76" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">1</text>
        <text x="163" y="76" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">7</text>
        <path d="M12 71 H28" stroke="#4f46e5" stroke-width="3"/>
        <polygon points="28,71 20,66 20,76" fill="#4f46e5"/>
        <path d="M188 71 H214" stroke="#4f46e5" stroke-width="3"/>
        <polygon points="214,71 206,66 206,76" fill="#4f46e5"/>
        <text x="12" y="52" font-size="13" fill="#4f46e5" font-weight="700">front</text>
        <text x="205" y="52" font-size="13" fill="#4f46e5" font-weight="700">rear</text>
      </svg>
    `;
  }
  if (key === "tree") {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <line x1="130" y1="34" x2="82" y2="70" stroke="#06b6d4" stroke-width="3"/>
        <line x1="130" y1="34" x2="178" y2="70" stroke="#06b6d4" stroke-width="3"/>
        <line x1="82" y1="70" x2="54" y2="108" stroke="#06b6d4" stroke-width="3"/>
        <line x1="82" y1="70" x2="110" y2="108" stroke="#06b6d4" stroke-width="3"/>
        <line x1="178" y1="70" x2="150" y2="108" stroke="#06b6d4" stroke-width="3"/>
        <line x1="178" y1="70" x2="206" y2="108" stroke="#06b6d4" stroke-width="3"/>
        ${["130,34","82,70","178,70","54,108","110,108","150,108","206,108"].map((item) => {
          const [x, y] = item.split(",");
          return `<circle cx="${x}" cy="${y}" r="10" fill="#ffffff" stroke="#06b6d4" stroke-width="3"/>`;
        }).join("")}
      </svg>
    `;
  }
  if (key === "graph") {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <line x1="56" y1="92" x2="98" y2="48" stroke="#8b5cf6" stroke-width="3"/>
        <line x1="98" y1="48" x2="166" y2="48" stroke="#8b5cf6" stroke-width="3"/>
        <line x1="166" y1="48" x2="206" y2="88" stroke="#8b5cf6" stroke-width="3"/>
        <line x1="98" y1="48" x2="132" y2="102" stroke="#8b5cf6" stroke-width="3"/>
        <line x1="132" y1="102" x2="206" y2="88" stroke="#8b5cf6" stroke-width="3"/>
        ${["56,92","98,48","166,48","206,88","132,102"].map((item) => {
          const [x, y] = item.split(",");
          return `<circle cx="${x}" cy="${y}" r="10" fill="#ffffff" stroke="#8b5cf6" stroke-width="3"/>`;
        }).join("")}
      </svg>
    `;
  }
  return "";
}

function buildAlgorithmPreview(key) {
  if (["selectionSort", "insertionSort", "mergeSort", "quickSort", "bubbleSort"].includes(key)) {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        <rect x="30" y="74" width="22" height="42" rx="8" fill="#ffffff" opacity="0.95"/>
        <rect x="64" y="56" width="22" height="60" rx="8" fill="#ffffff" opacity="0.95"/>
        <rect x="98" y="28" width="22" height="88" rx="8" fill="#ffffff" opacity="0.95"/>
        <rect x="132" y="82" width="22" height="34" rx="8" fill="#ffffff" opacity="0.95"/>
        <rect x="166" y="44" width="22" height="72" rx="8" fill="#ffffff" opacity="0.95"/>
      </svg>
    `;
  }
  if (["linearSearch", "binarySearch"].includes(key)) {
    return `
      <svg viewBox="0 0 260 140" aria-hidden="true">
        ${[0,1,2,3,4].map((idx) => `<rect x="${30 + idx * 40}" y="46" width="32" height="32" rx="8" fill="${idx === 2 ? "#fde68a" : "#ffffff"}" stroke="#334155" stroke-width="2"/>`).join("")}
      </svg>
    `;
  }
  if (["graphSearch", "bfs", "dfs"].includes(key)) {
    return buildCardPreview("graph");
  }
  if (["preorder", "inorder", "postorder"].includes(key)) {
    return buildCardPreview("tree");
  }
  return "";
}


function getStructureRenderer(key, fallback) {
  if (key === "array") return "array";
  if (key === "list") return "linked";
  return fallback;
}

function getInitialStructureState(key) {
  if (key === "graph") return { nodes: [], edges: [] };
  if (key === "tree") return { edges: [] };
  return { values: [] };
}

function getRenderState(state) {
  if (state.algorithm.key === "array") {
    return { values: state.structureState.values || [], layout: "array" };
  }
  if (state.algorithm.key === "list") {
    return { values: state.structureState.values || [], layout: "linked" };
  }
  if (state.algorithm.key === "stackOps") {
    return { stack: state.structureState.values || [], action: "idle" };
  }
  if (state.algorithm.key === "queueOps") {
    return { queue: state.structureState.values || [], action: "idle" };
  }
  if (state.algorithm.key === "tree") {
    // 새 포맷: edges 배열 기반
    if (state.structureState.edges !== undefined) {
      const edgeList = state.structureState.edges || [];
      const soloRoot = state.structureState.root;
      if (edgeList.length === 0 && soloRoot) {
        return { nodes: [{ id: soloRoot, label: soloRoot, x: 320, y: 56, highlight: false }], edges: [] };
      }
      return buildTreeEdgePreviewState(edgeList);
    }
    return buildTreePreviewState(state.structureState.values || []);
  }
  if (state.algorithm.key === "graph") {
    return buildGraphPreviewState(state.structureState.nodes || [], state.structureState.edges || []);
  }
  return null;
}

function getStructureActions(key) {
  const mapping = {
    array: ["insert", "delete"],
    list: ["insert", "delete"],
    stackOps: ["push", "pop"],
    queueOps: ["enqueue", "dequeue"],
    tree: ["insert", "delete"],
    graph: ["insert", "delete"],
  };
  return mapping[key] || [];
}

function getStructureInputPlaceholder(key) {
  const placeholders = {
    array: "삽입: index, value / 삭제: index",
    list: "삽입: index, value / 삭제: index",
    stackOps: "값 입력",
    queueOps: "값 입력",
    tree: "삽입: 부모>자식 / 삭제: 노드이름",
    graph: "정점: A / 간선: A-B",
  };
  return placeholders[key] || "값 입력";
}

function getStructureInputGuide(key) {
  const guides = {
    array: "삽입: `index, value` 또는 `value` / 삭제: `index` 또는 비우기",
    list: "삽입: `index, value` 또는 `value` / 삭제: `index` 또는 비우기",
    stackOps: "push는 값 입력, pop은 비워두기",
    queueOps: "enqueue는 값 입력, dequeue는 비워두기",
    tree: "삽입: `부모>자식` (첫 노드는 값만 입력) / 삭제: 노드 이름 입력",
    graph: "정점 추가/삭제: `A` / 간선 추가/삭제: `A-B`",
  };
  return guides[key] || "";
}

function getActionLabel(action) {
  const labels = {
    insert: "삽입",
    delete: "삭제",
    push: "Push",
    pop: "Pop",
    enqueue: "Enqueue",
    dequeue: "Dequeue",
  };
  return labels[action] || action;
}

function buildTreePreviewState(values) {
  const nodes = [];
  const edges = [];
  values.forEach((value, index) => {
    const level = Math.floor(Math.log2(index + 1));
    const pos = index - (2 ** level - 1);
    const x = 640 / (2 ** level + 1) * (pos + 1);
    const y = 60 + level * 84;
    nodes.push({ id: index, label: formatValue(value), x, y, highlight: index === values.length - 1 });
    if (index > 0) {
      edges.push({ from: Math.floor((index - 1) / 2), to: index });
    }
  });
  return { nodes, edges };
}

function buildTreeEdgePreviewState(edgeList) {
  // edgeList: [["A","B"], ...] 형식
  if (!edgeList || edgeList.length === 0) return { nodes: [], edges: [] };

  const childrenMap = {};
  const parentsMap = {};
  const allNodes = new Set();
  for (const [p, c] of edgeList) {
    allNodes.add(p);
    allNodes.add(c);
    if (!childrenMap[p]) childrenMap[p] = [];
    childrenMap[p].push(c);
    parentsMap[c] = p;
  }
  const roots = [...allNodes].filter((n) => !parentsMap[n]);
  const root = roots[0] || edgeList[0][0];

  // BFS로 레벨 계산
  const levels = [];
  const queue = [[root, 0]];
  const visited = new Set();
  while (queue.length) {
    const [node, depth] = queue.shift();
    if (visited.has(node)) continue;
    visited.add(node);
    if (!levels[depth]) levels[depth] = [];
    levels[depth].push(node);
    for (const ch of (childrenMap[node] || [])) queue.push([ch, depth + 1]);
  }

  const nodes = [];
  const nodePos = {};
  levels.forEach((row, depth) => {
    row.forEach((label, idx) => {
      const x = 640 / (row.length + 1) * (idx + 1);
      const y = 56 + depth * 84;
      nodes.push({ id: label, label, x, y, highlight: false });
      nodePos[label] = { x, y };
    });
  });
  const edges = edgeList.map(([p, c]) => ({ from: p, to: c }));
  return { nodes, edges };
}

function buildGraphPreviewState(nodes, edges) {
  const sourceEdges = (edges || []).map((edge) => [edge[0], edge[1]]);
  if (!nodes.length) return { nodes: [], edges: [] };
  const radius = Math.min(210, 120 + nodes.length * 10);
  const centerX = 380;
  const centerY = 190;
  const graphNodes = nodes.map((label, index) => {
    const angle = (Math.PI * 2 * index) / Math.max(nodes.length, 1);
    return {
      id: label,
      label,
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
      current: index === nodes.length - 1,
      visited: false,
      frontier: false,
    };
  });
  return {
    nodes: graphNodes,
    edges: sourceEdges.map(([from, to]) => ({ from, to, label: "", active: false, traversed: false })),
    frontier: [],
    frontierLabel: "nodes",
  };
}

function initComparePage() {
  const config = readStoredConfig();
  const panelGrid = document.querySelector("#panel-grid");
  const panelTemplate = document.querySelector("#panel-template");
  const runAll = document.querySelector("#run-all");
  const pauseAll = document.querySelector("#pause-all");
  const speedSlider = document.querySelector("#speed-slider");
  const speedLabel = document.querySelector("#speed-label");
  const drawerToggle = document.querySelector("#drawer-toggle");
  const drawerPanel = document.querySelector("#drawer-panel");

  if (!config) {
    window.setTimeout(() => { window.location.href = "/"; }, 900);
    return;
  }

  updateSpeedState(speedSlider, speedLabel);
  speedSlider.addEventListener("input", () => updateSpeedState(speedSlider, speedLabel));

  const selectedAlgorithms = config.selectedKeys
    .map((key) => getAlgorithm(key))
    .filter(Boolean)
    .slice(0, 2);

  const panelStates = selectedAlgorithms.map((algorithm, index) => {
    const fragment = panelTemplate.content.cloneNode(true);
    panelGrid.appendChild(fragment);
    const panel = panelGrid.lastElementChild;
    const state = buildComparePanelState(panel, algorithm, index);
    state.rawInput = config.inputs?.[algorithm.key] || "";
    return state;
  });

  const isAlgorithmTopic = config.topic === "알고리즘";
  runAll.hidden = !isAlgorithmTopic;
  pauseAll.hidden = !isAlgorithmTopic;
  pauseAll.addEventListener("click", () => panelStates.forEach((state) => pausePanel(state)));
  runAll.addEventListener("click", () => panelStates.filter((state) => state.isAlgorithmMode).forEach((state) => runPanel(state)));

  setupDrawerModern(panelStates);
  drawerToggle.addEventListener("click", () => {
    const isOpen = drawerToggle.getAttribute("aria-expanded") === "true";
    drawerToggle.setAttribute("aria-expanded", String(!isOpen));
    drawerToggle.textContent = isOpen ? "상세 정보 열기" : "상세 정보 닫기";
    drawerPanel.hidden = isOpen;
  });

  if (isAlgorithmTopic && config.autoRun) {
    panelStates.filter((state) => state.isAlgorithmMode).forEach((state) => runPanel(state));
  }

}

function buildComparePanelState(root, algorithm, index) {
  const isAlgorithmMode = algorithm.category === "알고리즘";
  const state = {
    root,
    algorithm,
    rawInput: "",
    isAlgorithmMode,
    steps: [],
    stepIndex: 0,
    timerId: null,
    renderer: getStructureRenderer(algorithm.key, algorithm.renderer),
    pythonCode: [],
    logs: [],
    structureState: getInitialStructureState(algorithm.key),
    elements: {
      panelIndex: root.querySelector(".panel-index"),
      panelTitle: root.querySelector(".panel-title"),
      badge: root.querySelector(".badge"),
      statusSuccess: root.querySelector(".status.success"),
      statusError: root.querySelector(".status.error"),
      runBtn: root.querySelector(".run-btn"),
      pauseBtn: root.querySelector(".pause-btn"),
      nextBtn: root.querySelector(".next-btn"),
      resetBtn: root.querySelector(".reset-btn"),
      actionInput: root.querySelector(".action-input"),
      structureActions: root.querySelector(".structure-actions"),
      actionHelp: root.querySelector(".action-help"),
      stage: root.querySelector(".canvas-stage"),
      codeBlock: root.querySelector(".code-block"),
    },
  };

  state.elements.panelIndex.textContent = `비교 패널 ${index + 1}`;
  state.elements.panelTitle.textContent = getDisplayTitle(algorithm);
  state.elements.badge.textContent = algorithm.badge;
  state.elements.actionInput.placeholder = getStructureInputPlaceholder(algorithm.key);
  state.elements.actionHelp.textContent = getStructureInputGuide(algorithm.key);
  state.elements.structureActions.innerHTML = getStructureActions(algorithm.key)
    .map((action) => `<button type="button" class="structure-action-btn" data-action="${action}">${getActionLabel(action)}</button>`)
    .join("");
  renderCode(state.elements.codeBlock, [], []);
  renderByRenderer(state.renderer, state.elements.stage, isAlgorithmMode ? null : getRenderState(state));

  state.elements.runBtn.hidden = !isAlgorithmMode;
  state.elements.structureActions.parentElement.hidden = isAlgorithmMode;
  state.elements.actionInput.hidden = isAlgorithmMode;
  state.elements.actionHelp.hidden = isAlgorithmMode || !state.elements.actionHelp.textContent;
  state.elements.runBtn.addEventListener("click", () => runPanel(state));
  state.elements.pauseBtn.addEventListener("click", () => pausePanel(state));
  state.elements.nextBtn.addEventListener("click", () => advanceOneStep(state));
  state.elements.resetBtn.addEventListener("click", () => resetPanel(state));
  state.elements.structureActions.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => runStructureAction(state, button.dataset.action));
  });

  // 실행 시간 토글 버튼 (알고리즘 모드 + 시간 실측 지원 알고리즘에서만)
  const NO_TIMING_KEYS = new Set(["bfs", "dfs", "preorder", "inorder", "postorder"]);
  if (isAlgorithmMode && !NO_TIMING_KEYS.has(algorithm.key)) {
    const timingBtn = document.createElement("button");
    timingBtn.type = "button";
    timingBtn.className = "timing-toggle-btn";
    timingBtn.textContent = "⏱ 실행 시간";
    timingBtn.title = "실행 시간 보기";
    timingBtn.hidden = true;

    const timingBox = document.createElement("div");
    timingBox.className = "timing-box";
    // 내부 래퍼 (grid 애니메이션용)
    const timingBoxInner = document.createElement("div");
    timingBoxInner.className = "timing-box-inner";
    timingBox.appendChild(timingBoxInner);

    timingBtn.addEventListener("click", () => {
      const isOpen = timingBox.classList.toggle("is-open");
      timingBtn.classList.toggle("timing-toggle-btn--active", isOpen);
    });

    // panel-top 오른쪽 끝에 버튼 삽입
    const panelTop = root.querySelector(".panel-top");
    panelTop.appendChild(timingBtn);

    // canvas-card 아래에 timingBox 삽입
    const canvasCard = root.querySelector(".canvas-card");
    canvasCard.after(timingBox);

    state.elements.timingBtn = timingBtn;
    state.elements.timingBox = timingBox;
  }

  return state;
}

async function runPanel(state) {
  if (!state.isAlgorithmMode) return;
  if (state.steps.length && state.stepIndex < state.steps.length - 1) {
    pausePanel(state);
    scheduleNext(state);
    return;
  }
  if (state.steps.length && state.stepIndex === state.steps.length - 1) {
    state.steps = [];
    state.stepIndex = 0;
  }
  pausePanel(state);
  state.abortController?.abort();
  state.abortController = new AbortController();
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ algorithmKey: state.algorithm.key, rawInput: state.rawInput }),
      signal: state.abortController.signal,
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) throw new Error(payload.error || "알고리즘 실행에 실패했습니다.");
    state.steps = payload.steps;
    state.stepIndex = 0;
    state.renderer = payload.renderer || state.algorithm.renderer;
    state.pythonCode = payload.pythonCode || state.algorithm.pythonCode;
    state.logs = payload.steps.map((step, index) => `${index + 1}단계 · ${step.message}`);
    state.executionTimeMs = payload.executionTimeMs ?? null;
    state.inputCount = payload.inputCount ?? null;
    clearError(state);
    renderCode(state.elements.codeBlock, state.pythonCode, []);
    showStep(state);
    scheduleNext(state);
    refreshLogDrawerModern();
    updateTimingToggle(state);
  } catch (error) {
    if (error.name === "AbortError") return;
    showError(state, error.message);
    state.logs = [`오류 · ${error.message}`];
    refreshLogDrawerModern();
  }
}

async function runStructureAction(state, action) {
  if (state.steps.length && state.stepIndex < state.steps.length - 1) {
    pausePanel(state);
    setSuccess(state, "현재 애니메이션이 끝난 뒤 다시 실행해 주세요.");
    return;
  }

  pausePanel(state);
  state.abortController?.abort();
  state.abortController = new AbortController();
  const value = state.elements.actionInput.value.trim();

  try {
    const response = await fetch("/api/structure-action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        algorithmKey: state.algorithm.key,
        action,
        value,
        structureState: state.structureState,
      }),
      signal: state.abortController.signal,
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      throw new Error(payload.error || "자료구조 동작 실행에 실패했습니다.");
    }

    state.steps = payload.steps;
    state.stepIndex = 0;
    state.renderer = payload.renderer || state.algorithm.renderer;
    state.pythonCode = payload.pythonCode || state.algorithm.pythonCode;
    state.structureState = payload.structureState || state.structureState;
    state.logs = payload.steps.map((step, index) => `${index + 1}단계 · ${step.message}`);
    clearError(state);
    renderCode(state.elements.codeBlock, state.pythonCode, []);
    setSuccess(state, "동작 애니메이션을 생성했습니다.");
    showStep(state);
    scheduleNext(state);
    refreshLogDrawerModern();
  } catch (error) {
    if (error.name === "AbortError") return;
    showError(state, error.message);
    state.logs = [`오류 · ${error.message}`];
    refreshLogDrawerModern();
  }
}

function pausePanel(state) {
  if (state.timerId) {
    clearTimeout(state.timerId);
    state.timerId = null;
  }
}

function advanceOneStep(state) {
  pausePanel(state);
  if (!state.steps.length) {
    setSuccess(state, "먼저 동작 버튼을 눌러 애니메이션을 생성해 주세요.");
    return;
  }
  if (state.stepIndex >= state.steps.length - 1) {
    setSuccess(state, "이미 마지막 단계입니다.");
    return;
  }
  state.stepIndex += 1;
  showStep(state);
  if (state.stepIndex < state.steps.length - 1) {
    setSuccess(state, `${state.stepIndex + 1}단계를 확인했습니다. 실행을 누르면 이어서 재생합니다.`);
  }
}

function resetPanel(state) {
  pausePanel(state);
  state.abortController?.abort();
  state.abortController = null;
  state.steps = [];
  state.stepIndex = 0;
  clearError(state);
  state.structureState = getInitialStructureState(state.algorithm.key);
  renderByRenderer(state.renderer, state.elements.stage, getRenderState(state));
  state.pythonCode = [];
  renderCode(state.elements.codeBlock, state.pythonCode, []);
  setSuccess(state, "패널을 초기 상태로 되돌렸습니다.");
  // 실행 시간 박스 접기
  if (state.elements.timingBox) {
    state.elements.timingBox.classList.remove("is-open");
    state.elements.timingBox.removeAttribute("data-ever-shown");
    state.elements.timingBtn?.classList.remove("timing-toggle-btn--active");
    if (state.elements.timingBtn) state.elements.timingBtn.hidden = true;
  }
}

function scheduleNext(state) {
  if (state.stepIndex >= state.steps.length - 1) {
    state.timerId = null;
    setSuccess(state, `${state.steps[state.stepIndex].message} 실행이 완료되었습니다.`);
    return;
  }
  state.timerId = setTimeout(() => {
    state.stepIndex += 1;
    showStep(state);
    scheduleNext(state);
  }, stepInterval);
}

function showStep(state) {
  const step = state.steps[state.stepIndex];
  renderByRenderer(state.renderer, state.elements.stage, step.state);
  renderCode(state.elements.codeBlock, state.pythonCode, step.activeLines || []);
  setSuccess(state, step.message);
}

function renderCode(container, lines, activeLines) {
  const activeSet = new Set(activeLines.filter((n) => n >= 1 && n <= lines.length));
  container.innerHTML = lines
    .map((line, index) => {
      const lineNum = index + 1;
      const className = activeSet.has(lineNum) ? "code-line active" : "code-line";
      return `<span class="${className}">${escapeHtml(`${String(lineNum).padStart(2, " ")}. ${line}`)}</span>`;
    })
    .join("");

  if (activeSet.size === 0) return;

  const firstActive = container.querySelector(".code-line.active");
  const lastActive = container.querySelectorAll(".code-line.active");
  const lastActiveEl = lastActive[lastActive.length - 1];
  if (!firstActive) return;

  const containerTop = container.getBoundingClientRect().top;
  const containerBottom = container.getBoundingClientRect().bottom;
  const firstTop = firstActive.getBoundingClientRect().top;
  const lastBottom = lastActiveEl.getBoundingClientRect().bottom;

  const isVisible = firstTop >= containerTop && lastBottom <= containerBottom;
  if (!isVisible) {
    const offset = firstActive.offsetTop - container.offsetTop;
    const center = offset - (container.clientHeight / 2) + (firstActive.offsetHeight / 2);
    container.scrollTo({ top: Math.max(0, center), behavior: "smooth" });
  }
}

function setSuccess(state, message) {
  state.elements.statusSuccess.textContent = message;
}

function clearError(state) {
  state.elements.statusError.hidden = true;
  state.elements.statusError.textContent = "";
}

function showError(state, message) {
  pausePanel(state);
  state.elements.statusError.hidden = false;
  state.elements.statusError.textContent = message;
  state.elements.stage.innerHTML = '<div class="viz-empty">입력 오류로 실행이 중단되었습니다.</div>';
  renderCode(state.elements.codeBlock, state.pythonCode, []);
  setSuccess(state, "오류가 있는 입력은 실행하지 않고 현재 상태를 유지합니다.");
}


function createDrawerItemModern(title, body) {
  return `<article class="drawer-item"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(body).replace(/\n/g, "<br>")}</p></article>`;
}

function createDrawerGroupModern(title, items, className = "") {
  return `<section class="drawer-group"><h3>${escapeHtml(title)}</h3><div class="${className}">${items.join("")}</div></section>`;
}

function setupDrawerModern(panelStates) {
  document.querySelector("#drawer-points").innerHTML = panelStates
    .map((state) => {
      const items = [
        createDrawerItemModern("개념 설명", getDetailText(state.algorithm.key, state.algorithm.compareText)),
      ];
      if (state.algorithm.category === "자료구조") {
        items.push(createDrawerItemModern("응용", cleanApplications[state.algorithm.key] || "응용 예시 준비 중"));
        items.push(createDrawerItemModern("함수", (cleanFunctions[state.algorithm.key] || ["함수 설명 준비 중"]).join("\n")));
      }
      return createDrawerGroupModern(getDisplayTitle(state.algorithm), items);
    })
    .join("");

  document.querySelector("#drawer-complexity").innerHTML = panelStates
    .map((state) => {
      const info = getComplexityText(state.algorithm.key) || {};
      return createDrawerGroupModern(getDisplayTitle(state.algorithm), [
        createDrawerItemModern("최선", info.best || "정보 준비 중"),
        createDrawerItemModern("평균", info.average || "정보 준비 중"),
        createDrawerItemModern("최악", info.worst || "정보 준비 중"),
      ], "complexity-grid");
    })
    .join("");

  document.querySelectorAll(".drawer-tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".drawer-tab").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".drawer-view").forEach((view) => view.classList.remove("active"));
      button.classList.add("active");
      document.querySelector(`[data-drawer-view="${button.dataset.drawerTab}"]`).classList.add("active");
    });
  });

  window.__panelStatesForLogs__ = panelStates;
  refreshLogDrawerModern();
}

function refreshLogDrawerModern() {
  const logRoot = document.querySelector("#drawer-logs");
  if (!logRoot || !window.__panelStatesForLogs__) return;
  logRoot.classList.add("log-columns");
  logRoot.innerHTML = window.__panelStatesForLogs__
    .map((state) => createDrawerGroupModern(
      getDisplayTitle(state.algorithm),
      state.logs.length
        ? state.logs.map((item) => createDrawerItemModern("실행 로그", item))
        : [createDrawerItemModern("실행 로그", "아직 생성된 로그가 없습니다.")]
    ))
    .join("");
}

function updateSpeedState(slider, label) {
  const value = Number(slider.value);
  stepInterval = 2400 - value;
  label.textContent = value <= 800 ? "느림" : value <= 1400 ? "보통" : "빠름";
}

function readStoredConfig() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function getAlgorithm(key) {
  return algorithms.find((item) => item.key === key);
}

function renderByRenderer(renderer, container, state) {
  if (renderer === "array") return renderArrayModern(container, state);
  if (renderer === "linked") return renderLinkedModern(container, state);
  if (renderer === "sequence") return renderSequence(container, state);
  if (renderer === "search") return renderSearch(container, state);
  if (renderer === "stack") return renderStack(container, state);
  if (renderer === "queue") return renderQueueModern(container, state);
  if (renderer === "tree") return renderTreeModern(container, state);
  if (renderer === "graph") return renderGraphModern(container, state);
  container.innerHTML = '<div class="viz-empty">표시할 데이터가 없습니다.</div>';
}


function renderStack(container, state) {
  if (!state) {
    container.innerHTML = '<div class="viz-empty">명령을 실행하면 top 기준의 쌓임과 제거 흐름이 표시됩니다.</div>';
    return;
  }
  const stack = state.stack || [];
  const nodes = stack.length
    ? [...stack].reverse().map((value, index) => `
      <div class="queue-node ${index === 0 ? "incoming" : ""}">
        <div>${escapeHtml(formatValue(value))}</div>
        <div class="viz-label">${index === 0 ? "top" : ""}</div>
      </div>
    `).join("")
    : '<div class="queue-chip">현재 스택은 비어 있습니다.</div>';
  const incoming = state.incoming !== undefined && state.incoming !== null
    ? `<div class="queue-chip">push: ${escapeHtml(formatValue(state.incoming))}</div>`
    : "";
  const removed = state.removed !== undefined && state.removed !== null
    ? `<div class="queue-chip">pop: ${escapeHtml(formatValue(state.removed))}</div>`
    : "";
  container.innerHTML = `
    <div class="queue-wrapper">
      <div class="queue-meta">
        <div class="queue-chip">action: ${escapeHtml(state.action || "idle")}</div>
        <div class="queue-chip">size: ${stack.length}</div>
        ${incoming}
        ${removed}
      </div>
      <div class="stack-rail">${nodes}</div>
    </div>
  `;
}

function renderSequence(container, state) {
  if (!state) {
    container.innerHTML = '<div class="viz-empty">실행 전에는 예시를 채우거나 직접 데이터를 입력해 주세요.</div>';
    return;
  }
  const values = state.values || [];
  if (!values.length) {
    container.innerHTML = '<div class="viz-empty">표시할 데이터가 없습니다.</div>';
    return;
  }
  const maxValue = Math.max(...values.map((value) => Math.abs(Number(value)) || 1), 1);
  const html = values.map((value, index) => {
    const classes = ["viz-item"];
    if (state.compare?.includes(index) || state.active?.includes(index)) classes.push("compare");
    if (state.swap?.includes(index)) classes.push("swap");
    if (state.sorted?.includes(index)) classes.push("sorted");
    const height = 52 + (Math.abs(Number(value)) / maxValue) * 92;
    return `<div class="viz-cell"><div class="${classes.join(" ")}" style="height:${height}px">${escapeHtml(formatValue(value))}</div><div class="viz-label">[${index}]</div></div>`;
  }).join("");
  container.innerHTML = `<div class="bar-row">${html}</div>`;
}

function renderSearch(container, state) {
  if (!state) {
    container.innerHTML = '<div class="viz-empty">탐색을 실행하면 현재 확인 위치와 탐색 범위를 볼 수 있습니다.</div>';
    return;
  }
  const values = state.values || [];
  if (!values.length) {
    container.innerHTML = '<div class="viz-empty">표시할 데이터가 없습니다.</div>';
    return;
  }
  const cells = values.map((value, index) => {
    const classes = ["viz-item", "search-box"];
    if (typeof state.low === "number" && typeof state.high === "number" && index >= state.low && index <= state.high) {
      classes.push("search-window");
    }
    if (state.current === index) classes.push("compare");
    if (state.mid === index) classes.push("midpoint");
    if (state.found === index) classes.push("found");
    return `<div class="viz-cell"><div class="${classes.join(" ")}">${escapeHtml(formatValue(value))}</div><div class="viz-label">[${index}]</div></div>`;
  }).join("");
  const chips = [
    `<div class="queue-chip">target: ${escapeHtml(formatValue(state.target))}</div>`,
    typeof state.current === "number" ? `<div class="queue-chip">current: [${state.current}]</div>` : "",
    typeof state.mid === "number" ? `<div class="queue-chip">mid: [${state.mid}]</div>` : "",
    typeof state.low === "number" && typeof state.high === "number" ? `<div class="queue-chip">range: [${state.low}] ~ [${state.high}]</div>` : "",
    typeof state.found === "number" ? `<div class="queue-chip">found: [${state.found}]</div>` : "",
  ].filter(Boolean).join("");
  container.innerHTML = `
    <div class="queue-wrapper">
      <div class="queue-meta">${chips}</div>
      <div class="search-row">${cells}</div>
    </div>
  `;
}




function renderArrayModern(container, state) {
  const values = state?.values || [];
  const incoming = state?.incoming;
  if (!values.length && incoming === undefined) {
    container.innerHTML = '<div class="viz-empty">삽입 버튼으로 배열 조작을 시작할 수 있습니다.</div>';
    return;
  }
  const cells = values.map((value, index) => {
    const classes = ["array-box"];
    if (state.compare?.includes(index)) classes.push("active");
    if (typeof state.shiftFrom === "number" && index >= state.shiftFrom) classes.push("shifting");
    return `<div class="array-cell"><div class="${classes.join(" ")}">${escapeHtml(formatValue(value))}</div><div class="viz-label">${index}</div></div>`;
  }).join("");
  const incomingCell = incoming !== undefined && incoming !== null
    ? `<div class="array-cell incoming-slot"><div class="array-box incoming">${escapeHtml(formatValue(incoming))}</div><div class="viz-label">${typeof state.insertIndex === "number" ? `insert @ ${state.insertIndex}` : "new"}</div></div>`
    : "";
  container.innerHTML = `<div class="array-row">${cells}${incomingCell}</div>`;
}

function renderLinkedModern(container, state) {
  const values = state?.values || [];
  const incoming = state?.incoming;
  if (!values.length && incoming === undefined) {
    container.innerHTML = '<div class="viz-empty">삽입 버튼으로 리스트 연결을 시작할 수 있습니다.</div>';
    return;
  }
  const insertIndex = typeof state.insertIndex === "number" ? state.insertIndex : null;
  const parts = [];
  values.forEach((value, index) => {
    if (insertIndex === index && incoming !== undefined && incoming !== null && state.previewInsert) {
      parts.push('<div class="linked-arrow reconnect">↘</div>');
      parts.push(`<div class="linked-node incoming mid-insert"><span>${escapeHtml(formatValue(incoming))}</span></div>`);
      parts.push('<div class="linked-arrow reconnect">↗</div>');
    }
    parts.push(`<div class="linked-node ${state.compare?.includes(index) ? "active" : ""}"><span>${escapeHtml(formatValue(value))}</span></div>`);
    if (index < values.length - 1) parts.push('<div class="linked-arrow">→</div>');
  });
  if (insertIndex === values.length && incoming !== undefined && incoming !== null && state.previewInsert) {
    if (values.length) parts.push('<div class="linked-arrow">→</div>');
    parts.push(`<div class="linked-node incoming"><span>${escapeHtml(formatValue(incoming))}</span></div>`);
  }
  container.innerHTML = `<div class="linked-row">${parts.join("")}</div>`;
}

function renderQueueModern(container, state) {
  if (!state) {
    container.innerHTML = '<div class="viz-empty">명령을 실행하면 큐의 동작을 확인할 수 있습니다.</div>';
    return;
  }
  const queue = state.queue || [];
  const chips = queue.length
    ? queue.map((value, index) => `
      <div class="queue-node ${index === 0 ? "front" : ""}">
        <div>${escapeHtml(formatValue(value))}</div>
        <div class="viz-label">${index === 0 ? "left/front" : index === queue.length - 1 ? "right/rear" : `index ${index}`}</div>
      </div>
      ${index < queue.length - 1 ? '<div class="queue-arrow">→</div>' : ""}
    `).join("")
    : '<div class="queue-chip">현재 큐는 비어 있습니다.</div>';
  const incoming = state.incoming !== undefined && state.incoming !== null
    ? `<div class="queue-node incoming">${escapeHtml(formatValue(state.incoming))}<div class="viz-label">incoming</div></div>`
    : "";
  const removed = state.removed !== undefined && state.removed !== null
    ? `<div class="queue-chip">dequeue: ${escapeHtml(formatValue(state.removed))}</div>`
    : "";
  container.innerHTML = `
    <div class="queue-wrapper">
      <div class="queue-meta">
        <div class="queue-chip">action: ${escapeHtml(state.action || "idle")}</div>
        <div class="queue-chip">size: ${queue.length}</div>
        ${removed}
      </div>
      <div class="queue-rail">
        ${chips}
        ${incoming ? '<div class="queue-arrow">→</div>' : ""}${incoming}
      </div>
    </div>
  `;
}

function renderTreeModern(container, state) {
  if (!state || !(state.nodes || []).length) {
    container.innerHTML = '<div class="viz-empty">트리 구조가 준비되면 여기에 시각화됩니다.</div>';
    return;
  }
  const edges = state.edges || [];
  const nodes = state.nodes || [];
  const nodeMap = new Map(nodes.map((node) => [String(node.id), node]));
  const edgeSvg = edges.map((edge) => {
    const from = nodeMap.get(String(edge.from));
    const to = nodeMap.get(String(edge.to));
    if (!from || !to) return "";
    return `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="#94a3b8" stroke-width="2" />`;
  }).join("");
  const nodeSvg = nodes.map((node) => `
    <g>
      <circle cx="${node.x}" cy="${node.y}" r="22" fill="${node.highlight ? '#dbeafe' : '#ffffff'}" stroke="${node.highlight ? '#2563eb' : '#64748b'}" stroke-width="2"/>
      <text x="${node.x}" y="${node.y + 4}" text-anchor="middle" font-size="12" font-weight="700" fill="#0f172a">${escapeHtml(node.label)}</text>
    </g>
  `).join("");

  // 스택·결과 패널 (순회일 때만 표시) — BFS 스타일 칩 기반
  const stackLabels = state.stack_labels;
  const resultLabels = state.result_labels;
  const hasTraversalInfo = Array.isArray(stackLabels) || Array.isArray(resultLabels);
  const traversalPanel = hasTraversalInfo ? `
    <div class="tree-traversal-panel">
      <div class="tree-traversal-row">
        <span class="tree-traversal-label">스택 (top→)</span>
        <div class="tree-traversal-chips">
          ${(stackLabels || []).length
            ? [...(stackLabels)].reverse().map((v, i) =>
                `<span class="tree-chip tree-chip-stack${i === 0 ? " tree-chip-top" : ""}">${escapeHtml(v)}</span>`
              ).join("")
            : '<span class="tree-chip tree-chip-empty">비어 있음</span>'
          }
        </div>
      </div>
      <div class="tree-traversal-row">
        <span class="tree-traversal-label">방문 순서</span>
        <div class="tree-traversal-chips">
          ${(resultLabels || []).length
            ? (resultLabels).map((v, i) =>
                `<span class="tree-chip tree-chip-result">${escapeHtml(v)}</span>${i < resultLabels.length - 1 ? '<span class="tree-chip-arrow">→</span>' : ""}`
              ).join("")
            : '<span class="tree-chip tree-chip-empty">없음</span>'
          }
        </div>
      </div>
    </div>
  ` : "";

  container.innerHTML = `
    <div class="tree-responsive">
      <svg viewBox="0 0 820 480" preserveAspectRatio="xMidYMid meet" width="100%" height="100%">${edgeSvg}${nodeSvg}</svg>
    </div>
    ${traversalPanel}
  `;
}

function renderGraphModern(container, state) {
  if (!state || !(state.nodes || []).length) {
    container.innerHTML = '<div class="viz-empty">그래프 구조가 준비되면 여기에 시각화됩니다.</div>';
    return;
  }
  const nodes = state.nodes || [];
  const edges = state.edges || [];
  const nodeMap = new Map(nodes.map((node) => [String(node.id), node]));
  const edgeSvg = edges.map((edge) => {
    const from = nodeMap.get(String(edge.from));
    const to = nodeMap.get(String(edge.to));
    if (!from || !to) return "";
    const labelX = (from.x + to.x) / 2;
    const labelY = (from.y + to.y) / 2 - 6;
    const stroke = edge.active ? "#f97316" : edge.traversed ? "#60a5fa" : "#94a3b8";
    const sw = edge.active ? "4" : "2";
    return `
      <line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke="${stroke}" stroke-width="${sw}" />
      ${edge.active ? `<circle cx="${(from.x+to.x)/2}" cy="${(from.y+to.y)/2}" r="5" fill="${stroke}" opacity="0.7"/>` : ""}
      ${edge.label ? `<text x="${labelX}" y="${labelY}" text-anchor="middle" font-size="11" fill="#475569">${escapeHtml(edge.label)}</text>` : ""}
    `;
  }).join("");
  const nodeSvg = nodes.map((node) => `
    <g>
      <circle cx="${node.x}" cy="${node.y}" r="24" fill="${node.current ? '#dbeafe' : node.visited ? '#dcfce7' : node.frontier ? '#fef3c7' : '#ffffff'}" stroke="${node.current ? '#2563eb' : node.visited ? '#16a34a' : node.frontier ? '#f59e0b' : '#64748b'}" stroke-width="${node.current ? '3' : '2'}"/>
      <text x="${node.x}" y="${node.y - 2}" text-anchor="middle" font-size="12" font-weight="700" fill="#0f172a">${escapeHtml(String(node.label).split("\n")[0])}</text>
      ${String(node.label).includes("\n") ? `<text x="${node.x}" y="${node.y + 12}" text-anchor="middle" font-size="11" fill="#475569">${escapeHtml(String(node.label).split("\n")[1])}</text>` : ""}
      ${node.order ? `<text x="${node.x + 23}" y="${node.y - 18}" text-anchor="middle" font-size="10" font-weight="700" fill="#b45309">${escapeHtml(String(node.order))}</text>` : ""}
    </g>
  `).join("");

  // BFS/DFS 순회 전용 패널 (frontier_chips가 있으면 순회 모드)
  const hasFrontierChips = Array.isArray(state.frontier_chips);
  const traversalPanel = hasFrontierChips ? (() => {
    const label = state.frontier_label || state.frontierLabel || "frontier";
    const isDfs = label === "스택";
    const chips = state.frontier_chips || [];
    // DFS 스택은 top이 마지막 원소이므로 reverse해서 표시
    const displayChips = isDfs ? [...chips].reverse() : chips;
    const chipClass = isDfs ? "tree-chip-stack" : "tree-chip-queue";
    const topClass = isDfs ? "tree-chip-top" : "tree-chip-front";
    const frontierHtml = displayChips.length
      ? displayChips.map((v, i) =>
          `<span class="tree-chip ${chipClass}${i === 0 ? ` ${topClass}` : ""}">${escapeHtml(String(v))}</span>`
        ).join(isDfs ? "" : '<span class="tree-chip-arrow">→</span>')
      : '<span class="tree-chip tree-chip-empty">비어 있음</span>';
    const visitedChips = (state.visited_chips || []);
    const visitedHtml = visitedChips.length
      ? visitedChips.map((v) =>
          `<span class="tree-chip tree-chip-result">${escapeHtml(String(v))}</span>`
        ).join('<span class="tree-chip-arrow">→</span>')
      : '<span class="tree-chip tree-chip-empty">없음</span>';
    return `
      <div class="tree-traversal-panel graph-traversal-panel">
        <div class="tree-traversal-row">
          <span class="tree-traversal-label">${escapeHtml(label)} ${isDfs ? "(top→)" : "(front→)"}</span>
          <div class="tree-traversal-chips">${frontierHtml}</div>
        </div>
        <div class="tree-traversal-row">
          <span class="tree-traversal-label">방문 순서</span>
          <div class="tree-traversal-chips">${visitedHtml}</div>
        </div>
      </div>
    `;
  })() : "";

  const currentNode = nodes.find((node) => node.current)?.id || "-";
  container.innerHTML = `
    <div class="queue-wrapper graph-responsive">
      <div class="queue-meta">
        <div class="queue-chip">현재 노드: ${escapeHtml(String(currentNode))}</div>
        ${!hasFrontierChips ? `<div class="queue-chip">${escapeHtml(state.frontierLabel || "frontier")}: ${(state.frontier || []).length ? state.frontier.map((item) => escapeHtml(formatValue(item))).join(" → ") : "비어 있음"}</div>` : ""}
      </div>
      <svg viewBox="0 0 820 480" preserveAspectRatio="xMidYMid meet" width="100%" height="100%">${edgeSvg}${nodeSvg}</svg>
      ${traversalPanel}
    </div>
  `;
}

function formatValue(value) {
  const number = Number(value);
  if (!Number.isNaN(number)) {
    return Number.isInteger(number) ? String(number) : String(Number(number.toFixed(4)));
  }
  return String(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function updateTimingToggle(state) {
  const { timingBtn, timingBox } = state.elements;
  if (!timingBtn || !timingBox) return;

  const ms = state.executionTimeMs;
  const count = state.inputCount;
  if (ms === null || ms === undefined) return;

  const msFormatted = ms < 0.01 ? "< 0.01 ms" : `${ms.toFixed(4)} ms`;
  const countHtml = count !== null ? `<div class="timing-row"><span>입력 개수</span><strong>${count}개</strong></div>` : "";

  const inner = timingBox.querySelector(".timing-box-inner");
  inner.innerHTML = `
    <div class="timing-row"><span>알고리즘</span><strong>${escapeHtml(state.algorithm.title)}</strong></div>
    ${countHtml}
    <div class="timing-row timing-row--highlight"><span>⏱ 실행 시간</span><strong>${msFormatted}</strong></div>
    <p class="timing-note">* 참고용 단일 실행 측정값 — 입력이 작아 실제 복잡도와 다를 수 있습니다</p>
  `;

  timingBtn.hidden = false;

  // 처음 결과가 왔을 때만 자동 펼침 (이후엔 사용자가 직접 토글)
  const isFirstRun = !timingBox.dataset.everShown;
  if (isFirstRun) {
    timingBox.dataset.everShown = "1";
    requestAnimationFrame(() => {
      timingBox.classList.add("is-open");
      timingBtn.classList.add("timing-toggle-btn--active");
    });
  }
}