import random

class DealOrNoDeal:
    def __init__(self):
        # Initialize prize values in pounds
        self.prizes = [0.01, 1, 5, 10, 25, 50, 75, 100, 200, 300, 400, 500, 750, 1000, 5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000]
        self.boxes = {}
        self.player_box = None
        self.remaining_boxes = set(range(1, 27))
        self.opened_boxes = {}
        self.offer_number = 0  # Track which offer number we're on
        self.setup_game()

    def setup_game(self):
        # Randomly assign prizes to boxes
        available_prizes = self.prizes.copy()
        for box_number in range(1, 27):
            prize = random.choice(available_prizes)
            self.boxes[box_number] = prize
            available_prizes.remove(prize)
        
        # Assign player's box
        self.player_box = random.randint(1, 26)
        self.remaining_boxes.remove(self.player_box)

    def calculate_offer(self):
        # Calculate expected value of remaining boxes
        remaining_values = [self.boxes[box] for box in self.remaining_boxes]
        remaining_values.append(self.boxes[self.player_box])
        expected_value = sum(remaining_values) / len(remaining_values)
        
        # UK show banker strategy: Linear progression from 37% to 84% over 7 offers
        self.offer_number += 1
        offer_percentages = {
            1: 0.37,  # First offer: 37% of EV
            2: 0.45,  # Linear progression
            3: 0.53,
            4: 0.61,
            5: 0.69,
            6: 0.77,
            7: 0.84   # Final offer: 84% of EV
        }
        
        offer_percentage = offer_percentages.get(self.offer_number, 0.84)  # Default to 84% if beyond 7 offers
        return round(expected_value * offer_percentage, 2)

    def open_box(self, box_number):
        if box_number not in self.remaining_boxes:
            return False, "Invalid box number"
        
        prize = self.boxes[box_number]
        self.remaining_boxes.remove(box_number)
        self.opened_boxes[box_number] = prize
        return True, prize

    def display_remaining_prizes(self):
        remaining_values = [self.boxes[box] for box in self.remaining_boxes]
        remaining_values.append(self.boxes[self.player_box])
        remaining_values.sort()
        print("\nRemaining prizes:")
        for value in remaining_values:
            if value < 1:
                print(f"{value:,.2f}p")  # Display in pence if less than £1
            else:
                print(f"£{value:,.2f}")

    def play_game(self):
        print("Welcome to Deal or No Deal!")
        print(f"\nYou have been assigned box number {self.player_box}")
        
        # Opening round - open 5 boxes
        print("\n=== First Round ===")
        print("Open 5 boxes")
        self.play_round(5)
        
        # Subsequent rounds - open 3 boxes until only 2 boxes remain
        round_number = 2
        while len(self.remaining_boxes) > 1:  # Continue until only 1 box remains against player's box
            print(f"\n=== Round {round_number} ===")
            boxes_to_open = min(3, len(self.remaining_boxes) - 1)  # Ensure we leave at least 1 box
            if boxes_to_open > 0:
                print(f"Open {boxes_to_open} boxes")
                self.play_round(boxes_to_open)
            round_number += 1

        # Final decision
        last_box = list(self.remaining_boxes)[0]
        print("\n=== Final Decision ===")
        print(f"There are two boxes remaining:")
        print(f"Your box (Box {self.player_box})")
        print(f"The final box (Box {last_box})")
        
        while True:
            choice = input("\nDo you want to keep your box or switch? (keep/switch): ").lower()
            if choice in ['keep', 'switch']:
                break
            print("Please enter 'keep' or 'switch'")
        
        if choice == 'keep':
            won_amount = self.boxes[self.player_box]
            other_amount = self.boxes[last_box]
        else:
            won_amount = self.boxes[last_box]
            other_amount = self.boxes[self.player_box]
        
        print(f"\nFinal Results:")
        print(f"Your box contained: £{self.boxes[self.player_box]:,.2f}")
        print(f"The other box contained: £{self.boxes[last_box]:,.2f}")
        print(f"\nYou won: £{won_amount:,.2f}")

    def play_round(self, boxes_to_open):
        # Open boxes
        for _ in range(boxes_to_open):
            self.display_remaining_prizes()
            print(f"\nRemaining box numbers: {sorted(list(self.remaining_boxes))}")
            
            while True:
                try:
                    choice = int(input("\nWhich box would you like to open? "))
                    success, result = self.open_box(choice)
                    if success:
                        if result < 1:
                            print(f"Box {choice} contains: {result:,.2f}p")  # Display in pence if less than £1
                        else:
                            print(f"Box {choice} contains: £{result:,.2f}")
                        break
                    else:
                        print(result)
                except ValueError:
                    print("Please enter a valid box number")
        
        # Make offer if there's more than one box remaining
        if len(self.remaining_boxes) > 1:
            offer = self.calculate_offer()
            print(f"\nThe banker offers: £{offer:,.2f}")
            
            while True:
                deal = input("Deal or No Deal? (D/N): ").upper()
                if deal in ['D', 'N']:
                    break
                print("Please enter 'D' for Deal or 'N' for No Deal")
            
            if deal == 'D':
                print(f"\nCongratulations! You won £{offer:,.2f}")
                print(f"Your box contained: £{self.boxes[self.player_box]:,.2f}")
                exit()

# Play the game
def main():
    game = DealOrNoDeal()
    game.play_game()

if __name__ == "__main__":
    main()