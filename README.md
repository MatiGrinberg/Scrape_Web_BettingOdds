## Project Overview

This project involves scraping archived betting odds from a website using **Selenium** and then calculating the returns from a simulated betting strategy.

### Key Features:
- **Data Collection**: Scraping betting odds from a website using **Selenium**.
- **Betting Strategy**: The strategy involves distributing an equal amount of money across all bets on a specific date, where the payoffs exceed a set threshold.
- **Return Calculation**: The returns are calculated by evaluating the performance of the strategy based on the payoffs.

### How the Strategy Works:
1. **Data Scraping**: The script collects betting data for a given date, including three possible payoffs: Win (W), Draw (D), and Lose (L).
2. **Bet Selection**: For each date, the strategy selects all bets where at least one of the payoffs is higher than the chosen threshold.
3. **Simulated Betting**: Equal amounts of money are distributed to all qualifying bets.
4. **Result Calculation**: The returns are calculated based on the outcome of the bets.

### Outcome:
After simulating the strategy for different threshold values (i.e., the minimum payoff required to place a bet), the results show that, on average, the strategy yields **negative returns**.
