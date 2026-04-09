const classesList = document.getElementById("classes-list");
const classes = fetch("http://localhost:8000/classes")
.then(response => response.json())
.then(data => {
  data.forEach(item => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name + " " + item.class;
    classesList.appendChild(option);
  })
});
const selectBtn = document.getElementById("select-class");

