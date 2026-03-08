var dept_first = ['内科', '外科', '妇产科', '传染科', '生殖健康',
'男科', '皮肤性病科', '中医科', '五官科', '精神科', '心理科',
'儿科', '营养科', '肿瘤科', '其他科室', '急诊科', '肝病'];
var dept_second = {
    内科: ["呼吸内科", "消化内科", "泌尿内科","心内科", "血液科", "内分泌科",
    "神经内科", "肾内科", "遗传病科", "风湿免疫科"],
    外科: ['感染科', '普外科', '骨外科', '神经外科', '心胸外科', '肝胆外科',
    '泌尿外科', '烧伤科', '肛肠科', '器官移植', '整形美容科'],
    妇产科: ['妇科', '产科'],
    传染科: [],
    生殖健康: ['不孕不育'],
    男科: [],
    皮肤性病科: ['皮肤科', '性病科'],
    中医科: ['中医综合', '针灸科', '中医骨伤科', '中医理疗科', '中医美容'],
    五官科: ['眼科', '口腔科', '耳鼻喉科'],
    精神科: [],
    心理科: [],
    儿科: ['儿科综合', '小儿外科', '小儿内科'],
    营养科: [],
    肿瘤科: ['肿瘤内科', '肿瘤外科'],
    其他科室: ['药品科', '超声科', '重症监护', '辅助检查', '减肥', '康复科',
    '理疗科', '其他综合', '护理', '生活常识', '保健养生', '中西医结合科'],
    急诊科: [],
    肝病: []
};
$(function getdept(){
  for (var i = 0; i < dept_first.length; i++) {
          $option = $("<option/>");
          $option.attr("value", dept_first[i]);
          $option.text(dept_first[i]);
          $(".dept_first").append($option);
  }
});
function removeDiseaseDept(){
     var big_box = document.getElementById("disease");
     big_box.innerHTML = "<div class=\"row my-bar-box\">\
       <p style=\"float:left\" name=\"dept_first-name\"; id=\"dept_first-name\"></p>\
     </div>"
 }
