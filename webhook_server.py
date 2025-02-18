from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/upload_data', methods=['POST'])
def upload_data():
    try:
        data = request.get_json()
        total_cost = calculate_price(data)
        identifier = str(uuid.uuid4())  # Generate a UUID
        return jsonify({'total_cost': total_cost, 'identifier': identifier})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        return f"Pricing error: Missing key {e} in data: {data}"
    except (ValueError, TypeError) as e:
        return f"Pricing error: Invalid input type - {e}, data: {data}"
    except Exception as e:
        return f"Pricing error: An unexpected error occurred - {e}, data: {data}"

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=port) # Run the Flask app, but only if this script is run directly.
