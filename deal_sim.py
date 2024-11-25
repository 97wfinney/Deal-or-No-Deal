import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import statistics
from enum import Enum

class PlayerStrategy(Enum):
    ALWAYS_PLAY = "always_play"
    RISK_AVERSE = "risk_averse"
    RISK_NEUTRAL = "risk_neutral"
    RISK_SEEKING = "risk_seeking"
    TARGET_BASED = "target_based"
    MOMENTUM_BASED = "momentum_based"

class BankerStrategy(Enum):
    STANDARD = "standard"  # Actual UK show strategy (37% to 84%)

@dataclass
class Banker:
    strategy: BankerStrategy
    player_decisions: List[bool] = None
    offer_number: int = 0

    def __post_init__(self):
        self.player_decisions = []
        self.last_offer_percentage = None

    def get_standard_percentage(self, offer_number: int) -> float:
        """Get the standard UK show percentage for each offer"""
        percentages = [0.37, 0.45, 0.53, 0.61, 0.69, 0.77, 0.84]
        return percentages[min(offer_number - 1, len(percentages) - 1)]

    def calculate_offer(self, expected_value: float, offer_number: int) -> Tuple[float, float]:
        """Calculate offer based on strategy. Returns (offer, offer_percentage)"""
        self.offer_number += 1
        offer_percentage = self.get_standard_percentage(self.offer_number)
        self.last_offer_percentage = offer_percentage
        return round(expected_value * offer_percentage, 2), offer_percentage

    def record_decision(self, accepted: bool):
        self.player_decisions.append(accepted)

@dataclass
class Agent:
    name: str
    strategy: PlayerStrategy
    target_amount: float = 0

    def evaluate_offer(self, offer: float, expected_value: float, previous_offers: List[float]) -> bool:
        if self.strategy == PlayerStrategy.ALWAYS_PLAY:
            return False

        elif self.strategy == PlayerStrategy.RISK_AVERSE:
            return offer >= 0.8 * expected_value

        elif self.strategy == PlayerStrategy.RISK_NEUTRAL:
            return offer >= 0.95 * expected_value

        elif self.strategy == PlayerStrategy.RISK_SEEKING:
            return offer >= 1.2 * expected_value

        elif self.strategy == PlayerStrategy.TARGET_BASED:
            return offer >= self.target_amount

        elif self.strategy == PlayerStrategy.MOMENTUM_BASED:
            if len(previous_offers) < 2:
                return False
            offer_trend = previous_offers[-1] - previous_offers[-2]
            return offer_trend < 0 and offer >= 0.9 * expected_value

