class HistoricalData:
    """
    A class to manage historical data tracking with persistence and change detection.
    Stores timestamped data points and detects significant changes in values.
    """
    
    def __init__(self, history_file="history.json", max_hours=24, cleanup_interval=3600):
        """
        Initialize the historical data manager.
        
        Args:
            history_file (str): Name of file to store historical data
            max_hours (int): Maximum hours of history to maintain
            cleanup_interval (int): Seconds between cleanup operations
        """
        import ujson
        import os
        import time
        
        self.history_file = history_file
        self.max_hours = max_hours
        self.cleanup_interval = cleanup_interval
        self.current_data = None
        self.history = []
        self.last_cleanup = time.time()
        
        # Thresholds for detecting significant changes
        self.thresholds = {
            'balance': 0.01,      # 1% change in balance
            'satori_balance': 0.01,  # 1% change in SATORI balance
            'satori_price': 0.001,   # 0.1% change in price
            'neurons': 1,         # Any change in neuron count
            'stake': 0.01,       # 1% change in stake requirement
        }
        
        self.load_history()

    def load_history(self):
        """Load historical data from file."""
        import ujson
        import os
        
        try:
            if self.history_file in os.listdir():
                with open(self.history_file, 'r') as f:
                    self.history = ujson.loads(f.read())
                print(f"Loaded {len(self.history)} historical entries")
            else:
                self.history = []
                print("No history file found, starting fresh")
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []

    def save_history(self):
        """Save historical data to file."""
        import ujson
        
        try:
            with open(self.history_file, 'w') as f:
                f.write(ujson.dumps(self.history))
            print(f"Saved {len(self.history)} historical entries")
        except Exception as e:
            print(f"Error saving history: {e}")

    def cleanup_old_entries(self):
        """Remove entries older than max_hours."""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (self.max_hours * 3600)
        original_len = len(self.history)
        self.history = [entry for entry in self.history if entry.get('timestamp', 0) > cutoff_time]
        if len(self.history) != original_len:
            print(f"Cleaned up {original_len - len(self.history)} old entries")

    def check_cleanup_needed(self):
        """Check if cleanup is needed based on cleanup_interval."""
        import time
        
        current_time = time.time()
        if current_time - self.last_cleanup >= self.cleanup_interval:
            self.cleanup_old_entries()
            self.save_history()
            self.last_cleanup = current_time
            return True
        return False

    def _check_percentage_change(self, old_val, new_val, threshold):
        """
        Calculate if percentage change between values exceeds threshold.
        
        Args:
            old_val (float): Previous value
            new_val (float): New value
            threshold (float): Change threshold (as decimal)
            
        Returns:
            bool: True if change exceeds threshold
        """
        if old_val == 0 and new_val == 0:
            return False
        if old_val == 0:
            return True
        change = abs((new_val - old_val) / old_val)
        return change > threshold

    def has_significant_changes(self, new_data):
        """
        Check if new data shows significant changes from current data.
        
        Args:
            new_data (dict): New data point to compare
            
        Returns:
            bool: True if significant changes detected
        """
        if not self.current_data:
            return True

        # Check balance changes
        if self._check_percentage_change(
            self.current_data['balance_data']['balance'],
            new_data['balance_data']['balance'],
            self.thresholds['balance']
        ):
            print("Significant change in balance detected")
            return True

        # Check SATORI balance changes
        if self._check_percentage_change(
            self.current_data['balance_data']['assets']['SATORI'],
            new_data['balance_data']['assets']['SATORI'],
            self.thresholds['satori_balance']
        ):
            print("Significant change in SATORI balance detected")
            return True

        # Check price changes
        if (self.current_data['satori_price'] is not None and 
            new_data['satori_price'] is not None and
            self._check_percentage_change(
                self.current_data['satori_price'],
                new_data['satori_price'],
                self.thresholds['satori_price']
            )):
            print("Significant change in SATORI price detected")
            return True

        # Check neuron and stake changes
        if (self.current_data['neurons_data'] and new_data['neurons_data']):
            if (abs(self.current_data['neurons_data']['competing_neurons'] - 
                   new_data['neurons_data']['competing_neurons']) >= self.thresholds['neurons']):
                print("Change in neuron count detected")
                return True
                
            if self._check_percentage_change(
                self.current_data['neurons_data']['current_stake_requirement'],
                new_data['neurons_data']['current_stake_requirement'],
                self.thresholds['stake']
            ):
                print("Significant change in stake requirement detected")
                return True

        return False

    def update_data(self, balance_data, neurons_data, satori_price):
        """
        Update historical data with new values.
        
        Args:
            balance_data (dict): Current balance information
            neurons_data (dict): Current neuron statistics
            satori_price (float): Current SATORI price
            
        Returns:
            bool: True if display should be updated
        """
        import time
        
        new_data = {
            'timestamp': time.time(),
            'balance_data': balance_data,
            'neurons_data': neurons_data,
            'satori_price': satori_price
        }

        should_update = self.has_significant_changes(new_data)

        if should_update:
            self.history.append(new_data)
            self.current_data = new_data
            self.save_history()
            print("Data updated due to significant changes")

        self.check_cleanup_needed()
        return should_update

    def get_statistics(self):
        """
        Calculate statistics from historical data.
        
        Returns:
            dict: Statistics including min, max, and average values
        """
        if not self.history:
            return None
            
        stats = {
            'satori_balance': {
                'min': float('inf'),
                'max': float('-inf'),
                'avg': 0
            },
            'satori_price': {
                'min': float('inf'),
                'max': float('-inf'),
                'avg': 0
            }
        }
        
        price_count = 0
        balance_sum = 0
        price_sum = 0
        
        for entry in self.history:
            # SATORI balance stats
            balance = entry['balance_data']['assets']['SATORI']
            stats['satori_balance']['min'] = min(stats['satori_balance']['min'], balance)
            stats['satori_balance']['max'] = max(stats['satori_balance']['max'], balance)
            balance_sum += balance
            
            # Price stats
            if entry['satori_price'] is not None:
                price = entry['satori_price']
                stats['satori_price']['min'] = min(stats['satori_price']['min'], price)
                stats['satori_price']['max'] = max(stats['satori_price']['max'], price)
                price_sum += price
                price_count += 1
        
        # Calculate averages
        stats['satori_balance']['avg'] = balance_sum / len(self.history)
        if price_count > 0:
            stats['satori_price']['avg'] = price_sum / price_count
        
        return stats