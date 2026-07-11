;(function () {
    function Ajax(url, actor, data, onSuccess, onComplete) {
        $.ajaxSetup({cache: false});

        $.ajax({
            type: actor,
            url: url,
            timeout: 30000,
            data: data == null ? null : JSON.stringify(data),
            dataType: "json",
            beforeSend: function(request) {
                request.setRequestHeader("X-Requested-With", "XMLHttpRequest");//兼容
            },
            success: onSuccess,
            error: function (jqXHR) {
                console.log("[" + jqXHR.status + "]\n" + jqXHR.responseText);
                if(jqXHR.status == 404){
                    alert("未发现页面");
                }
            },
            complete:onComplete
        })
    }

    function filterEmpty(json) {
        if (!json)
            return json;
        var new_json = {};
        for (var k in json) {
            if (json[k] == undefined || json[k] == null || json[k] == "") {

            } else {
                new_json[k] = json[k];
            }
        }
        return new_json;
    }

    function HttpBuilder(url, actor) {
        this._url = url;
        this._actor = actor;
        this._statusEvent = {};
        this._interceptor = [];
        this._creator = null;
        this._repeat = true;
        this._filterRequestData = null;
        this._beforeRequest = null;
        this._afterResponse = null;
        this.createData = function(creator){
            this._creator = creator;
            return this;
        };
        this.onStatus = function (statusCode, fn) {
            this._statusEvent[statusCode + ""] = fn;
            return this;
        };
        this.intercept = function(interceptor){
            this._interceptor.push(interceptor);
            return this;
        };
        this.setRepeat = function(repeat){
            this._repeat = repeat;
            return this;
        };
        this.filterRequestData = function(filterRequestData){
            this._filterRequestData = filterRequestData;
            return this;
        };
        this.beforeRequest = function(beforeRequest){
            this._beforeRequest = beforeRequest;
            return this;
        };
        this.afterResponse = function(afterResponse){
            this._afterResponse = afterResponse;
            return this;
        };
        this.build = function(){
            return new HttpHandler(this);
        }
    }
    function HttpHandler(httpBuilder){
        var _url = httpBuilder._url;
        this.jQ = null;
        this.requesting = false;
        this.$ = function (selector){
            this.jQ = jQuery(selector);
            return this;
        }
        this.setUrlParam = function(data){
            _url = httpBuilder._url.split("/").map(function(e){
                if(e != "" && e[0] == ":" && data[e.substring(1)]){
                    return data[e.substring(1)];
                }else{
                    return e;
                }
            }).join("/");
            return this;
        }
        this.start = function(onSuccess){
            if(httpBuilder._repeat && this.requesting){
                return;
            }
            var _self = this;
            var data = null;
            if(httpBuilder._creator){
                data = httpBuilder._creator(this.jQ);
            }
            if(httpBuilder._interceptor){
                for(var i in httpBuilder._interceptor){
                    if(!httpBuilder._interceptor[i](data, this.jQ))
                        return;
                }
            }
            this.requesting = true;
            if(httpBuilder._beforeRequest){
                httpBuilder._beforeRequest(data, this.jQ);
            }
            if(httpBuilder._filterRequestData){
                data = httpBuilder._filterRequestData(data, this.jQ);
            }
            if(httpBuilder._actor == "GET" && data){
                this.setUrlParam(data);
            }
            new Ajax(
                _url,
                httpBuilder._actor,
                filterEmpty(data),
                function(data){
                    if(httpBuilder._statusEvent[data.code + ""]){
                        httpBuilder._statusEvent[data.code + ""](data, _self.jQ);
                    }
                    if(data.code == 200 && onSuccess){
                        onSuccess(data, _self.jQ)
                    }
                },
                function(){
                    _self.requesting = false;
                    if(httpBuilder._afterResponse)
                        httpBuilder._afterResponse(_self.jQ);
                }
            );
        }
    }
    var Validate = (function(){
        function isNull(val){
            return typeof val == "undefined" || typeof val == "null" || typeof val == "NaN" || val == "";
        }
        return {
            "required": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && isNull(input_val)){
                    return  input_vd_name + "不能为空";
                }
            },
            "number": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val) && !/^\-?[1-9][0-9]*(\.[0-9]+)?$/.test(input_val)){
                    return input_vd_name + "必须为合法的数字";
                }
            },
            "digits": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val) && !/^[1-9][0-9]*$/.test(input_val)){
                    return input_vd_name + "必须为数字";
                }
            },
            "length": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val) && input_val.toString().length != vd_check_value){
                    return input_vd_name + "长度必须为" + vd_check_value;
                }
            },
            "email": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val) &&
                    /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(input_val.toString())){
                    return input_vd_name + "格式错误";
                }
            },
            "select": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val) && input_val.toString().length != vd_check_value){
                    return  "请选择" + input_vd_name;
                }
            },
            "range": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val)){
                    if(vd_check_value.length == 1 && input_val.toString().length > vd_check_value[0]){
                        return   input_vd_name+"字数超过" +vd_check_value;
                    }else if(vd_check_value.length == 2 &&
                        !(input_val.toString().length >= vd_check_value[0] && input_val.toString().length <= vd_check_value[1])){
                        return   input_vd_name+"字数必须在"+vd_check_value[0]+"和"+vd_check_value[1]+"之间";
                    }
                }
            },
            "match": function(vd_check_value, input_val, input_vd_name){
                if(vd_check_value && !isNull(input_val) && !new RegExp(vd_check_value, 'g').test(input_val)){
                    return  input_vd_name + "格式错误";
                }
            }
        }
    })();
    window.FileObject  = function () {
        var oFile = new Object();
        //初始化fileinput控件（第一次初始化）
        oFile.Init = function(ctrlName, uploadUrl,allowedFile) {
            var obj = $('#' + ctrlName);
            //初始化上传控件的样式
            obj.fileinput({
                    language: 'zh', //设置语言
                    uploadUrl: uploadUrl, //上传的地址
                    allowedFileExtensions: allowedFile,//['jpg', 'gif', 'png','txt'],//接收的文件后缀
                    showUpload: false, //是否显示上传按钮
                    showCaption: true,//是否显示标题
                    showRemove:true,//是否显示删除/清空按钮。默认值true。
                    browseClass: "btn btn-primary", //按钮样式
                    maxFileCount: 1, //表示允许同时上传的最大文件个数
                    enctype: 'multipart/form-data',
                    validateInitialCount:true,
                    previewFileIcon: "<i class='glyphicon glyphicon-king'></i>",
                    msgFilesTooMany: "选择上传的文件数量({n}) 超过允许的最大数值{m}！",
                })
                .on("filebatchselected", function(event, file) {
                    // file[0].size  file[0].type; 文件大小，类型 byte*1024 =kB
                    //上传按钮触发事件 设置后选中图片后直接上传v
                    $('.'+$(this).attr("msgClass")).html("");
                    $(this).fileinput("upload");
                })
                .on("fileuploaded", function(event, data) {
                    //上传之后的，返回函数
                    var file = $(this);
                    var Inputs =   $('.'+ file.attr("msgClass"));
                    if(data.response.code==200){
                        //给出现的删除按钮绑定点击事件
                        $('.fileinput-remove').bind('click',function(){
                            Inputs.html("");
                        })
                        //上传成功 后生产input 记录url
                        // msg-name="videoUrl" msg-vd-name="视频链接" msg-vd-check ="{}"
                        Inputs.html(' <input type="hidden" name="'+file.attr("msg-name")+'" vd-name="'+file.attr("msg-vd-name")+
                            '" vd-check="'+file.attr("msg-vd-check")+'" value="'+data.response.message+'">');
                    }else{
                        Inputs.html("上传失败！");
                    }
                })

        }
        return oFile;
    };
    window.Http = {
        get: function (url) {
            return new HttpBuilder(url, "GET");
        },
        post: function (url) {
            return new HttpBuilder(url, "POST");
        },
        serialize: function($form){
            var data = {};
            $form.serializeArray().forEach(function(kv){
                if(kv.value || kv.value == 0){
                    data[kv.name] = kv.value;
                }
            })
            return data;
        },
        validate: function(data, $form, onError){
            var vds = $form.find("[vd-name]");
            if(vds.length > 0){
                try{
                    for(var i = 0;i < vds.length;i++){
                        var vd = vds.eq(i);
                        var name = vd.attr("name");
                        if(name == undefined){
                            console.warn("缺少name")
                        }
                        var vd_name = vd.attr("vd-name");
                        var vd_check = JSON.parse(vd.attr("vd-check"));
                        var value = data[name];
                        for(var k in vd_check){
                            if(!Validate[k]){
                                console.warn("不支持的属性：" + k);
                            }
                            var error = Validate[k](vd_check[k], value, vd_name);
                            if(error){
                                onError(error, vd);
                                vd.focus();
                                return false;
                            }
                        }
                    }
                }catch (e){
                    console.log("请注意vd-check必须遵循json标准格式")
                    console.error(e);
                    return false;
                }
            }
            return true;
        },
    }
})()