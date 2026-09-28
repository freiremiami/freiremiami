const STORAGE_KEY = "todo-tasks";

const form = document.getElementById("add-form");
const input = document.getElementById("task-input");
const list = document.getElementById("task-list");
const emptyState = document.getElementById("empty-state");

function loadTasks() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveTasks(tasks) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

let tasks = loadTasks();

function render() {
  list.innerHTML = "";
  emptyState.classList.toggle("hidden", tasks.length > 0);

  tasks.forEach((task, index) => {
    const li = document.createElement("li");
    li.className = "task" + (task.done ? " done" : "");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = `task-${index}`;
    checkbox.checked = task.done;
    checkbox.addEventListener("change", () => {
      tasks[index].done = checkbox.checked;
      saveTasks(tasks);
      render();
    });

    const label = document.createElement("label");
    label.htmlFor = `task-${index}`;
    label.textContent = task.text;

    li.append(checkbox, label);
    list.appendChild(li);
  });
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  tasks.push({ text, done: false });
  saveTasks(tasks);
  input.value = "";
  render();
});

render();
