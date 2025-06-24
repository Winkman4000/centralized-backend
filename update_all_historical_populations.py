#!/usr/bin/env python3
"""
Master script to update all historical population data (2020-2023) in the temporal geography database.
"""

import subprocess
import sys
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_script(script_name, year):
    """Run a population update script and handle any errors."""
    try:
        logger.info(f"🚀 Starting {year} population data update...")
        start_time = time.time()
        
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ {year} update completed successfully in {duration:.1f} seconds")
        logger.info(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error updating {year} populations:")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error updating {year} populations: {e}")
        return False

def main():
    """Run all historical population updates."""
    logger.info("🌍 STARTING COMPREHENSIVE HISTORICAL POPULATION UPDATE")
    logger.info("=" * 70)
    
    # List of scripts to run in order (oldest to newest)
    updates = [
        ("update_2020_populations.py", "2020"),
        ("update_2021_populations.py", "2021"),
        ("update_2022_populations.py", "2022"),
        ("update_2023_populations.py", "2023")
    ]
    
    successful_updates = 0
    total_updates = len(updates)
    overall_start_time = time.time()
    
    for script_name, year in updates:
        success = run_script(script_name, year)
        if success:
            successful_updates += 1
        else:
            logger.warning(f"⚠️  {year} update failed, but continuing with remaining years...")
        
        # Add a small delay between updates
        time.sleep(1)
    
    overall_end_time = time.time()
    total_duration = overall_end_time - overall_start_time
    
    # Final summary
    logger.info("=" * 70)
    logger.info("📊 HISTORICAL POPULATION UPDATE SUMMARY")
    logger.info(f"Total updates attempted: {total_updates}")
    logger.info(f"Successful updates: {successful_updates}")
    logger.info(f"Failed updates: {total_updates - successful_updates}")
    logger.info(f"Total processing time: {total_duration:.1f} seconds")
    
    if successful_updates == total_updates:
        logger.info("🎉 ALL HISTORICAL POPULATION UPDATES COMPLETED SUCCESSFULLY!")
        logger.info("Your temporal database now has comprehensive CIA World Factbook population data for 2020-2025")
    else:
        logger.warning(f"⚠️  {total_updates - successful_updates} updates failed. Please check the logs above.")
    
    # Now run a final verification
    logger.info("\n🔍 Running final verification...")
    try:
        result = subprocess.run([sys.executable, "check_temporal_populations.py"], 
                              capture_output=True, text=True, check=True)
        logger.info("Final database status:")
        logger.info(result.stdout)
    except Exception as e:
        logger.warning(f"Could not run final verification: {e}")

if __name__ == "__main__":
    main() 