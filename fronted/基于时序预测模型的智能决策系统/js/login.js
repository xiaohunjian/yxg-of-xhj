document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form')
    const usernameInput = document.getElementById('username')
    const passwordInput = document.getElementById('password')
    const checkedBox = document.getElementById('checkbox')
    const spanName = document.querySelector('.span1')
    const spanPsw = document.querySelector('.span2')
    const submitBtn = document.querySelector('.submit')

    // 解析JWT payload
    function parseJwt(token) {
        try {
            const base64Url = token.split('.')[1]
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
            const jsonPayload = decodeURIComponent(
                atob(base64)
                    .split('')
                    .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                    .join('')
            )
            return JSON.parse(jsonPayload)
        } catch (e) {
            return null
        }
    }

    // 检查token是否有效
    function checkTokenValid(token) {
        if (!token) return false
        const payload = parseJwt(token)
        if (payload && payload.exp * 1000 < Date.now()) {
            localStorage.removeItem('token')
            return false
        }
    }

    // 加载页面时检查是否已登录
    const token = localStorage.getItem('token')
    if (token && checkTokenValid(token)) {
        window.location.href = 'index.html'
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault()

        spanName.textContent = ''
        spanPsw.textContent = ''

        const username = usernameInput.value.trim()
        const password = passwordInput.value.trim()

        if (!username) {
            spanName.textContent = '用户名不能为空'
            return
        }

        if (!password) {
            spanPsw.textContent = '密码不能为空'
            return
        }

        const loginData = {
            name: username,
            password: password,
            status: checkedBox.checked ? 1 : 0
        }

        try {
            submitBtn.disabled = true
            submitBtn.textContent = '登录中...'

            const response = await fetch('http://localhost:8080/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(loginData)
            })
            if (!response.ok) {
                throw new Error(`Network response was not ok`)
            }

            const data = await response.json()

            switch (data.code) {
                case 200:
                    // 登录成功，储存token
                    localStorage.setItem('token', data.data)
                    localStorage.setItem('username', username)
                    alert('登录成功！')
                    window.location.href = 'index.html'
                    break
                case 400:
                    if (data.message === 'name or password wrong') {
                        alert('用户名或密码错误！')
                    } else if (data.message === 'fail') {
                        alert('登录已过期，请重新登录')
                    } else {
                        alert(`登录失败: ${data.message || '未知错误'}`)
                    }
                    break
                default:
                    alert(`登录失败: ${data.message || '未知错误'}`);
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            alert('登录请求失败，请检查网络后重试')
        } finally {
            submitBtn.disabled = false
            submitBtn.textContent = '登录'
        }
    })
})