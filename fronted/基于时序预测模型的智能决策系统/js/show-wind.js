document.addEventListener('DOMContentLoaded', function () {
    // 从sessionStorage获取存储的数据
    const storedData = sessionStorage.getItem('predictionData')
    if (!storedData) {
        console.error('没有找到预测数据')
        return
    }

    const predictionData = JSON.parse(storedData)
    console.log(predictionData)
    const chartData = predictionData.data.data
    const pieChartData = chartData.pieChart
    const lineChartData = chartData.lineChart;

    // 轮毂高度处的风向
    (function () {
        var myChart = echarts.init(document.querySelector('.pie2 .chart'))
        var option = {
            color: ['#0096ff', '#9fe6b8', '#32c5e9', '#ff9f7f', '#9fe6b8', '#32c5e9'],
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b} : {c} ({d}%)'
            },
            legend: {
                bottom: "0%",
                itemHeight: 1,
                itemHeight: 10,
                textStyle: {
                    color: "rgba(255,255,255,.5)",
                    fontSize: "10"
                }
            },
            series: [
                {
                    name: '占比',
                    type: 'pie',
                    radius: ['10%', '70%'],
                    center: ['50%', '40%'],
                    roseType: 'radius',
                    itemStyle: {
                        borderRadius: 5
                    },
                    label: {
                        fontSize: 10
                    },
                    labelLine: {
                        length: 6,
                        length2: 6
                    },
                    // data: [
                    //     { value: 20, name: '(0，60]' },
                    //     { value: 12, name: '(60,120]' },
                    //     { value: 18, name: '(120,180]' },
                    //     { value: 27, name: '(180,240]' },
                    //     { value: 21, name: '(240,300]' },
                    //     { value: 14, name: '(300,360]' },
                    // ]
                    data: pieChartData.data1
                }
            ]
        };

        myChart.setOption(option)
        window.addEventListener("resize", function () {
            myChart.resize();
        });
    })();

    // 地面上1.5米处气温
    (function () {
        var xAxisData = {
            '一天': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'],
            '一周': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            '一月': Array.from({ length: 30 }, (_, i) => (i + 1).toString()),
            '一季度': Array.from({ length: 90 }, (_, i) => (i % 30 + 1).toString())
        };

        // var seriesData = {
        //     '一天': [140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264],
        //     '一周': [120, 282, 111, 234, 220, 340, 310],
        //     '一月': Array.from({ length: 30 }, (_, i) => Math.round(100 + Math.random() * 200)),
        //     '一季度': Array.from({ length: 90 }, (_, i) => Math.round(80 + Math.random() * 250))
        // };

        const seriesData1 = lineChartData.seriesData1

        var myChart = echarts.init(document.querySelector('.line2 .chart'));

        var option = {
            color: ['#00f2f1', '#ed3f35'],
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['一天', '一周', '一月', '一季度'],
                selectedMode: 'single',
                textStyle: {
                    color: '#4c9bfd'
                },
                right: '10%'
            },
            grid: {
                top: '20%',
                left: '3%',
                right: '4%',
                bottom: '3%',
                show: true,
                borderColor: '#012f4a',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: xAxisData['一天'],
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: '#4c9bfd'
                },
                axisLine: {
                    show: false
                }
            },
            yAxis: {
                type: 'value',
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: '#4c9bfd'
                },
                axisLine: {
                    show: false
                },
                splitLine: {
                    lineStyle: {
                        color: '#012f4a'
                    }
                }
            },
            series: [
                {
                    name: '一天',
                    type: 'line',
                    smooth: true,
                    // data: seriesData['一天']
                    data: seriesData1['一天']
                },
                {
                    name: '一周',
                    type: 'line',
                    smooth: true,
                    // data: seriesData['一周']
                    data: seriesData1['一周']
                },
                {
                    name: '一月',
                    type: 'line',
                    smooth: true,
                    // data: seriesData['一月']
                    data: seriesData1['一月']
                },
                {
                    name: '一季度',
                    type: 'line',
                    smooth: true,
                    // data: seriesData['一季度']
                    data: seriesData1['一季度']
                }
            ]
        };

        myChart.setOption(option);

        myChart.on('legendselectchanged', function (params) {
            var selected = params.name;
            myChart.setOption({
                xAxis: {
                    data: xAxisData[selected]
                }
            });
        });

        window.addEventListener("resize", function () {
            myChart.resize();
        });
    })();

    // 地面上1.5米处相对湿度
    (function () {
        var myChart = echarts.init(document.querySelector('.pie1 .chart'))
        var option = {
            color: ['#006cff', '#60cda0', '#ed8884', '#ff9f7f', '#0096ff', '#9fe6b8', '#32c5e9', '#1d9dff'],
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b} : {c} ({d}%)'
            },
            legend: {
                bottom: "0%",
                itemHeight: 1,
                itemHeight: 10,
                textStyle: {
                    color: "rgba(255,255,255,.5)",
                    fontSize: "10"
                }
            },
            series: [
                {
                    name: '占比',
                    type: 'pie',
                    radius: ['10%', '70%'],
                    center: ['50%', '40%'],
                    roseType: 'radius',
                    itemStyle: {
                        borderRadius: 5
                    },
                    label: {
                        fontSize: 10
                    },
                    labelLine: {
                        length: 6,
                        length2: 6
                    },
                    // data: [
                    //     { value: 20, name: '(0，20]' },
                    //     { value: 32, name: '(20,40]' },
                    //     { value: 14, name: '(40,60]' },
                    //     { value: 21, name: '(60,80]' },
                    //     { value: 26, name: '(80,100]' },
                    // ]
                    data: pieChartData.data2
                }
            ]
        };

        myChart.setOption(option)
        window.addEventListener("resize", function () {
            myChart.resize();
        });
    })();

    // 轮毂高度处的风速
    (function () {
        var myChart = echarts.init(document.querySelector('.line3 .chart'));

        var xAxisData = {
            '一天': Array.from({ length: 25 }, (_, i) => i.toString()), // 0-24小时
            '一周': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            '一月': Array.from({ length: 30 }, (_, i) => (i + 1).toString()), // 1-30日
            '一季度': Array.from({ length: 90 }, (_, i) => (i % 30 + 1).toString()) // 1-30日重复3次
        };

        // var seriesData = {
        //     '一天': [140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264],
        //     '一周': [120, 282, 111, 234, 220, 340, 310],
        //     '一月': Array.from({ length: 30 }, (_, i) => Math.round(200 + Math.random() * 200)), // 30个随机数据点
        //     '一季度': Array.from({ length: 90 }, (_, i) => Math.round(150 + Math.random() * 250)) // 90个随机数据点
        // };
        const seriesData2 = lineChartData.seriesData2

        const seriesConfig = [
            {
                name: '一天',
                color: "rgb(255, 6, 6)",
                borderColor: "rgba(221, 220, 107, .1)",
                // data: seriesData['一天']
                data: seriesData2['一天']
            },
            {
                name: "一周",
                color: "#00d887",
                borderColor: "rgba(221, 220, 107, .1)",
                // data: seriesData['一周']
                data: seriesData2['一周']
            },
            {
                name: '一月',
                color: "#0184d5",
                borderColor: "rgb(221, 220, 107)",
                // data: seriesData['一月']
                data: seriesData2['一月']
            },
            {
                name: "一季度",
                color: "rgb(255, 225, 0)",
                borderColor: "rgba(221, 220, 107, .1)",
                // data: seriesData['一季度']
                data: seriesData2['一季度']
            }
        ];

        function createSeries(config) {
            return {
                name: config.name,
                type: 'line',
                smooth: true,
                lineStyle: {
                    color: config.color,
                    width: 2
                },
                symbol: 'circle',
                symbolSize: 8,
                itemStyle: {
                    color: config.color,
                    borderColor: config.borderColor,
                    borderWidth: 12
                },
                showSymbol: false,
                emphasis: {
                    focus: 'series'
                },
                data: config.data
            };
        }

        var option = {
            tooltip: {
                trigger: 'axis',
            },
            legend: {
                selectedMode: 'single',
                top: "0%",
                textStyle: {
                    color: "rgba(255,255,255,.5)",
                    fontSize: "12"
                }
            },
            grid: {
                left: "10",
                top: "30",
                right: "10",
                bottom: "10",
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: xAxisData['一天'],
                axisLabel: {
                    textStyle: {
                        color: "rgba(255,255,255,.6)",
                        fontSize: 12
                    }
                },
                axisLine: {
                    lineStyle: {
                        color: "rgba(255,255,255,.2)"
                    }
                }
            },
            yAxis: {
                type: 'value',
                axisTick: { show: false },
                axisLine: {
                    lineStyle: {
                        color: "rgba(255,255,255,.1)"
                    }
                },
                axisLabel: {
                    textStyle: {
                        color: "rgba(255,255,255,.6)",
                        fontSize: 12
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: "rgba(255,255,255,.1)"
                    }
                }
            },
            series: seriesConfig.map(config => createSeries(config))
        };

        myChart.setOption(option);

        // Handle legend selection change to update x-axis data
        myChart.on('legendselectchanged', function (params) {
            const selectedSeries = Object.keys(params.selected).find(key => params.selected[key]);
            if (selectedSeries && xAxisData[selectedSeries]) {
                myChart.setOption({
                    xAxis: {
                        data: xAxisData[selectedSeries]
                    }
                });
            }
        });

        window.addEventListener("resize", function () {
            myChart.resize();
        });
    })();

    // 原始数据输出功率
    (function () {
        var myChart = echarts.init(document.querySelector('.line4 .chart'));

        var xAxisData = {
            '一天': Array.from({ length: 25 }, (_, i) => i.toString()), // 0-24小时
            '一周': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            '一月': Array.from({ length: 30 }, (_, i) => (i + 1).toString()), // 1-30日
            '一季度': Array.from({ length: 90 }, (_, i) => (i % 30 + 1).toString()) // 1-30日重复3次
        };

        // var seriesData = {
        //     '一天': [140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264],
        //     '一周': [120, 282, 111, 234, 220, 340, 310],
        //     '一月': Array.from({ length: 30 }, (_, i) => Math.round(200 + Math.random() * 200)), // 30个随机数据点
        //     '一季度': Array.from({ length: 90 }, (_, i) => Math.round(150 + Math.random() * 250)) // 90个随机数据点
        // };
        const seriesData3 = lineChartData.seriesData3

        const seriesConfig = [
            {
                name: '一天',
                color: '#F6BD16',
                gradient: [
                    { offset: 0, color: 'rgba(246, 189, 22, 0.6)' },
                    { offset: 1, color: 'rgba(246, 189, 22, 0.1)' }
                ],
                emphasisColor: '#D9A300',
                // data: seriesData['一天']
                data: seriesData3['一天']
            },
            {
                name: '一周',
                color: '#5B8FF9',
                gradient: [
                    { offset: 0, color: 'rgba(91, 143, 249, 0.6)' },
                    { offset: 1, color: 'rgba(91, 143, 249, 0.1)' }
                ],
                emphasisColor: '#3A66C7',
                // data: seriesData['一周']
                data: seriesData3['一周']
            },
            {
                name: '一月',
                color: '#5AD8A6',
                gradient: [
                    { offset: 0, color: 'rgba(90, 216, 166, 0.6)' },
                    { offset: 1, color: 'rgba(90, 216, 166, 0.1)' }
                ],
                emphasisColor: '#36B37E',
                // data: seriesData['一月']
                data: seriesData3['一月']
            },
            {
                name: '一季度',
                color: '#5D7092',
                gradient: [
                    { offset: 0, color: 'rgba(93, 112, 146, 0.6)' },
                    { offset: 1, color: 'rgba(93, 112, 146, 0.1)' }
                ],
                emphasisColor: '#455880',
                // data: seriesData['一季度']
                data: seriesData3['一季度']
            }
        ];

        function createSeries(config) {
            return {
                name: config.name,
                type: 'line',
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: config.color
                },
                itemStyle: {
                    color: config.color
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, config.gradient)
                },
                emphasis: {
                    focus: 'series',
                    itemStyle: {
                        color: config.emphasisColor
                    }
                },
                data: config.data
            };
        }

        option = {
            color: ['#5B8FF9', '#5AD8A6', '#5D7092', '#F6BD16'],
            tooltip: {
                trigger: 'axis',
            },
            legend: {
                data: seriesConfig.map(item => item.name),
                selectedMode: 'single',
                top: "0%",
                textStyle: {
                    color: "rgba(255,255,255,.8)",
                    fontSize: "12"
                }
            },
            grid: {
                top: '20%',
                left: '3%',
                right: '4%',
                bottom: '3%',
                show: true,
                borderColor: '#012f4a',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: xAxisData['一天'],
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: '#4c9bfd'
                },
                axisLine: {
                    show: false
                },
            },
            yAxis: {
                type: 'value',
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: '#4c9bfd'
                },
                axisLine: {
                    show: false
                },
                splitLine: {
                    lineStyle: {
                        color: 'rgba(1, 47, 74, 0.6)',
                        width: 1
                    }
                }
            },
            series: seriesConfig.map(config => createSeries(config))
        };

        myChart.setOption(option);

        myChart.on('legendselectchanged', function (params) {
            const selectedSeries = Object.keys(params.selected).find(key => params.selected[key]);
            if (selectedSeries && xAxisData[selectedSeries]) {
                myChart.setOption({
                    xAxis: {
                        data: xAxisData[selectedSeries]
                    }
                });
            }
        });

        window.addEventListener("resize", function () {
            myChart.resize();
        });
    })();

    // 预测数据输出功率
    (function () {
        var myChart = echarts.init(document.querySelector('.line5 .chart'));


        var xAxisData = {
            '一天': Array.from({ length: 25 }, (_, i) => i.toString()), // 0-24小时
            '一周': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            '一月': Array.from({ length: 30 }, (_, i) => (i + 1).toString()), // 1-30日
            '一季度': Array.from({ length: 90 }, (_, i) => (i % 30 + 1).toString()) // 1-30日重复3次
        };

        // var seriesData = {
        //     '一天': [140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264, 90, 340, 250, 140, 232, 101, 264],
        //     '一周': [120, 282, 111, 234, 220, 340, 310],
        //     '一月': Array.from({ length: 30 }, (_, i) => Math.round(200 + Math.random() * 200)), // 30个随机数据点
        //     '一季度': Array.from({ length: 90 }, (_, i) => Math.round(150 + Math.random() * 250)) // 90个随机数据点
        // };

        const seriesData4 = lineChartData.seriesData4


        const seriesConfig = [
            {
                name: '一天',
                color: '#F6BD16',
                gradient: [
                    { offset: 0, color: 'rgba(246, 189, 22, 0.6)' },
                    { offset: 1, color: 'rgba(246, 189, 22, 0.1)' }
                ],
                emphasisColor: '#D9A300',
                // data: seriesData['一天']
                data: seriesData4['一天']
            },
            {
                name: '一周',
                color: '#5B8FF9',
                gradient: [
                    { offset: 0, color: 'rgba(91, 143, 249, 0.6)' },
                    { offset: 1, color: 'rgba(91, 143, 249, 0.1)' }
                ],
                emphasisColor: '#3A66C7',
                // data: seriesData['一周']
                data: seriesData4['一周']
            },
            {
                name: '一月',
                color: '#5AD8A6',
                gradient: [
                    { offset: 0, color: 'rgba(90, 216, 166, 0.6)' },
                    { offset: 1, color: 'rgba(90, 216, 166, 0.1)' }
                ],
                emphasisColor: '#36B37E',
                // data: seriesData['一月']
                data: seriesData4['一月']
            },
            {
                name: '一季度',
                color: '#5D7092',
                gradient: [
                    { offset: 0, color: 'rgba(93, 112, 146, 0.6)' },
                    { offset: 1, color: 'rgba(93, 112, 146, 0.1)' }
                ],
                emphasisColor: '#455880',
                // data: seriesData['一季度']
                data: seriesData4['一季度']
            }
        ];

        function createSeries(config) {
            return {
                name: config.name,
                type: 'line',
                smooth: true,
                lineStyle: {
                    width: 3,
                    color: config.color
                },
                itemStyle: {
                    color: config.color
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, config.gradient)
                },
                emphasis: {
                    focus: 'series',
                    itemStyle: {
                        color: config.emphasisColor
                    }
                },
                data: config.data
            };
        }

        option = {
            color: ['#5B8FF9', '#5AD8A6', '#5D7092', '#F6BD16'],
            tooltip: {
                trigger: 'axis',
            },
            legend: {
                data: seriesConfig.map(item => item.name),
                selectedMode: 'single',
                top: "0%",
                textStyle: {
                    color: "rgba(255,255,255,.8)",
                    fontSize: "12"
                }
            },
            grid: {
                top: '20%',
                left: '3%',
                right: '4%',
                bottom: '3%',
                show: true,
                borderColor: '#012f4a',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: xAxisData['一天'],
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: '#4c9bfd'
                },
                axisLine: {
                    show: false
                },
            },
            yAxis: {
                type: 'value',
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: '#4c9bfd'
                },
                axisLine: {
                    show: false
                },
                splitLine: {
                    lineStyle: {
                        color: 'rgba(1, 47, 74, 0.6)',
                        width: 1
                    }
                }
            },
            series: seriesConfig.map(config => createSeries(config))
        };

        myChart.setOption(option);

        myChart.on('legendselectchanged', function (params) {
            const selectedSeries = Object.keys(params.selected).find(key => params.selected[key]);
            if (selectedSeries && xAxisData[selectedSeries]) {
                myChart.setOption({
                    xAxis: {
                        data: xAxisData[selectedSeries]
                    }
                });
            }
        });

        window.addEventListener("resize", function () {
            myChart.resize();
        });
    })();

    // 获取数据和DOM元素
    const originalData = chartData.originalData
    const forecastData = chartData.forecastData
    const decisionData = chartData.decisionData
    const starData = chartData.starData

    const modalOverlay = document.getElementById('modalOverlay')
    const closeBtn = document.querySelector('.close')
    const buttons = document.querySelectorAll('.no .btn')
    const backbtn = document.querySelector('.backbtn')

    // 显示特定内容的函数
    function showContent(contentToShow, button) {
        document.querySelectorAll('.modal-content').forEach(content => {
            content.classList.remove('active')
        })

        contentToShow.classList.add('active')

        buttons.forEach(btn => {
            btn.classList.remove('active')
        })

        button.classList.add('active');
        modalOverlay.style.display = 'flex';
    }

    // 数据渲染函数————原始数据
    function renderOriginalData() {
        const table = document.querySelector('#originalContent table')
        while (table.rows.length > 1) {
            table.deleteRow(1)
        }

        originalData.forEach(row => {
            table.innerHTML += `
            <tr>
                <td>${row.key}</td>
                <td>${row.value}</td>
            </tr>
          `
        })

    }

    // 数据渲染函数————预测数据
    function renderForecastData() {
        const periods = ['day', 'week', 'month', 'quarter']
        periods.forEach(period => {
            const table = document.querySelector(`#forecastContent .${period} table`)
            if (!table) return

            while (table.rows.length > 1) {
                table.deleteRow(1)
            }

            forecastData[period].forEach(item => {
                table.innerHTML += `
                <tr>
                    <td>${item.key}</td>
                    <td>${item.value}</td>
                </tr>
                `
            })
        })
    }

    // 数据渲染函数————决策结果
    function renderDecisionData() {
        const decisions = ['first', 'second', 'third']
        decisions.forEach(decision => {
            const decisionDiv = document.querySelector(`#decisionContent .${decision}`)
            if (!decisionDiv || !decisionData[decision]) return

            decisionDiv.innerHTML = ''

            const title = document.createElement('h4')
            const br = document.createElement('br')
            title.textContent = decisionData[decision].title
            decisionDiv.appendChild(title)
            decisionDiv.appendChild(br)

            decisionData[decision].sections.forEach(section => {
                const heading = document.createElement('p');
                const strong = document.createElement('strong');
                strong.textContent = section.heading
                heading.appendChild(strong)
                decisionDiv.appendChild(heading)

                const paragraphs = section.content.split('\n')
                paragraphs.forEach(paragraph => {
                    if (paragraph.trim() === '') return

                    const p = document.createElement('p')
                    p.textContent = paragraph.trim()
                    decisionDiv.appendChild(p)
                })

                const hr1 = document.createElement('hr')
                const hr2 = document.createElement('hr')
                decisionDiv.appendChild(hr1)
                decisionDiv.appendChild(hr2)
            })
        })
    }

    // 内容初始化函数
    function initContent(containerId) {
        const container = document.getElementById(containerId)
        if (!container) return

        container.querySelectorAll('.right-content > div').forEach(el => {
            el.style.display = 'none'
        })

        const firstContent = container.querySelector('.right-content > div:first-child')
        if (firstContent) {
            firstContent.style.display = 'block'
        }

        container.querySelectorAll('.left-li li').forEach(li => {
            li.classList.remove('li-active')
        })

        const firstLi = container.querySelector('.left-li li:first-child')
        if (firstLi) {
            firstLi.classList.add('li-active')
        }
    }


    function renderAllTables() {
        ['first', 'second', 'third'].forEach(tableKey => {
            const tableContainer = document.querySelector(`.${tableKey}-table`);
            if (!tableContainer || !starData[tableKey]) return

            const table = tableContainer.querySelector('table')
            const caption = table.querySelector('caption')
            const tbody = table.querySelector('tbody')
            const title = decisionData[tableKey]?.title.replace(/：/g, '——') || `决策${tableKey === 'first' ? '一' : tableKey === 'second' ? '二' : '三'}`
            caption.textContent = title

            tbody.innerHTML = ''
            // 使用模板字符串批量生成行
            starData[tableKey].forEach(item => {
                tbody.innerHTML += `
            <tr>
                <td>${item.dimension || ''}</td>
                <td><span class="star">${generateStars(item.score || 0)}</span></td>
                <td>${item.basis || ''}</td>
            </tr>
            `
            })
        })
    }

    function generateStars(rating) {
        const validRating = Math.max(1, Math.min(5, parseInt(rating) || 0))
        let stars = ''

        for (let i = 0; i < validRating; i++) {
            stars += '<span class="star-icon filled">★</span>'
        }

        for (let i = validRating; i < 5; i++) {
            stars += '<span class="star-icon empty">☆</span>'
        }

        return stars
    }


    // 侧边栏设置函数
    function setupSidebar(containerId) {
        const container = document.getElementById(containerId)
        if (!container) return

        container.querySelectorAll('.left-li li').forEach(item => {
            item.addEventListener('click', function (e) {
                e.preventDefault()

                container.querySelectorAll('.left-li li').forEach(li => {
                    li.classList.remove('li-active')
                })
                this.classList.add('li-active')

                const targetClass = Array.from(this.classList)
                    .find(cls => cls.endsWith('-btn'))
                    ?.replace('-btn', '')

                if (!targetClass) return

                container.querySelectorAll('.right-content > div').forEach(el => {
                    el.style.display = 'none'
                })

                const targetDiv = container.querySelector(`.right-content .${targetClass}`)
                if (targetDiv) {
                    targetDiv.style.display = 'block'
                }
            })
        })
    }


    function setupTableClicks() {
        const tableMap = {
            'first-table': {
                content: 'first',
                button: 'first-btn',
            },
            'second-table': {
                content: 'second',
                button: 'second-btn'
            },
            'third-table': {
                content: 'third',
                button: 'third-btn'
            }
        };

        Object.entries(tableMap).forEach(([tableClass, config]) => {
            const table = document.querySelector(`.${tableClass}`);
            if (!table) {
                console.warn(`Table with class ${tableClass} not found`);
                return
            }

            table.addEventListener('click', function () {
                // console.log(tableClass)
                // 确保点击的是表格本身或其中的元素
                const parentElement = document.getElementById('decisionContent')
                const contentClass = config.content
                const btn = document.querySelector(`.${config.button}`)
                showContent(parentElement, btn)
                showContentPart(contentClass)
            })
        })
    }

    // 表格对应函数
    function showContentPart(contentClass) {
        const bigDiv = document.getElementById('decisionContent')
        if (!bigDiv) return

        const btnElement = document.querySelector(`.${contentClass}-btn`)
        const lis = bigDiv.querySelectorAll('.left-li li')
        const right = bigDiv.querySelector('.right-content')
        const rightdivs = right.querySelectorAll('.right-content > div')
        const divElement = bigDiv.querySelector(`.${contentClass}`)

        lis.forEach(li => {
            li.classList.remove('li-active')
        })

        rightdivs.forEach(rightdiv => {
            rightdiv.style.display = 'none'
        })

        btnElement.classList.add(('li-active'))
        divElement.style.display = 'block'
    }

    // 初始化所有数据
    renderOriginalData()
    renderForecastData()
    renderDecisionData()
    renderAllTables()

    // 切换按钮的点击事件
    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const target = this.dataset.value
            const content = document.getElementById(`${target}Content`)

            if (content) {
                showContent(content, this)

                if (target === 'forecast' || target === 'decision') {
                    initContent(`${target}Content`)
                }
            }
        })
    })

    // 关闭按钮的点击事件
    closeBtn.addEventListener('click', function () {
        modalOverlay.style.display = 'none'
        buttons.forEach(btn => btn.classList.remove('active'))
    })

    // 模态框背景点击事件
    modalOverlay.addEventListener('click', function (e) {
        if (e.target === modalOverlay) {
            modalOverlay.style.display = 'none'
            buttons.forEach(btn => btn.classList.remove('active'))
        }
    })

    backbtn.addEventListener('click', () => {
        if (window.history.length > 1) {
            window.history.back()
        } else {
            window.location.href = 'index.html'
        }
    })

    // 设置预测和决策内容
    setupSidebar('forecastContent')
    setupSidebar('decisionContent')
    setupTableClicks()
})