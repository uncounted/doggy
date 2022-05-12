$(function() {
    $('#uid').focusout(function(){
        $.ajax({
            type: "POST",
            url:"/api/join/dup",
            data: {id_give: $('#uid').val()},
            success: function(response){
                if (response['msg']){
                    $('#dup-chk').removeClass('is-hidden')
                    $('#dup-chk').text(response['msg'])
                } else {
                    $('#dup-chk').addClass('is-hidden')
                }
            }
        })
    })
})

$(function() {
    $('#upw').focusout(function() {
        const regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,16}$/;
        const upwChk = regExp.test($('#upw').val())

        if(!upwChk) {
            $('#wrong-pw').removeClass('is-hidden')
            $('#wrong-pw').text('비밀번호는 영문(대소문자구분),숫자,특수문자(~!@#$%^&*()-_? 만 허용)를 혼용하여 8~16자를 입력해주세요.')
        } else {
            $('#wrong-pw').addClass('is-hidden')
        }
    })
})

$(function() {
    $('#upw2').focusout(function(){
        if($('#upw').val() != $('#upw2').val()) {
            $('#chk-pw').removeClass('is-hidden')
            $('#chk-pw').text('비밀번호가 일치하지 않습니다')
        } else {
            $('#chk-pw').addClass('is-hidden')
        }
    })
})

function join() {
    const uid = $('#uid').val()
    const upw = $('#upw').val()
    const username = $('#username').val()
    const dogname = $('#dogname').val()
    const dogage = $('#dogage').val()
    const doggender = $('input[name="doggender"]:checked').val()
    const dogbirth = $('#dogbirth').val()
    const dupchk = $('#dup-chk').css('display')
    const chkpw = $('#chk-pw').css('display')
    const wrongpw = $('#wrong-pw').css('display')

    if (!uid || !upw || !username  || !dogname || !dogage || !doggender || !dogbirth) {
        alert("모든 항목을 입력해주세요")
    } else if (dupchk !='none' || chkpw != 'none' || wrongpw != 'none'){
        alert("입력 항목을 확인해주세요")
    } else {
            $.ajax({
                type: "POST",
                url: "/api/join",
                data: {
                    id_give: uid,
                    pw_give: upw,
                    name_give: username,
                    dname_give: dogname,
                    dage_give: dogage,
                    dgender_give: doggender,
                    dbirth_give: dogbirth
                },
                success: function (response) {
                    if (response['result'] == 'success') {
                        alert('회원가입이 완료되었습니다.')
                        window.location.href = '/login'
                    } else {
                        alert(response['msg'])
                    }
                }
            })
    }
}

function login() {

    if (!$('#userid').val()|| !$('#userpw').val()) {
        alert ('아이디 또는 비밀번호를 입력하세요')
    } else {
        $.ajax({
            type: "POST",
            url: "/api/login",
            data: {id_give: $('#userid').val(), pw_give: $('#userpw').val()},
            success: function (response) {
                console.log(response)
                if (response['result'] == 'success') {
                    // 로그인이 정상적으로 되면, 토큰을 받아옵니다.
                    // 이 토큰을 mytoken이라는 키 값으로 쿠키에 저장합니다.
                    $.cookie('mytoken', response['token']);
                    alert('로그인 완료!')
                    window.location.href = '/'
                } else {
                    // 로그인이 안되면 에러메시지를 띄웁니다.
                    alert(response['msg'])
                }
            }
        })
    }
}

function logout() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!');
    window.location.href = "/";
}