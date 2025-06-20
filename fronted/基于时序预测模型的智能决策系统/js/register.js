document.addEventListener('DOMContentLoaded', () => {
    //1、验证的是用户名
    const username = document.querySelector('[name=username]')
    username.addEventListener('change', verifyName)
    function verifyName() {
        const span = document.querySelector('.span1')
        const reg = /^[a-zA-Z0-9-_]{6,10}$/
        if (!reg.test(username.value)) {
            span.innerText = '输入不合法，请输入6~10位用户名'
            return false
        }
        span.innerText = ''
        // console.log(username.value)
        return true
    }

    //2、验证的是手机号
    const phone = document.querySelector('[name=phone]')
    phone.addEventListener('change', verifyPhone)
    function verifyPhone() {
        const span = document.querySelector('.span2')
        const reg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
        if (!reg.test(phone.value)) {
            span.innerText = '输入不合法，请输入正确的邮箱'
            return false
        }

        span.innerText = ''
        return true
    }

    //3、验证的是密码
    const password = document.querySelector('[name=password]')
    password.addEventListener('change', verifyPwd)
    function verifyPwd() {
        const span = document.querySelector('.span3')
        const reg = /^[a-zA-Z0-9-_]{6,20}$/
        if (!reg.test(password.value)) {
            span.innerText = '请输入正确的6~20位数字字母组成的密码'
            return false
        }

        span.innerText = ''
        return true
    }

    //4、密码的再次验证
    const confirm = document.querySelector('[name=confirm]')
    confirm.addEventListener('change', verifyConfirm)
    function verifyConfirm() {
        const span = document.querySelector('.span4')
        if (confirm.value !== password.value) {
            span.innerText = '两次密码输入不一致'
            return false
        }

        span.innerText = ''
        return true
    }

    //5、我同意
    const queren = document.querySelector('.icon-queren')
    queren.addEventListener('click', function () {
        this.classList.toggle('icon-queren2')
    })

    // 用户须知
    const needToKnowbtn = document.querySelector('.needToknowbtn')
    const needToKnowDiv = document.querySelector('.needToknow')
    const closeBtn = document.querySelector('.close')

    needToKnowbtn.addEventListener('click', (e) => {
        e.stopPropagation()
        needToKnowDiv.style.display = 'block'
    })

    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation()
        needToKnowDiv.style.display = 'none'
    })

    document.addEventListener('click', (e) => {
        if (needToKnowDiv.style.display === 'block' &&
            !needToKnowDiv.contains(e.target) &&
            e.target !== needToKnowbtn) {
            needToKnowDiv.style.display = 'none'
        }
    })

    needToKnowDiv.addEventListener('click', (e) => {
        e.stopPropagation()
    })



    //6.提交模块
    const registerForm = document.getElementById('register-form')

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault()

        if (!queren.classList.contains('icon-queren2')) {
            alert('请勾选同意协议')
            e.preventDefault()
            return 0
        }
        if (!verifyName() || !verifyPhone() || !verifyPwd() || !verifyConfirm()) {
            e.preventDefault()
            return 0
        }

        const username = document.getElementById('username').value
        const password = document.getElementById('password').value
        const email = document.getElementById('phone').value
        const submitBtn = document.querySelector('.submit')

        const registerData = {
            name: username,
            password: password,
            email: email
        }

        try {
            submitBtn.disabled = true
            submitBtn.textContent = '注册中...'

            const response = await fetch('http://localhost:8080/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registerData)
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const registerdata = await response.json()

            if (registerdata.message === 'success' && registerdata.code === 200) {
                alert('注册成功！')
                window.location.href = 'login.html'
            } else if (registerdata.data.password === '不能为空' && registerdata.code === 400) {
                alert("密码不能为空")
            } else if (registerdata.data.name === '创建时用户名必填' && registerdata.code === 400) {
                alert("创建时用户名必填！")
            } else if (registerdata.message === 'user has exist' && registerdata.code === 400) {
                alert("用户已存在，注册失败")
            } else {
                alert('注册失败，请稍后重试')
            }
        } catch (error) {
            console.error('注册请求失败:', error)
            alert('注册请求失败，请稍后再试')
        } finally {
            submitBtn.disabled = false
            submitBtn.textContent = '注册'
        }
    })
})