class SimulatedGame:
    def __init__(self):
        # UK version prizes
        self.prizes = [0.01, 0.10, 0.50, 1, 5, 10, 50, 100, 250, 500, 750, 1000,
                       3000, 5000, 10000, 15000, 20000, 35000, 50000, 75000,
                       100000, 250000]
        self.banker = Banker(BankerStrategy.STANDARD)
        self.reset_game()

    def reset_game(self):
        self.boxes = {}
        self.player_box = None
        self.remaining_boxes = set(range(1, 23))  # Boxes from 1 to 22
        self.opened_boxes = {}
        self.previous_offers = []
        self.setup_game()

    def setup_game(self):
        available_prizes = self.prizes.copy()
        for box_number in range(1, 23):
            prize = random.choice(available_prizes)
            self.boxes[box_number] = prize
            available_prizes.remove(prize)
        self.player_box = random.randint(1, 22)
        self.remaining_boxes.remove(self.player_box)

    def calculate_expected_value(self):
        remaining_values = [self.boxes[box] for box in self.remaining_boxes]
        remaining_values.append(self.boxes[self.player_box])
        return statistics.mean(remaining_values)

    def open_boxes(self, num_boxes: int) -> List[float]:
        opened_values = []
        for _ in range(num_boxes):
            if self.remaining_boxes:
                box = random.choice(list(self.remaining_boxes))
                value = self.boxes[box]
                self.remaining_boxes.remove(box)
                self.opened_boxes[box] = value
                opened_values.append(value)
        return opened_values

    def simulate_round(self, agent: Agent) -> Dict:
        rounds = [(5, "first"), (3, "second"), (3, "third"), (3, "fourth"),
                  (3, "fifth"), (3, "sixth")]
        total_rounds = len(rounds)
        round_results = []

        for round_num, (boxes_to_open, round_name) in enumerate(rounds, 1):
            # Open boxes for this round
            opened_values = self.open_boxes(boxes_to_open)

            expected_value = self.calculate_expected_value()
            offer, offer_percentage = self.banker.calculate_offer(expected_value, self.banker.offer_number + 1)
            self.previous_offers.append(offer)

            # Record round statistics
            round_results.append({
                "round": round_num,
                "expected_value": expected_value,
                "offer": offer,
                "offer_percentage": offer_percentage,
                "remaining_boxes": len(self.remaining_boxes),
                "opened_values": opened_values
            })

            deal_accepted = agent.evaluate_offer(offer, expected_value, self.previous_offers)
            self.banker.record_decision(deal_accepted)

            if deal_accepted:
                return {
                    "result": "accepted_deal",
                    "amount_won": offer,
                    "box_value": self.boxes[self.player_box],
                    "round": round_name,
                    "remaining_boxes": len(self.remaining_boxes),
                    "expected_value": expected_value,
                    "offer_percentage": offer_percentage,
                    "round_results": round_results
                }

        # Final Offer after all rounds
        expected_value = self.calculate_expected_value()
        offer, offer_percentage = self.banker.calculate_offer(expected_value, self.banker.offer_number + 1)
        self.previous_offers.append(offer)

        # Record final round statistics
        round_results.append({
            "round": self.banker.offer_number,
            "expected_value": expected_value,
            "offer": offer,
            "offer_percentage": offer_percentage,
            "remaining_boxes": len(self.remaining_boxes),
            "opened_values": []
        })

        deal_accepted = agent.evaluate_offer(offer, expected_value, self.previous_offers)
        self.banker.record_decision(deal_accepted)

        if deal_accepted:
            return {
                "result": "accepted_deal",
                "amount_won": offer,
                "box_value": self.boxes[self.player_box],
                "round": "final",
                "remaining_boxes": len(self.remaining_boxes),
                "expected_value": expected_value,
                "offer_percentage": offer_percentage,
                "round_results": round_results
            }

        # Decide whether to offer a box swap (e.g., 40% chance)
        swap_offer_made = random.random() < 0.4

        if swap_offer_made:
            # Offer to swap boxes
            swap_accepted = self.player_accepts_swap(agent)
            if swap_accepted:
                # Swap player box with the remaining box
                remaining_box = self.remaining_boxes.pop()
                self.remaining_boxes.add(self.player_box)
                self.player_box = remaining_box
        else:
            swap_accepted = False

        # Record swap decision
        round_results[-1].update({
            "swap_offer_made": swap_offer_made,
            "swap_accepted": swap_accepted
        })

        # Reveal the final prize
        return {
            "result": "played_to_end",
            "amount_won": self.boxes[self.player_box],
            "box_value": self.boxes[self.player_box],
            "round": "final",
            "remaining_boxes": len(self.remaining_boxes),
            "swap_offer_made": swap_offer_made,
            "swap_accepted": swap_offer_made and swap_accepted,
            "round_results": round_results
        }

    def player_accepts_swap(self, agent: Agent) -> bool:
        # Simple logic: risk-averse players may not swap, risk-seeking players may swap
        if agent.strategy == PlayerStrategy.RISK_SEEKING:
            return True
        elif agent.strategy == PlayerStrategy.RISK_AVERSE:
            return False
        else:
            # For other strategies, decide randomly
            return random.choice([True, False])

