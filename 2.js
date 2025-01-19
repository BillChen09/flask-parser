document.getElementById('btn').addEventListener('click', () => {
    const text = document.getElementById('inputBox').value; // 获取输入框的值
    if (!text){
        return document.getElementById('result').innerText = "null";
    }
    // 使用 Fetch 发送 POST 请求
    fetch('http://127.0.0.1:5000/', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }) // 将数据序列化为 JSON 格式
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`); // 抛出错误，捕获异常
        }
        return response.json(); // 将响应解析为 JSON
    })
    .then(data => {
        document.getElementById('result').innerText = `结果: ${data.result}`; // 更新页面内容
    })
    .catch(error => {
        console.error('Error:', error); // 输出错误信息
        document.getElementById('result').innerText = '请求失败，请检查后端是否启动'; // 提示用户
    });
});
document.getElementById('btn2').addEventListener('click', () => {
    const text = document.getElementById('inputBox').value;
    fetch('http://127.0.0.1:5000/add', {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text: text})
    })
            .then(response => {
                return response.json();
            })
            .then(data => {
                document.getElementById('result').innerText = data;
            })
})
document.getElementById('btn3').addEventListener('click', () => {
    const code = document.getElementById('inputBox').value;
    fetch('http://127.0.0.1:5000/parse', {
        method: 'POST',
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({code: code})
    })
            .then(response => {
                return response.json();
            })
            .then(data => {
            document.getElementById('result').innerText = JSON.stringify(data, null, 2);
            })
})
