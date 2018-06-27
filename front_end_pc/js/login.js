window.onload = function () {
    var vm = new Vue({
        el: "#app",
        data: {
            host: hosts,
            error_username: false,
            error_password: false,
            error_username_message: '请填写用户名或手机号',
            error_password_message: '请填写密码',
            username: '',
            password: '',
            remember: false,
        },
        methods: {
            get_query_string: function (name) {
                var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
                var r = window.location.search.substr(1).match(reg);
                if (r != null) {
                    return decodeURI(r[2]);
                }
                return null;
            },
            check_username: function () {
                if (!this.username) {
                    this.error_username_message = '请填写手机号或用户名';
                    this.error_username = true;
                } else {
                    this.error_username = false;
                }
            },
            check_password: function () {
                if (!this.password) {
                    this.error_password_message = '请填写密码';
                    this.error_password = true
                } else {
                    this.error_password = false
                }
            },
            on_submit: function () {
                this.check_password();
                this.check_username();
                if (this.error_password == false && this.error_username == false) {
                    axios.post(this.host + '/authorizations/', {
                        'username': this.username,
                        'password': this.password,
                    }, {
                        responseType: 'json'
                    })
                        .then(response => {
                            if (this.remember) {
                                sessionStorage.clear();
                                localStorage.token = response.data.token;
                                localStorage.user_id = response.data.user_id;
                                localStorage.username = response.data.username;
                            } else {
                                localStorage.clear();
                                sessionStorage.token = response.data.token;
                                sessionStorage.user_id = response.data.user_id;
                                sessionStorage.username = response.data.username;
                            }
                            var return_url = this.get_query_string('next');
                            if (!return_url) {
                                return_url = '/index.html'
                            }
                            location.href = return_url;
                        })
                        .catch(error => {
                            this.error_password_message = '账号或密码错误';
                            this.error_password = true;
                        })
                }
            }
        }
    });
}