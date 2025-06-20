document.addEventListener('DOMContentLoaded', () => {
    //检查登录状态
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')

    // 检查token是否有效
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

    //侧边栏用户名和登录状态部分
    const username = document.querySelector('.user')
    const gologin = document.querySelector('.gologin')
    const logout = document.querySelector('.logout')

    const payload = parseJwt(token)
    function isTokenValid(token) {
        if (!token) return false
        const payload = parseJwt(token)
        return payload && payload.exp * 1000 > Date.now()
    }

    if (payload && payload.exp * 1000 < Date.now()) {
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        window.location.href = 'login.html?expired=true'
        return
    }

    if (token && isTokenValid(token) && storedUsername) {
        username.textContent = storedUsername
        gologin.classList.remove('active')
        logout.classList.add('active')

        loadHistoryRecords()
    } else {
        username.textContent = '用户未登录'
        gologin.classList.add('active')
        logout.classList.remove('active')

        if (token && !isTokenValid(token)) {
            localStorage.removeItem('token')
            localStorage.removeItem('username')
        }

        historyList.innerHTML = ''
    }

    logout.addEventListener('click', () => {
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        location.reload()
    })

    // 侧边栏历史记录部分
    const leftDiv = document.getElementById('history-list')
    const rightDiv = document.getElementById('right-container')
    const toggleButton = document.getElementById('toggle-button')
    const historyList = leftDiv.querySelector('ul')

    let isLeftDivVisible = false

    toggleButton.addEventListener('click', () => {
        if (isLeftDivVisible) {
            leftDiv.style.left = '-300px'
            rightDiv.style.marginLeft = 0
        } else {
            leftDiv.style.left = '0'
            rightDiv.style.marginLeft = '300px'
        }

        isLeftDivVisible = !isLeftDivVisible
    })


    // 加载历史记录函数
    async function loadHistoryRecords() {
        try {
            const response = await fetchWithToken('http://localhost:8081/hist', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })

            if (!response.ok) {
                throw new Error(`获取历史记录失败: ${response.status}`)
            }

            const hisData = await response.json()
            renderHistoryList(hisData.data || [])

        } catch (error) {
            console.error('加载历史记录错误:', error)
            renderHistoryList([], '加载历史记录失败')
        }
    }

    // 渲染历史记录列表
    function renderHistoryList(records, errorMessage) {
        historyList.innerHTML = ''

        if (errorMessage) {
            const li = document.createElement('li')
            li.textContent = errorMessage
            historyList.appendChild(li)
            return
        }

        if (records.length === 0) {
            const li = document.createElement('li')
            li.textContent = '暂无历史记录'
            historyList.appendChild(li)
            return
        }

        records.forEach(record => {
            const li = document.createElement('li')
            li.innerHTML = `
                <a href="javascript:;">
                    <strong>${record.fileName}</strong>
                    <span>类型: ${record.type}</span>
                    <small>${record.time}</small>
                </a>
            `
            li.querySelector('a').addEventListener('click', () => {
                viewHistoryDetail(record)
            })
            historyList.appendChild(li)
        })
    }

    // 查看历史记录详情
    async function viewHistoryDetail(record) {
        try {
            const loadingdiv = document.createElement('div')
            loadingdiv.textContent = '加载历史记录详情中...'
            historyList.innerHTML = ''
            historyList.appendChild(loadingdiv)

            const response = await fetchWithToken('http://localhost:8081/reHist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    time: record.time,
                    type: record.type
                })
            })

            if (!response.ok) {
                throw new Error(`获取历史记录详情失败：${response.status}`)
            }

            const result = await response.json()

            if (result.code !== 200) {
                throw new Error(result.message || '获取历史详情失败')
            }

            const historyDetail = {
                ...record,
                detailData: result.data
            }

            sessionStorage.setItem('historyDetail', JSON.stringify(historyDetail))

            if (record.type === 'wind') {
                window.location.href = 'his-wind.html?from=history'
            } else if (record.type === 'solar') {
                window.location.href = 'his-solar.html?from=history'
            } else {
                window.location.href = 'his-elec.html?from=history'
            }
        } catch (error) {
            console.error('加载历史详情错误:', error)
            renderHistoryList([], `加载失败: ${error.message}`)
        }
    }

    // 封装token的fetch请求
    async function fetchWithToken(url, options = {}) {
        const token = localStorage.getItem('token')

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        }

        if (token) {
            headers['token'] = token
        }

        const mergedOptions = {
            ...options,
            headers
        }

        try {
            const response = await fetch(url, mergedOptions)

            if (response.status === 401) {
                const result = await response.json()
                if (result.code === '400' && result.message === 'fail') {
                    localStorage.removeItem('token')
                    window.location.href = 'login.html?expired=true'
                    return Promise.reject('Token expired')
                }
            }
            return response
        } catch (error) {
            console.error('Request failed:', error)
            throw error
        }
    }


    // 方向预测的按钮操作
    const buttons = document.querySelectorAll('.btn')
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('choiceActive'))
            button.classList.add('choiceActive')
        })
    })


    // 文件处理部分
    const uploadBox = document.getElementById('upload-box')
    const fileInput = document.getElementById('file-input')
    const fileList = document.getElementById('file-list').querySelector('ul')
    const submitButton = document.getElementById('submit')
    let selectedFile = null // 用于存储当前选中的文件

    // 拖拽功能
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault()
        uploadBox.style.borderColor = '#007bff'
    })

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.style.borderColor = '#ccc'
    })

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault()
        uploadBox.style.borderColor = '#ccc'
        const files = e.dataTransfer.files
        handleFiles(files)
    })
    // 点击上传文件
    uploadBox.addEventListener('click', () => {
        fileInput.click()
    })

    fileInput.addEventListener('change', () => {
        const files = fileInput.files
        handleFiles(files)
    })

    // 处理文件的函数
    function handleFiles(files) {
        if (files.length > 1) {
            alert('最多只可以上传一个文件');
            fileInput.value = ''
            return
        }

        if (files.length === 0) return

        const file = files[0]

        // 检查文件扩展名
        const allowedExtensions = ['.txt', '.csv', '.xlsx', '.tsv', '.xls']
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            alert('只允许上传.txt、.csv、.tsv、.xls或者.xlxs文件')
            fileInput.value = ''
            return
        }

        // 检查大小 (这里保持5MB限制，可根据需要调整)
        const maxSize = 30 * 1024 * 1024
        if (file.size > maxSize) {
            alert('文件大小不能超过5MB')
            fileInput.value = ''
            return
        }

        selectedFile = files[0]

        fileList.innerHTML = `
        <li>
            ${file.name} 
            <span>(${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            <button class="remove-btn">×</button>
        </li>
    `
        fileList.querySelector('.remove-btn').addEventListener('click', () => {
            fileInput.value = ''
            fileList.innerHTML = ''
        })
    }

    // 上传文件并预测
    submitButton.addEventListener('click', handleSubmit)
    async function handleSubmit(e) {
        e.preventDefault();

        if (!selectedFile) {
            alert('请上传数据集文件进行预测');
            return;
        }

        const selectedDirection = document.querySelector('.choiceActive');
        if (!selectedDirection) {
            alert('请选择要预测的方向');
            return;
        }

        const preType = selectedDirection.dataset.value;
        const jsonData = {
            type: preType,
            fileName: selectedFile.name
        };

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('data', JSON.stringify(jsonData));

        try {
            submitButton.disabled = true;
            submitButton.textContent = '预测中...';

            const response = await fetchWithToken('http://localhost:8081/prediction', {
                method: 'POST',
                body: formData,
                headers: {}
            })

            if (!response.ok) {
                throw new Error(`预测失败: ${response.status}`)
            }

            const result = await response.json()

            // 存储数据到sessionStorage用于show页面使用
            sessionStorage.setItem('predictionData', JSON.stringify({
                data: result,
                fileName: selectedFile.name,
                predictionType: preType
            }))

            await loadHistoryRecords()

            // 跳转到展示页面
            if (preType === 'wind') {
                window.location.href = 'show-wind.html'
            }
            if (preType === 'solar') {
                window.location.href = 'show-solar.html'
            }
            if (preType === 'elec') {
                window.location.href = 'show-elec.html'
            }
        } catch (error) {
            console.error('预测错误:', error)
            alert(`预测失败: ${error.message}`)
        } finally {
            submitButton.disabled = false
            submitButton.textContent = '生成预测报告'
        }
    }
})