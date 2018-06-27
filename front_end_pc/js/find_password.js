var vm = new Vue({
    el: '#app',
    data: {
        host: hosts,
        username: "",
        image_code: "",
        image_code_id: "",
        image_code_url: "",
        error_username_message: '',
        error_image_code_message: "",
        error_username: false,
        error_image_code: false,
        access_token: '',
        mobile: '',
        sms_code_tip: '发送验证码',
        error_sms_code: false,
        error_sms_code_message: '短信验证码错误',
        sms_code: "",
        sending_flag: false,
        user_id: "",
        password: '',
        password2: "",
        error_password: false,
        error_password2: false,


        // 控制表单显示
        is_show_form_1: true,
        is_show_form_2: false,
        is_show_form_3: false,
        is_show_form_4: false,


        // 控制进度条显示
        step_class: {
            'step-1': true,
            'step-2': false,
            'step-3': false,
            'step-4': false,
        }
    },
    mounted: function () {
        this.generate_image_code()
    },
    methods: {
        // 创建图形验证码的uuid
        generate_uuid: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        generate_image_code: function () {
            this.image_code_id = this.generate_uuid();
            this.image_code_url = this.host + '/image_code/' + this.image_code_id + "/"
        },
        check_username: function () {
            if (!this.username) {
                this.error_username_message = '账户名不能为空';
                this.error_username = true;
            } else {
                this.error_username = false
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code_message = '图片验证码不能为空';
                this.error_image_code = true;
            } else {
                this.error_image_code = false
            }
        },
        // 找回密码第一步表单提交
        form_1_on_submit: function () {
            this.check_username();
            this.check_image_code();
            if (this.error_image_code == false && this.error_username == false) {
                axios.get(this.host + '/accounts/' + this.username + '/sms/token/?image_code=' +
                    this.image_code + '&image_code_id=' + this.image_code_id, {
                    responseType: 'json'
                })
                    .then(response => {
                        this.mobile = response.data.mobile;
                        this.access_token = response.data.access_token;
                        this.is_show_form_1 = false;
                        this.is_show_form_2 = true;
                        this.step_class['step-1'] = false;
                        this.step_class['step-2'] = true;
                    })
                    .catch(error => {
                        if (error.response.status == 404) {
                            this.error_username_message = '用户名或手机号不存在';
                            this.error_username = true
                        } else if (error.response.status == 400) {
                            this.error_image_code_message = '图片验证码错误';
                            this.error_image_code = true
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        },
        // 找回密码的第二步表单提交
        form_2_on_submit: function () {
            this.check_sms_code();
            if (this.error_sms_code == false) {
                axios.get(this.host + '/accounts/' + this.username + "/password/token/?sms_code=" + this.sms_code, {
                    responseType: 'json'
                })
                    .then(response => {
                        this.user_id = response.data.user_id;
                        this.access_token = response.data.access_token;
                        this.step_class['step-2'] = false;
                        this.step_class['step-3'] = true;
                        this.is_show_form_2 = false;
                        this.is_show_form_3 = true;
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_sms_code_message = error.response.data;
                            this.error_sms_code = true
                        } else {
                            alert(error.response.data);
                            console.log(error.response.data);
                        }
                    })
            }

        },
        // 校验短信验证码
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code = true;
                this.error_sms_code_message = '验证码不能为空'
            } else {
                this.error_sms_code = false
            }
        },
        // 发送短信验证码
        send_sms_code: function () {
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;
            axios.get(this.host + '/sms_codes/?access_token=' + this.access_token, {
                responseType: 'json'
            })
                .then(response => {
                    var num = 60;
                    var t = setInterval(() => {
                        if (num == 1) {
                            clearInterval(t);
                            this.sms_code_tip = '获取短信验证码';
                            this.sending_flag = false
                        } else {
                            num -= 1;
                            this.sms_code_tip = num + '秒';
                        }
                    }, 1000)
                })
                .catch(error => {
                    alert(error.response.data.message);
                    this.sending_flag = false
                })
        },
        check_password: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }

        },
        check_password2: function () {
            if(this.password != this.password2){
                this.error_password2 = true;
            }else {
                this.error_password2 = false
            }
        },
        form_3_on_submit: function () {
            this.check_password();
            this.check_password2();
            if(this.error_password2 == false && this.error_password == false){
                axios.post(this.host + '/users/'+ this.user_id + '/password/',{
                    "password":this.password,
                    "password2":this.password2,
                    "access_token":this.access_token,
                },{
                    responseType:'json'
                })
                    .then(response=>{
                        this.step_class['step-4'] = true;
                        this.step_class['step-3'] = false;
                        this.is_show_form_3 = false;
                        this.is_show_form_4 = true;
                    })
                    .catch(error=>{
                            alert(error.response.data.message);
                            console.log(error.response.data)

                    })
            }
        }
    },
});