from flask import Flask, request, jsonify
import json
import os
import uuid

app = Flask(__name__)

def calculate_price(data):
    """Calculates the price based on the input data."""
    try:
        pallet_price = 100 if data["pallet_spec"] == "符合出入口規格托盤" else 70 if data["pallet_spec"] == "IPPC棧板" else 0

        service_costs_per_pallet = {
            "wrap_plastic": 50 if data["wrap_plastic"] == "是" else 0,
            "corner_protection": 20 if data["corner_protection"] == "是" else 0,
            "report_pallet_size": 0,
            "take_photo": 0,
            "assist_loading": 60 if data["assist_loading"] == "是" else 0,
        }

        total_service_cost_per_pallet = sum(service_costs_per_pallet.values())
        num_pallets = int(data["num_pallets"])
        total_cost = (pallet_price + total_service_cost_per_pallet) * num_pallets
        return round(total_cost, 2)

    except KeyError as e:
        return jsonify({'error': f"Missing key {e} in data: {data}"}), 400 #More specific error
    except (ValueError, TypeError) as e:
        return jsonify({'error': f"Invalid input type - {e}, data: {data}"}), 400 #More specific error
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred - {e}, data: {data}"}), 500


@app.route('/', methods=['POST', 'GET', 'HEAD'])  # Handles POST, GET, and HEAD requests to /
def upload_data():
    if request.method == 'POST':
        try:
            data = request.get_json()
            total_cost = calculate_price(data)
            if isinstance(total_cost, tuple):  # Check for error tuples from calculate_price
                return total_cost
            identifier = str(uuid.uuid4())
            return jsonify({'total_cost': total_cost, 'identifier': identifier})
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON data'}), 400
        except Exception as e:
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    elif request.method == 'GET':
        return jsonify({'message': 'This is a GET request to the root URL'}) # Or a more appropriate response
    elif request.method == 'HEAD':
        return '', 200  # Return an empty response with 200 OK status


port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=port)
