;(function(global, factory){
    var fns = factory()
    for(var fn in fns){
        global[fn] = fns[fn];
    }
})(Http, function(){
    if(!Http){
        console.error("请导入http.js")
    }
    return {
        Login: Http.post("/study/session")
            .setRepeat(false)
            .createData(function($form){
                return Http.serialize($form);
            })
            .intercept(function(data, $form){
                var tipElement = $form.find(".tip").removeClass("blue").addClass("red");
                return Http.validate(data, $form, function(msg){tipElement.text(msg)})
            })
            // .intercept(function (data, $form) {
            //     if (yesOk()) {
            //         return yesOk();
            //     } else {
            //         $('#modalBtn').click();
            //         return yesOk();
            //     }
            // })
            .filterRequestData(function(data){
                data.password  = md5(data.password+ "gw-gd-exam").toUpperCase();
                return data;
            })
            .beforeRequest(function(data, $form){
                $form.find(".tip").html("");
                $form.addClass("inactive");
                $form.find("input").prop("readonly", true);
                $form.find(".button").addClass("button-inactive").html("登录中");
            })
            .afterResponse(function($form){
                $form.removeClass("inactive");
                $form.find("input").prop("readonly", false);
                $form.find(".button").removeClass("button-inactive").html("登 录");
            })
            .onStatus(200, function(msg, $form){
                $form.find(".tip").removeClass("red").addClass("blue").html("正在登录...");
                window.location.href = "/study/index";
            })
            .onStatus(400, function(msg, $form){
                $form.find(".tip").removeClass("blue").addClass("red").text(msg.message);
                $form.find(".captcha").click();
                $form.find(".button").removeClass("button-inactive").html("登 录");
            })
            .build()

    }
})
