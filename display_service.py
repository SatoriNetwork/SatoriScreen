# display_service.py

import urequests
import ujson
import gc
import time
from scaled_text import ScaledText
from bitmaps import SATORI_BITMAP, LOLLIPOP_BITMAP, SATORI_LOGO

class DisplayService:
    def __init__(self, epd_width=128, epd_height=296):
        self.EPD_WIDTH = epd_width
        self.EPD_HEIGHT = epd_height
        
    def fetch_neurons_data(self, watchdog):
        """Fetch current Satori Network statistics."""
        try:
            watchdog.feed()
            gc.collect()
            response = urequests.get(
                "https://satorinet.io/reports/daily/stats/predictors/latest",
                headers={'Accept': 'application/json'}
            )
            valid_json = response.text.replace("NaN", "null")
            response=None
            gc.collect()
            data = ujson.loads(valid_json)
            valid_json=None
            gc.collect()
            
            return {
                "current_stake_requirement": float(data.get("Current Staking Requirement", 0.0)),
                "current_neuron_version": data.get("Current Neuron Version", "Unknown"),
                "competing_neurons": int(data.get("Competing Neurons", 0))
            }
        except Exception as e:
            print(f"Error fetching neurons data: {e}")
            return None
        finally:
            try:
                response.close()
            except:
                pass

    def fetch_all_address_info(self, addresses, watchdog):
        """Fetch balance and asset information for all configured addresses."""
        total_balance = 0.0
        total_assets = {"SATORI": 0.0, "LOLLIPOP": 0.0}

        for address in addresses:
            for attempt in range(3):
                try:
                    watchdog.feed()
                    gc.collect()
                    response = urequests.get(f"https://evr.cryptoscope.io/api/getaddress/?address={address}")
                    if response.status_code == 200:
                        data = response.json()
                        response=None
                        gc.collect()
                        total_balance += float(data.get("balance", 0.0))
                        
                        assets = data.get("assets", {})
                        for asset in total_assets:
                            if asset in assets:
                                total_assets[asset] += float(assets[asset])
                        data = None
                        gc.collect()
                        break
                except Exception as e:
                    print(f"Error fetching address {address} (attempt {attempt + 1}): {e}")
                    if attempt < 2:
                        time.sleep(2)

        return {"balance": total_balance, "assets": total_assets}

    def get_satori_price(self, watchdog):
        """Fetch current SATORI price from Safe.Trade."""
        try:
            watchdog.feed()
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            }
            gc.collect()
            response = urequests.get("https://safe.trade/api/v2/trade/public/tickers/satoriusdt", 
                                headers=headers)
            if response.status_code == 200:
                return float(response.json()['avg_price'])
            return None
        except Exception as e:
            print(f"Error fetching SATORI price: {e}")
            return None
        finally:
            try:
                response.close()
            except:
                pass

    def update_display(self, epd, text_handler, balance_data, neurons_data, satori_price, watchdog, stats=None):
        """Update the e-paper display with current data."""
        try:
            print("Starting display update...")
            epd.fill(1)
            watchdog.feed()

            # Draw SATORI logo and balance
            try:
                text_handler.draw_bitmap(0, 0, SATORI_LOGO, 103, 32)
                satori_balance = balance_data["assets"].get("SATORI", 0.0)
                text_handler.draw_scaled_text(f"{satori_balance:.2f}", 0, 40, scale=3)
            except Exception as e:
                print(f"Error drawing SATORI section: {e}")

            # Draw SATORI price with dynamic positioning
            try:
                if satori_price is not None:
                    price_str = str(satori_price)
                    adjusted_x = 200 - (max(0, len(price_str) - 5) * 16)
                    text_handler.draw_scaled_text(f"${satori_price}", adjusted_x, 0, scale=2)
            except Exception as e:
                print(f"Error drawing price section: {e}")

            watchdog.feed()

            # Draw EVR balance
            try:
                evr_balance = balance_data.get('balance', 0.0)
                text_handler.draw_scaled_text(f"EVR: {evr_balance:.2f}", 0, 80, scale=2)
            except Exception as e:
                print(f"Error drawing EVR balance: {e}")

            # Draw timestamp
            try:
                current_time = time.localtime()
                text_handler.draw_scaled_text(
                    "Updated: %02d:%02d %02d/%02d/%02d" % 
                    (current_time[3], current_time[4], current_time[2], 
                     current_time[1], current_time[0] % 100), 
                    0, 112, scale=1
                )
            except Exception as e:
                print(f"Error drawing timestamp: {e}")

            watchdog.feed()

            # Draw network statistics
            try:
                if neurons_data:
                    text_handler.draw_scaled_text(
                        f"V: {neurons_data.get('current_neuron_version', 'Unknown')} "
                        f"NEURONS: {neurons_data.get('competing_neurons', 0)} "
                        f"STAKE: {neurons_data.get('current_stake_requirement', 0.0)}", 
                        0, 120, scale=1
                    )
            except Exception as e:
                print(f"Error drawing network stats: {e}")

            # Draw historical stats if available
            try:
                if stats:
                    y_position = 100
                    if 'price_change' in stats:
                        text_handler.draw_scaled_text(
                            f"24h: {stats['price_change']:+.2f}%",
                            0, y_position, scale=1
                        )
            except Exception as e:
                print(f"Error drawing historical stats: {e}")

            # Draw LOLLIPOP icon if present
            try:
                if balance_data["assets"].get("LOLLIPOP", 0) > 0:
                    text_handler.draw_bitmap(261, 86, LOLLIPOP_BITMAP, 32, 32)
            except Exception as e:
                print(f"Error drawing LOLLIPOP icon: {e}")

            print("Display update completed successfully")
            return True

        except Exception as e:
            print(f"Critical error in update_display: {e}")
            return False
