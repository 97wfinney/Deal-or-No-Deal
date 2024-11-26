
# Deal or No Deal Simulation

### Project Description

This project simulates the UK version of the popular game show **"Deal or No Deal"**. It runs through a specified number of games (default is 100,000) to analyze different player strategies and their outcomes. The simulation provides insights into the effectiveness of various decision-making approaches when dealing with risk and uncertainty.

### Features

- **Realistic Game Mechanics**: Simulates the UK version with 22 boxes and authentic prize amounts.
- **Multiple Player Strategies**:
  - **Always Play**: Never accepts the banker's deal.
  - **Risk Averse**: Accepts the deal if it's at least 80% of the expected value.
  - **Risk Neutral**: Accepts the deal if it's at least 95% of the expected value.
  - **Risk Seeking**: Only accepts deals that are 120% or more of the expected value.
  - **Target Based**: Accepts the deal if it meets or exceeds a target amount (e.g., £100,000).
  - **Momentum Based**: Considers the trend of offers before deciding.
- **Comprehensive Statistics**:
  - Average, median, and standard deviation of winnings.
  - Deal and swap acceptance rates.
  - Win distribution across different prize ranges.
  - Round-by-round offer statistics.

### Installation and Setup

#### Prerequisites

- Python 3.6 or higher.

#### Clone the Repository

git clone https://github.com/your_username/Deal-or-No-Deal.git
cd Deal-or-No-Deal

### Usage

#### Running the Simulation

You can run the simulation by executing the `deal_sim.py` script:
python deal_sim.py

#### Customizing the Number of Simulations

By default, the script simulates 100,000 games. You can change this number by modifying the `num_games` variable in the `main()` function of `deal_sim.py`:
def main():
    simulator = Simulator()
    num_games = 50000  # Set to your desired number of simulations
    results = simulator.run_simulation(num_games)
    ...

#### Understanding the Output

The simulation results include:

- **Win Distribution**: Shows how winnings are distributed across different prize ranges.
- **Player Strategy Analysis**: Provides detailed statistics for each player strategy.
- **Round Statistics**: Displays average offers and expected values for each round.

### Player Strategies Explained

- **Always Play**: The player always rejects the banker's deal and plays to the end.
- **Risk Averse**: Accepts any deal that is at least 80% of the expected value.
- **Risk Neutral**: Accepts any deal that is at least 95% of the expected value.
- **Risk Seeking**: Only accepts deals that are 120% or more of the expected value.
- **Target Based**: Accepts any deal meeting or exceeding a specific target amount.
- **Momentum Based**: Considers the trend of the banker's offers; if offers are decreasing and the current offer is at least 90% of the expected value, the player accepts the deal.

### Project Structure

- `deal_sim.py`: Main script containing the simulation code.
- `README.md`: Project documentation.
- `.gitignore`: Specifies files and directories to be ignored by Git.

### Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions for improvements or new features.

### License

This project is open-source and available under the [MIT License](LICENSE).

### Acknowledgments

- Inspired by the UK version of **"Deal or No Deal"**.
- Special thanks to the community for support and contributions.