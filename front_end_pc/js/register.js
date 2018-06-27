var vm = new Vue({
	el: '#app',
	data: {
		host: hosts,
		error_name: false,
		error_password: false,
		error_check_password: false,
		error_phone: false,
		error_allow: false,
		error_image_code: false,
		error_sms_code: false,

		username: '',
		password: '',
		password2: '',
		mobile: '', 
		image_code: '',
		sms_code: '',
		image_code_id: '',
		image_code_url: '',
		allow: false,
		error_phone_message: '您输入的手机号格式不正确',
		sending_flag: false,
		sms_code_tip: '获取短信验证码',
		error_image_code_message: '请填写图片验证码',
		error_username_message: '请输入5-20个字符的用户',
        error_sms_code_message: '请填写短信验证码',
	},
	// 这里是钩子函数，直接在页面加载完成以后就不执行了
	mounted:function(){
		//生产uuid
		this.image_code_id = this.generate_uuid();
		//更新验证码图片url
		this.image_code_url = this.host + '/image_code/'+ this.image_code_id +"/"
	},
	methods: {
		// 生成uuid
		generate_uuid: function(){
			var d = new Date().getTime();
			if(window.performance && typeof window.performance.now === "function"){
				d += performance.now(); //use high-precision timer if available
			}
			var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
				var r = (d + Math.random()*16)%16 | 0;
				d = Math.floor(d/16);
				return (c =='x' ? r : (r&0x3|0x8)).toString(16);
			});
			return uuid;
		},
		generate_image_code:function(){
			//生产uuid
		this.image_code_id = this.generate_uuid();
		//更新验证码图片url
		this.image_code_url = this.host + '/image_code/'+ this.image_code_id +"/"
		},
		check_username: function (){
			var len = this.username.length;
			if(len<5||len>20) {
				this.error_name = true;
			} else {
				this.error_name = false;
			}
			if (this.error_name == false){
				axios.get(this.host + '/username/'+ this.username + '/count/',{
					responseType: 'json'
				})
					.then(response=>{
						if (response.data.count > 0){
							this.error_username_message = '用户名已存在';
							this.error_name = true
						}else {
							this.error_name = false
						}
					})
					.catch(error=>{
						console.log(error.response.data)
					})

			}

		},
		check_pwd: function (){
			var len = this.password.length;
			if(len<8||len>20){
				this.error_password = true;
			} else {
				this.error_password = false;
			}		
		},
		check_cpwd: function (){
			if(this.password!=this.password2) {
				this.error_check_password = true;
			} else {
				this.error_check_password = false;
			}		
		},
		check_phone: function (){
			var re = /^1[345789]\d{9}$/;
			if(re.test(this.mobile)) {
				this.error_phone = false;
			} else {
				this.error_phone = true;
			}
			if (this.error_phone == false){
				axios.get(this.host + '/mobiles/'+ this.mobile + '/count/',{
					responseType: 'json'
				})
					.then(response=>{
						if (response.data.count > 0){
							this.error_phone_message = '手机号已存在';
							this.error_phone = true
						}else{
							this.error_phone = false
						}
					})
					.catch(error=>{
						console.log(error.response.data)
					})
			}
		},
		check_image_code: function (){
			if(!this.image_code) {
				this.error_image_code = true;
			} else {
				this.error_image_code = false;
			}	
		},
		check_sms_code: function(){
			if(!this.sms_code){
				this.error_sms_code = true;
			} else {
				this.error_sms_code = false;
			}
		},
		check_allow: function(){
			if(!this.allow) {
				this.error_allow = true;
			} else {
				this.error_allow = false;
			}
		},
		// 注册
		on_submit: function(){
			this.check_username();
			this.check_pwd();
			this.check_cpwd();
			this.check_phone();
			this.check_sms_code();
			this.check_allow();
			if(this.error_name == false && this.error_password == false && this.error_check_password == false
            && this.error_image_code == false && this.error_phone == false && this.error_allow == false
            && this.error_sms_code == false){
			    axios.post(this.host + '/users_register/',{
			        'username': this.username,
                    'password': this.password,
                    'password2': this.password2,
                    'mobile': this.mobile,
                    'image_code': this.image_code,
                    'image_code_id': this.image_code_id,
                    'allow': this.allow.toString(),
                    'sms_code': this.sms_code
                },{
			        responseType: 'json'
                })
                    .then(response=>{
                    	console.log(response.data);
                        localStorage.clear();
                        sessionStorage.clear();
                        sessionStorage.username = response.data.username;
                        sessionStorage.user_id = response.data.id;
                        sessionStorage.token = response.data.token;
                        location.href = '/index.html';
                    })
                    .catch(error=>{
                        if(error.response.status == 400){
                            this.error_sms_code_message = '短信验证码错误';
                            this.error_sms_code = true;
                        }else {
                            console.log(error.response.data);
                        }
                    })
            }
		},
		// 发送手机短信验证码
		send_sms_code: function () {
			// 声明一个点击发送短信的状态，
			if(this.sending_flag == true){
				return;
			}
			this.sending_flag = true;
			// 校验参数是否有数据
			this.check_phone();
			this.check_image_code();
			if(this.error_phone == true || this.error_image_code == true){
				this.sending_flag = false;
				return
			}
			axios.get(this.host + '/sms_code/'+
				this.mobile +'/?image_code='+ this.image_code +'&image_code_id='+ this.image_code_id,{
				responseType: 'json'
			})
				.then((response)=>{
					//表示后端发送短信成功
					//倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
					var num = 60;
					var t = setInterval(()=>{if(num == 1){
						// 计时器到最后，关闭计时器
						clearInterval(t);
						// 将点击获取验证码的按钮展示的文本回复成原始文本
						this.sms_code_tip = '获取短信验证码';
						// 将点击按钮的onclick事件函数恢复回去
						this.sending_flag = false;
					}else{
						num -= 1;
						// 展示倒计时信息
						this.sms_code_tip = num + '秒';
					}
					}, 1000, 60)
				})
				.catch(error=>{
					if (error.response.status == 400){
						this.error_image_code_message = '图片验证码有误';
						this.error_image_code = true;
					}else{
						console.log(error.response.data);
					}
					this.sending_flag = false;
				})
        }
	}
});
