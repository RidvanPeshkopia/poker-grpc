
from concurrent import futures
import os
import grpc
import poker_pb2
import poker_pb2_grpc
import hand_rank

class PokerService(poker_pb2_grpc.PokerServiceServicer):
    def EvaluateHand(self, request, context):
        try:
            # Combine hole and community cards into a single list
            # We assume input is like ["Ah", "Kd"] etc.
            all_cards = list(request.hole_cards) + list(request.community_cards)
            
            if len(all_cards) < 5:
                # Not enough cards for a full hand, but we can still evaluate strength of what we have 
                # or just return error/empty.
                # Standard Texas Hold'em uses best 5 of 7.
                # If less than 5, maybe just "High Card"?
                # But best_hand logic expects at least 5 for combinations.
                # Let's just pass them all and let hand_rank handle it?
                # Actually hand_rank.best_hand() does itertools.combinations(cards, 5).
                # So we need at least 5 cards.
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Need at least 5 cards to evaluate a hand.')
                return poker_pb2.HandResponse()

            result = hand_rank.best_hand(all_cards)
            
            return poker_pb2.HandResponse(
                rank_value=result['rank_value'],
                rank_name=result['rank_name'],
                best_hand=result['best_hand']
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return poker_pb2.HandResponse()

    def CompareHands(self, request, context):
        try:
            # Assuming shared community cards are passed or implied?
            # The proto definition has separate HandRequests.
            # HandRequest has hole_cards AND community_cards.
            # Usually community cards are shared.
            # Let's perform comparison based on what is in the request.
            
            h1_cards = list(request.hand1.hole_cards)
            h1_comm = list(request.hand1.community_cards)
            
            h2_cards = list(request.hand2.hole_cards)
            h2_comm = list(request.hand2.community_cards)
            
            # If h2_comm is empty, maybe they share h1_comm?
            # Let's assume explicit input for now.
            
            # Use raw compare logic
            # This logic internally finds best hand for each
            # But compare_hands signature is (h1, h2, comm).
            # If they have DIFFERENT community cards (unlikely in Holdem but possible in other games),
            # we should just compare their best hands.
            
            best1 = hand_rank.best_hand(h1_cards + h1_comm)
            best2 = hand_rank.best_hand(h2_cards + h2_comm)
            
            winner = 0
            winning_hand_name = "Tie"
            
            if best1['rank_tuple'] > best2['rank_tuple']:
                winner = 1
                winning_hand_name = best1['rank_name']
            elif best2['rank_tuple'] > best1['rank_tuple']:
                winner = 2
                winning_hand_name = best2['rank_name']
            else:
                winner = 0
                winning_hand_name = best1['rank_name'] # Same name
                
            return poker_pb2.CompareResponse(
                winner=winner,
                winning_hand_name=winning_hand_name
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return poker_pb2.CompareResponse()

    def CalculateProbability(self, request, context):
        try:
            result = hand_rank.calculate_probability(
                list(request.hole_cards),
                list(request.community_cards),
                request.num_players,
                request.num_simulations or 1000
            )
            
            return poker_pb2.ProbabilityResponse(
                win_probability=result['win'],
                tie_probability=result['tie'],
                lose_probability=result['lose']
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return poker_pb2.ProbabilityResponse()

def serve():
    port = os.environ.get('PORT', '50051')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    poker_pb2_grpc.add_PokerServiceServicer_to_server(PokerService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Server started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
