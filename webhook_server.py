from flask import Flask, request, jsonify
import json
import os
import uuid
import hmac
import hashlib

app = Flask(__name__)

# --- Configuration ---
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET") #Get this from a secure environment variable
if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET environment variable must be set.")


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

def verify_webhook_signature(request, secret):
    """Verifies the webhook signature to prevent unauthorized access."""
    signature = request.headers.get('X-Webhook-Signature')
    if not signature:
        return False

    body = request.get_data()
    expected_signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

@app.route('/', methods=['POST', 'GET', 'HEAD'])
def upload_data():
    if request.method == 'POST':
        try:
            data = request.get_json()
            total_cost = calculate_price(data)
            if isinstance(total_cost, tuple): #Handle errors from calculate_price
                return total_cost #Return the error response

            response_data = {
                'total_cost': total_cost,
                'identifier': str(uuid.uuid4()),
                'am_pm': data.get('am_pm'),
                'do_number': data.get('do_number'),
                'num_pallets': data.get('num_pallets'),
                'delivery_date': data.get('delivery_date'),
                'bu': data.get('bu'),
                'customer_name': data.get('customer_name'),
            }
            return jsonify(response_data)

        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON data'}), 400
        except Exception as e:
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    elif request.method == 'GET':
        return jsonify({'message': 'This is a GET request to the root URL'}), 200 #Corrected response
    elif request.method == 'HEAD':
        return '', 200  #This is correct

@app.route('/webhook', methods=['POST']) #New Webhook endpoint
def webhook():
    if not verify_webhook_signature(request, WEBHOOK_SECRET):
        return jsonify({'error': 'Invalid webhook signature'}), 403 #Unauthorized

    try:
        data = request.get_json()
        # Process the data received from the webhook
        total_cost = calculate_price(data)
        if isinstance(total_cost, tuple): #Handle errors from calculate_price
            return total_cost #Return the error response
        # ... perform database operations or other actions ...
        return jsonify({'message': 'Webhook data processed successfully'}), 200
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=port)
