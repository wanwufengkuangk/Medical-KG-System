// 疾病详细信息添加网页中
function diseaseInfo(disease_info){
    var disease = document.getElementById('disease'),
      kind = document.getElementById("kind"),
      alias = document.getElementById("alias"),
      brief = document.getElementById("brief"),
      department = document.getElementById("department"),
      check = document.getElementById("check"),
      method = document.getElementById("method"),
      fee = document.getElementById("fee"),
      infect = document.getElementById("infect"),
      cure_period = document.getElementById("cure_period"),
      cure_rate = document.getElementById("cure_rate"),
      proportion = document.getElementById("proportion"),
      population = document.getElementById("population");
    disease.innerHTML = disease_info["disease"];
    if(disease_info["kind"]==""){
      kind.style.display = "none";
    } else{
        kind.innerHTML = disease_info["kind"];
    }
    if(disease_info["alias"]==""){
      alias.parentNode.style.display = "none";
    } else{
        alias.innerHTML = disease_info["alias"];
    }
    if(disease_info["brief"]==""){
      brief.innerHTML = '暂无相关信息';
    } else{
      var data = disease_info["brief"];
      for (i in data){
        var p = document.createElement('p');
        p.innerHTML = "&nbsp; &nbsp; &nbsp; &nbsp;" + data[i];
        brief.appendChild(p);
      }
    }
    if(disease_info["department"]==""){
      department.innerHTML = '暂无相关信息';
    } else{
      department.innerHTML = disease_info["department"];
    }
    if(disease_info["check"]==""){
      check.innerHTML = '暂无相关信息';
    } else{
      check.innerHTML = disease_info["check"];
    }
    if(disease_info["method"]==""){
      method.innerHTML = '暂无相关信息';
    } else{
      method.innerHTML = disease_info["method"];
    }
    if(disease_info["fee"]==""){
      fee.innerHTML = '暂无相关信息';
    } else{
      fee.innerHTML = disease_info["fee"];
    }
    if(disease_info["infect"]==""){
      infect.innerHTML = '暂无相关信息';
    } else{
      infect.innerHTML = disease_info["infect"];
    }
    if(disease_info["cure_period"]==""){
      cure_period.innerHTML = '暂无相关信息';
    } else{
      cure_period.innerHTML = disease_info["cure_period"];
    }
    if(disease_info["cure_rate"]==""){
      cure_rate.innerHTML = '暂无相关信息';
    } else{
      cure_rate.innerHTML = disease_info["cure_rate"];
    }
    if(disease_info["proportion"]==""){
      proportion.innerHTML = '暂无相关信息';
    } else{
        proportion.innerHTML = disease_info["proportion"];
    }
    if(disease_info["population"]==""){
      population.innerHTML = '暂无相关信息';
    } else{
      population.innerHTML = disease_info["population"];
    }
}

// 获取疾病信息列表
function getDisease() {
  $.ajax({
      url: '/info_brief/ajax/',
      type: 'GET',
      data: {'more_type': 'disease', 'search_text':search_text, 'page': disease_page, 'page_size': page_size},
      success: function (data) {
          var data = eval(data);
          // console.log(data.disease_list);
          addDisease(data.disease_list);
          disease_page += 1;
          if(data.disease_list.length < page_size && data.disease_list.length !=0 ){
            var disease = document.getElementById('disease');
            var div = document.createElement('div');
            div.style = "font-size: 20px;color:#999;text-align: center;padding: 10px;0px;10px;0px";
            div.innerHTML = '无更多信息';
            disease.appendChild(div);
            $('#disease-more').hide();
          }
        }
    })
}
// 添加疾病简单信息到网页中
function addDisease(disease_list){
   for(var i in disease_list){
     var big_box = document.getElementById("disease");
     var newA = document.createElement("a");
     var small_box = document.createElement("div");
     var title = document.createElement("div");
     var brief = document.createElement("div");
     var symptom = document.createElement("div");
     newA.href = '/disease/' + disease_list[i]["疾病"];
     newA.style = "text-decoration:none";
     small_box.className = "row my-small-box";
     title.className = "row title";
     title.innerHTML = disease_list[i]["疾病"] + "<span class=\"dept\">" + disease_list[i]["科室"] + "</span>";
     brief.className = "row brief";
     brief.innerHTML = disease_list[i]["简介"];
     symptom.className = "row symptom";
     symptom.innerHTML = "<span class=\"sym\">相关症状:</span>" + disease_list[i]["症状"];
     small_box.appendChild(title);
     small_box.appendChild(brief);
     small_box.appendChild(symptom);
     newA.appendChild(small_box);
     big_box.appendChild(newA);
     // var reforeNode = big_box[big_box.length - 1]
     // big_box.insertBefore(newA, reforeNode.nextSibling);
   }
}
