import numpy as np
import pandas as pd
import multiprocessing

def simulate_mining(days, blocks_per_day, p_hashrate, reward_per_block, pool_fee_percent, reserve_share, initial_reserve, runs):
    daily_pool_blocks = np.random.binomial(n=blocks_per_day, p=p_hashrate, size=(runs, days))
    daily_rewards = reward_per_block * daily_pool_blocks
    daily_payout_fpps = reward_per_block * blocks_per_day * p_hashrate * (1 - pool_fee_percent * reserve_share)
    daily_net_change = daily_rewards - daily_payout_fpps
    cumulative_reserves = np.cumsum(daily_net_change, axis=1) + initial_reserve
    survival_count = np.all(cumulative_reserves > 0, axis=1).sum()
    return 100 * survival_count / runs


def find_min_reserve_binary_search(params):
    days, blocks_per_day, p_hashrate, reward_per_block, pool_fee_percent, reserve_share, target_survival_rate, runs, low, high, precision = params
    survival_rate = 0
    while abs(survival_rate - target_survival_rate) > precision:
        mid = int((low + high) / 2)
        survival_rate = simulate_mining(days, blocks_per_day, p_hashrate, reward_per_block, pool_fee_percent, reserve_share, mid, runs)
        if survival_rate >= target_survival_rate:
            high = mid
        else:
            low = mid
    return (round(p_hashrate, 4), round(mid / 1e8, 0))

if __name__ == '__main__':
    for target_survival_rate in [95,99]:
        for year in [1,3]:
            for cycle in range(1):
                days = 365 * year
                blocks_per_day = 144
                reward_per_block = 3.125 * 100_000_000
                pool_fee_percent = 0.01
                reserve_share = 0.5
                runs = 100000 
                low = 0
                high = 10000 * 1e8 
                precision = 0.2*(100-target_survival_rate)
                min_hash = 0.01
                max_hash = 0.1
                step = 0.01
                hashrate_range = np.arange(min_hash, max_hash+step, step) 
                param_list = [(days, blocks_per_day, h, reward_per_block, pool_fee_percent, reserve_share, target_survival_rate, runs, low, high, precision) for h in hashrate_range]
                pool = multiprocessing.Pool(processes=4)
                results = pool.map(find_min_reserve_binary_search, param_list)
                pool.close()
                pool.join()
                df = pd.DataFrame(results, columns=['Hashrate', 'Min_Reserve'])
                df.to_csv(f"data/{target_survival_rate}_{year}-{runs}_{precision}_{cycle}.csv", index=False)
