
from flask import Flask, render_template, request
import grpc
import poker_pb2
import poker_pb2_grpc
import os

app = Flask(__name__)

# Backend connection settings
BACKEND_HOST = os.environ.get('BACKEND_HOST', 'localhost')
BACKEND_PORT = os.environ.get('BACKEND_PORT', '50051')

def get_stub():
    """Create a gRPC stub with appropriate channel security."""
    target = f'{BACKEND_HOST}:{BACKEND_PORT}'
    if BACKEND_PORT == '443':
        creds = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(target, creds)
    else:
        channel = grpc.insecure_channel(target)
    return poker_pb2_grpc.PokerServiceStub(channel)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    prob_result = None
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        hole_cards_str = request.form.get('hole_cards', '').upper() # Normalize case
        comm_cards_str = request.form.get('community_cards', '').upper()
        
        # Parse comma-separated inputs
        hole_cards = [c.strip() for c in hole_cards_str.split(',') if c.strip()]
        comm_cards = [c.strip() for c in comm_cards_str.split(',') if c.strip()]
        
        try:
            stub = get_stub()
            
            if action == 'evaluate':
                req = poker_pb2.HandRequest(hole_cards=hole_cards, community_cards=comm_cards)
                response = stub.EvaluateHand(req)
                result = {
                    "rank_name": response.rank_name,
                    "rank_value": response.rank_value,
                    "best_hand": ", ".join(response.best_hand)
                }
                
            elif action == 'probability':
                num_players = int(request.form.get('num_players', 2))
                req = poker_pb2.ProbabilityRequest(
                    hole_cards=hole_cards,
                    community_cards=comm_cards,
                    num_players=num_players,
                    num_simulations=1000
                )
                response = stub.CalculateProbability(req)
                prob_result = {
                    "win": f"{response.win_probability:.1%}",
                    "tie": f"{response.tie_probability:.1%}",
                    "lose": f"{response.lose_probability:.1%}"
                }
                
        except grpc.RpcError as e:
            error = f"RPC Error: {e.details()} (Code: {e.code()})"
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template('index.html', result=result, prob_result=prob_result, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
