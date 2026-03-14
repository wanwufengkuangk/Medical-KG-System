// 添加症状详细信息到页面中
function symptomInfo(symptom_info){
  var symptom = document.getElementById("symptom"),
     brief = document.getElementById("brief"),
     cause = document.getElementById("cause"),
     check = document.getElementById("check"),
     diagnose = document.getElementById("diagnose"),
     prevent = document.getElementById("prevent");
  symptom.innerHTML = symptom_info["symptom"];
  if (symptom_info["brief"]==""){
    brief.parentNode.style.display = "none";
  }else {
    var data = symptom_info["brief"];
    for (i in data){
      var p = document.createElement('p');
      p.innerHTML = data[i];
      brief.appendChild(p);
    }
  }
  if (symptom_info["cause"]==""){
    cause.parentNode.style.display = "none";
  }else {
    var data = symptom_info["cause"];
    for (i in data){
      var p = document.createElement('p');
      p.innerHTML = data[i];
      cause.appendChild(p);
    }
  }
  if (symptom_info["check"]==""){
    check.parentNode.style.display = "none";
  }else {
    var data = symptom_info["check"];
    for (i in data){
      var p = document.createElement('p');
      p.innerHTML = data[i];
      check.appendChild(p);
    }
  }
  if (symptom_info["diagnose"]==""){
    diagnose.parentNode.style.display = "none";
  }else {
    var data = symptom_info["diagnose"];
    for (i in data){
      var p = document.createElement('p');
      p.innerHTML = data[i];
      diagnose.appendChild(p);
    }
  }
  if (symptom_info["prevent"]==""){
    prevent.parentNode.style.display = "none";
  }else {
    var data = symptom_info["prevent"];
    for (i in data){
      var p = document.createElement('p');
      p.innerHTML = data[i];
      prevent.appendChild(p);
    }
  }
}

function getSymptom() {
  $.ajax({
      url: '/info_brief/ajax/',
      type: 'GET',
      data: {'more_type': 'symptom', 'search_text':search_text, 'page': symptom_page, 'page_size': page_size},
      success: function (data) {
          var data = eval(data);
          // console.log(data.symptom_list);
          addSymptom(data.symptom_list);
          symptom_page += 1;
          if(data.symptom_list.length < page_size && data.symptom_list.length !=0 ){
            var symptom = document.getElementById('symptom');
            var div = document.createElement('div');
            div.style = "font-size: 20px;color:#999;text-align: center;padding: 10px;0px;10px;0px";
            div.innerHTML = '无更多信息';
            symptom.appendChild(div)
            $('#symptom-more').hide();
          }
        }
    })
};
function addSymptom(symptom_list){
   for(var i in symptom_list){
     var big_box = document.getElementById("symptom");
     var newA = document.createElement("a");
     var small_box = document.createElement("div");
     var title = document.createElement("div");
     var brief = document.createElement("div");
     newA.href = '/symptom/' + symptom_list[i]["症状"];
     newA.style = "text-decoration:none";
     small_box.className = "row my-small-box";
     title.className = "row title";
     title.innerHTML = symptom_list[i]["症状"];
     brief.className = "row brief";
     brief.innerHTML = symptom_list[i]["概述"];
     small_box.appendChild(title);
     small_box.appendChild(brief);
     newA.appendChild(small_box);
     big_box.appendChild(newA);
   }
}