class Simulator:
    def __init__(self):
        self.agents = self.create_agents()

    def create_agents(self) -> List[Agent]:
        return [
            Agent("Always Play Andy", PlayerStrategy.ALWAYS_PLAY),
            Agent("Risk Averse Rachel", PlayerStrategy.RISK_AVERSE),
            Agent("Neutral Nancy", PlayerStrategy.RISK_NEUTRAL),
            Agent("Risk Seeking Rick", PlayerStrategy.RISK_SEEKING),
            Agent("Target Tom", PlayerStrategy.TARGET_BASED, target_amount=100000),
            Agent("Momentum Mike", PlayerStrategy.MOMENTUM_BASED)
        ]

    def run_simulation(self, num_games: int) -> Dict:
        results = []
        round_stats = []
        win_distribution = {
            "£0-£1,000": 0,
            "£1,001-£10,000": 0,
            "£10,001-£50,000": 0,
            "£50,001-£100,000": 0,
            "£100,001+": 0
        }

        for _ in range(num_games):
            agent = random.choice(self.agents)
            game = SimulatedGame()
            game_result = game.simulate_round(agent)

            # Record game result
            results.append({
                "agent_name": agent.name,
                "player_strategy": agent.strategy.value,
                **game_result
            })

            # Update win distribution
            amount_won = game_result["amount_won"]
            if amount_won <= 1000:
                win_distribution["£0-£1,000"] += 1
            elif amount_won <= 10000:
                win_distribution["£1,001-£10,000"] += 1
            elif amount_won <= 50000:
                win_distribution["£10,001-£50,000"] += 1
            elif amount_won <= 100000:
                win_distribution["£50,001-£100,000"] += 1
            else:
                win_distribution["£100,001+"] += 1

            # Collect round statistics
            round_stats.extend(game_result.get("round_results", []))

        # Process results into format needed for analysis
        analysis = self.analyze_results(results)

        return {
            "playerResults": analysis["player_results"],
            "winDistribution": win_distribution,
            "roundStats": self.aggregate_round_stats(round_stats)
        }

    def aggregate_round_stats(self, round_stats: List[Dict]) -> List[Dict]:
        # Group stats by round
        rounds = {}
        for stat in round_stats:
            round_num = stat["round"]
            if round_num not in rounds:
                rounds[round_num] = {
                    "offers": [],
                    "offer_percentages": [],
                    "expected_values": []
                }
            rounds[round_num]["offers"].append(stat["offer"])
            rounds[round_num]["offer_percentages"].append(stat["offer_percentage"])
            rounds[round_num]["expected_values"].append(stat["expected_value"])

        # Calculate averages for each round
        return [{
            "round": round_num,
            "averageOffer": statistics.mean(data["offers"]),
            "averageOfferPercentage": statistics.mean(data["offer_percentages"]),
            "averageExpectedValue": statistics.mean(data["expected_values"])
        } for round_num, data in sorted(rounds.items(), key=lambda x: int(x[0]))]

    def analyze_results(self, results: List[Dict]) -> Dict:
        player_results = {}

        # Process each game result
        for result in results:
            # Player strategy analysis
            player_strat = result["player_strategy"]
            if player_strat not in player_results:
                player_results[player_strat] = []
            player_results[player_strat].append(result)

        # Calculate statistics for each category
        return {
            "player_results": self.calculate_strategy_stats(player_results)
        }

    def calculate_strategy_stats(self, grouped_results: Dict) -> Dict:
        stats = {}
        for strategy, results in grouped_results.items():
            amounts_won = [r["amount_won"] for r in results]
            box_values = [r["box_value"] for r in results]
            deals_accepted = len([r for r in results if r["result"] == "accepted_deal"])
            swaps_accepted = len([r for r in results if r.get("swap_accepted")])
            swaps_offered = len([r for r in results if r.get("swap_offer_made")])
            rounds_played = [
                len(r["round_results"]) + 1 if r["result"] == "played_to_end" else len(r["round_results"])
                for r in results
            ]

            stats[strategy] = {
                "average_winnings": statistics.mean(amounts_won),
                "median_winnings": statistics.median(amounts_won),
                "std_winnings": statistics.stdev(amounts_won) if len(amounts_won) > 1 else 0,
                "max_winnings": max(amounts_won),
                "min_winnings": min(amounts_won),
                "25th_percentile": statistics.quantiles(amounts_won, n=4)[0],
                "75th_percentile": statistics.quantiles(amounts_won, n=4)[2],
                "deal_acceptance_rate": deals_accepted / len(results),
                "swap_acceptance_rate": swaps_accepted / swaps_offered if swaps_offered > 0 else 0,
                "better_than_box_rate": len([1 for r in results
                                             if r["amount_won"] > r["box_value"]]) / len(results),
                "average_rounds_played": statistics.mean(rounds_played),
                "median_rounds_played": statistics.median(rounds_played),
            }

            if deals_accepted > 0:
                accepted_deals = [r for r in results if r["result"] == "accepted_deal"]
                stats[strategy]["average_offer_percentage"] = statistics.mean(
                    [r["offer_percentage"] for r in accepted_deals]
                )

        return stats

def main():
    simulator = Simulator()
    num_games = 100000  # Simulate 10,000 games
    results = simulator.run_simulation(num_games)

    # Print the results to the terminal
    print("\n--- Deal or No Deal Simulation Results ---\n")
    print(f"Total Games Simulated: {num_games}\n")

    # Win Distribution
    print("Win Distribution:")
    for k, v in results["winDistribution"].items():
        print(f"  {k}: {v} games ({v / num_games * 100:.2f}%)")
    print("\n")

    # Player Strategy Analysis
    print("Player Strategy Analysis:")
    for strategy, data in results["playerResults"].items():
        print(f"\nStrategy: {strategy.replace('_', ' ').title()}")
        print(f"  Average Winnings: £{data['average_winnings']:.2f}")
        print(f"  Median Winnings: £{data['median_winnings']:.2f}")
        print(f"  Std Dev of Winnings: £{data['std_winnings']:.2f}")
        print(f"  Max Winnings: £{data['max_winnings']:.2f}")
        print(f"  Min Winnings: £{data['min_winnings']:.2f}")
        print(f"  25th Percentile: £{data['25th_percentile']:.2f}")
        print(f"  75th Percentile: £{data['75th_percentile']:.2f}")
        print(f"  Deal Acceptance Rate: {data['deal_acceptance_rate'] * 100:.2f}%")
        print(f"  Swap Acceptance Rate: {data['swap_acceptance_rate'] * 100:.2f}%")
        print(f"  Better Than Box Rate: {data['better_than_box_rate'] * 100:.2f}%")
        print(f"  Average Rounds Played: {data['average_rounds_played']:.2f}")
        print(f"  Median Rounds Played: {data['median_rounds_played']:.2f}")
        if 'average_offer_percentage' in data:
            print(f"  Average Offer Percentage: {data['average_offer_percentage'] * 100:.2f}%")

    # Round Statistics
    print("\nRound Statistics:")
    for round_data in results["roundStats"]:
        print(f"  Round {round_data['round']}:")
        print(f"    Average Offer: £{round_data['averageOffer']:.2f}")
        print(f"    Average Offer Percentage: {round_data['averageOfferPercentage'] * 100:.2f}%")
        print(f"    Average Expected Value: £{round_data['averageExpectedValue']:.2f}")

if __name__ == "__main__":
    main()