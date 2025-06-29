from flask import Flask, request, jsonify

from my_utils import run_according_to_category

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():

    try:
        # 获取请求参数
        data = request.get_json()
        file_path = data.get('address')
        energy_category = data.get('category')

        # 根据类型运行不同模型
        run_according_to_category(energy_category, file_path)

        print(111)

        # 返回结果
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": "",
        }),200

    except Exception as e:
        print(e)
        return jsonify({
            "code": 500,
            "message": f"Unexpected error: {str(e)}",
            "data":"",
        }), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)