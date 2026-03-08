var people = document.getElementsByClassName('people')[0].getElementsByTagName('li'),
    disease = document.getElementsByClassName('disease'),
    people_list = ['全部', '男性', '女性', '老年', '儿童'];
(function changeTab(tab) {
    for(var i = 0, len = people.length; i < len; i++) {
        people[i].onmousedown = showLi;
    }
})();

function showLi() {
    for(var i = 0, len = people.length; i < len; i++) {
      if(people[i] === this) {
          people[i].className = 'selected';
          removeDiseasePeople();
          document.getElementById("people-name").innerHTML = people_list[i] + "相关的疾病";
          population_name = people_list[i];
          page = 0;
          getDiseasePeople();
      } else {
          people[i].className = '';
      }
    }
}
function removeDiseasePeople(){
   var big_box = document.getElementById("disease");
   big_box.innerHTML = "<div class=\"row my-bar-box\">\
     <p style=\"float:left7\" name=\"people-name\"; id=\"people-name\"></p>\
   </div>"
}
function getDiseasePeople() {
  $.ajax({
      url: '/population_ajax/',
      type: 'GET',
      data: {'population_name': population_name, 'page': page, 'page_size': page_size},
      success: function (data) {
          var data = eval(data);
          // console.log(data.disease_list);
          addDisease(data.disease_list);
          page += 1;
          if(data.disease_list.length < page_size) return 0;
        }
    })
}
