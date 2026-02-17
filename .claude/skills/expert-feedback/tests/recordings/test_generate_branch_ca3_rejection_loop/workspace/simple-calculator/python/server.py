# Flask API Server - Intentionally flawed
# NO validation, NO error handling, NO documentation

from flask import Flask, request, jsonify
from calculator import add, subtract, multiply, divide, modulo, evaluate

app = Flask(__name__)

@app.route('/add', methods=['POST'])
def api_add():
    data = request.json
    result = add(data['a'], data['b'])
    return jsonify({'result': result})

@app.route('/subtract', methods=['POST'])
def api_subtract():
    data = request.json
    result = subtract(data['a'], data['b'])
    return jsonify({'result': result})

@app.route('/multiply', methods=['POST'])
def api_multiply():
    data = request.json
    result = multiply(data['a'], data['b'])
    return jsonify({'result': result})

@app.route('/divide', methods=['POST'])
def api_divide():
    data = request.json
    result = divide(data['a'], data['b'])
    return jsonify({'result': result})

@app.route('/modulo', methods=['POST'])
def api_modulo():
    data = request.json
    result = modulo(data['a'], data['b'])
    return jsonify({'result': result})

@app.route('/evaluate', methods=['POST'])
def api_evaluate():
    data = request.json
    result = evaluate(data['expression'])  # DANGEROUS!
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(port=5000)
