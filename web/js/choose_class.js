const classesList = document.getElementById("classes-list");
const token = localStorage.getItem(access_token);
const classes = fetch("/api/classes")
.then(response => {
  if (!response.ok) {
    document.getElementById("error").textContent = "Ошибка при получении классов";
    throw new Error("Ошибка при получении классов");
  };
  return response.json();
})
.then(data => {
  data.forEach(item => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name + " " + item.class;
    classesList.appendChild(option);
  })
});
const selectBtn = document.getElementById("select-class");

selectBtn.addEventListener("click", function () {
  const class_id = Number(classesList.value);

  fetch("/api/select_class"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({
      class_id: class_id
    })
    .then(response => {
      if (!response.ok) {
        document.getElementById("error").textContent = "Ошибка при получении классов";
    throw new Error("Ошибка при получении классов");
      }
    })
  }
});