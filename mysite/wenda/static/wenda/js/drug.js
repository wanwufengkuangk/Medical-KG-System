// 添加药物详细信息到网页中
function drugInfo(durg_info){
    var drug = document.getElementById("drug"),
        func = document.getElementById("func"),
        usage = document.getElementById("usage"),
        form = document.getElementById("form"),
        component = document.getElementById("component"),
        effects = document.getElementById("effects"),
        avoid = document.getElementById("avoid"),
        matters = document.getElementById("matters");
     // 通用名称
     drug.innerHTML = drug_info["通用名称"];
     // 功能主治
     if(drug_info["功能主治"]==""){
         var p = document.createElement('p');
         p.innerHTML = '暂无相关信息';
         func.appendChild(p);
     } else{
       data = drug_info["功能主治"];
       for (i in data){
         var p = document.createElement('p');
         p.innerHTML = data[i];
         func.appendChild(p);
       }
     }
     if(drug_info["用法用量"]==""){
         var p = document.createElement('p');
         p.innerHTML = '暂无相关信息';
         usage.appendChild(p);
     } else{
       data = drug_info["用法用量"];
       for (i in data){
         var p = document.createElement('p');
         p.innerHTML = data[i];
         usage.appendChild(p);
       }
     }
     if(drug_info["剂型"]==""){
         form.innerHTML = '暂无相关信息';
     } else{
       form.innerHTML = drug_info["剂型"];
     }
     if(drug_info["成份"]==""){
         var p = document.createElement('p');
         p.innerHTML = '暂无相关信息';
         component.appendChild(p);
     } else{
       data = drug_info["成份"];
       for (i in data){
         var p = document.createElement('p');
         p.innerHTML = data[i];
         component.appendChild(p);
       }
     }
     if(drug_info["不良反应"]==""){
         effects.innerHTML = '暂无相关信息';
     } else{
       data = drug_info["不良反应"];
       for (i in data){
         var p = document.createElement('p');
         p.innerHTML = data[i];
         effects.appendChild(p);
       }
     }
     if(drug_info["禁忌"]==""){
         avoid.innerHTML = '暂无相关信息';
     } else{
       data = drug_info["禁忌"];
       for (i in data){
         var p = document.createElement('p');
         p.innerHTML = data[i];
         avoid.appendChild(p);
       }
     }
     if(drug_info["注意事项"]==""){
         matters.innerHTML = '暂无相关信息';
     } else{
       data = drug_info["注意事项"];
       for (i in data){
         var p = document.createElement('p');
         p.innerHTML = data[i];
         matters.appendChild(p);
       }
     }

}

function getDrug() {
  $.ajax({
      url: '/info_brief/ajax/',
      type: 'GET',
      data: {'more_type': 'drug', 'search_text':search_text, 'page': drug_page, 'page_size': page_size},
      success: function (data) {
          var data = eval(data);
          // console.log(data.drug_list);
          addDrug(data.drug_list);
          drug_page += 1
          if(data.drug_list.length < page_size && data.drug_list.length !=0 ){
            var drug = document.getElementById('drug');
            var div = document.createElement('div');
            div.style = "font-size: 20px;color:#999;text-align: center;padding: 10px;0px;10px;0px";
            div.innerHTML = '无更多信息';
            drug.appendChild(div)
            $('#drug-more').hide();
          }
        }
    })
};
function addDrug(durg_list){
   for(var i in durg_list){
     var big_box = document.getElementById("drug");
     var newA = document.createElement("a");
     var small_box = document.createElement("div");
     var title = document.createElement("div");
     var brief = document.createElement("div");
     newA.href = '/drug/' + durg_list[i]["通用名称"];
     newA.style = "text-decoration:none";
     small_box.className = "row my-small-box";
     title.className = "row title";
     title.innerHTML = durg_list[i]["通用名称"];
     brief.className = "row brief";
     brief.innerHTML = durg_list[i]["功能主治"];
     small_box.appendChild(title);
     small_box.appendChild(brief);
     newA.appendChild(small_box);
     big_box.appendChild(newA);
 }
}
