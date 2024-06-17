'''
The MIT License (MIT)
Copyright © 2024 Dominic Powers

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import warnings

''' Suppress all warnings (FOR PRODUCTION) '''
warnings.filterwarnings('ignore')

import runpod
import speedtest
from datetime import datetime
import os
import sys
import time
import json
import matplotlib.pyplot as plt
import numpy as np

from utils.file_utils import upload_to_s3

duration = int(os.getenv('DURATION', 5))

def perform_speed_test(duration_minutes=duration):
    try:
        region  = os.getenv('REGION', 'REGION NOT SET')

        print(f'[Speedtest]: Starting test on RunPod Region {region}')
        # Initialize speedtest
        st = speedtest.Speedtest()

        # Print server list for debug purposes
        servers = st.get_servers()
        best_server = st.get_best_server()

        print(f'[Speedtest]: Selected server for test: {best_server}')

        start_time = time.time()
        end_time = start_time + duration_minutes * 60
        results = []

        while time.time() < end_time:
            # Perform download and upload speed tests
            download_speed = st.download() / 10_000_000  # Convert to Mbps
            upload_speed = st.upload() / 10_000_000      # Convert to Mbps
            ping = st.results.ping
            
            print(f'[Speedtest][testing]: {region} | {ping} ms | Download {download_speed:.2f} Mbps | Upload {upload_speed:.2f} Mbps')

            # Record the results
            result = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
                'download_speed_mbps': download_speed,
                'upload_speed_mbps': upload_speed,
                'ping_ms': ping
            }
            results.append(result)

            # Wait for a bit before the next test
            time.sleep(10)  # Adjust the interval as needed


        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')

        # Save results to a JSON file
        results_path = f'{region}_speed_test_results_{timestamp}.json'

        with open(results_path, 'w') as f:
            json.dump(results, f, indent=4)

        # Create and save the plots
        #timestamps = [res['timestamp'] for res in results]
        timestamps = [datetime.strptime(res['timestamp'], '%Y-%m-%d %H:%M:%S') for res in results]

        download_speeds = [res['download_speed_mbps'] for res in results]
        upload_speeds = [res['upload_speed_mbps'] for res in results]
        pings = [res['ping_ms'] for res in results]

        # Calculate averages
        avg_download_speed = np.mean(download_speeds)
        avg_upload_speed = np.mean(upload_speeds)

        # Plot for Download and Upload Speeds
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, download_speeds, label='Download Speed (Mbps)', marker='o')
        plt.plot(timestamps, upload_speeds, label='Upload Speed (Mbps)', marker='o')
        plt.axhline(y=avg_download_speed, color='b', linestyle='--', label=f'Avg Download Speed (Mbps)')
        plt.axhline(y=avg_upload_speed, color='g', linestyle='--', label=f'Avg Upload Speed (Mbps)')

        # Annotate average values near the middle of the plot
        mid_index = len(timestamps) // 2
        plt.text(timestamps[mid_index], avg_download_speed, f'{avg_download_speed:.2f} Mbps', color='b', fontsize=10, verticalalignment='bottom')
        plt.text(timestamps[mid_index], avg_upload_speed, f'{avg_upload_speed:.2f} Mbps', color='g', fontsize=10, verticalalignment='bottom')

        # Annotate average values
        #plt.text(len(timestamps) - 1, avg_download_speed, f'{avg_download_speed:.2f} Mbps', color='b', fontsize=10, verticalalignment='bottom')
        #plt.text(len(timestamps) - 1, avg_upload_speed, f'{avg_upload_speed:.2f} Mbps', color='g', fontsize=10, verticalalignment='bottom')

        plt.xlabel('Timestamp')
        plt.ylabel('Speed (Mbps)')
        plt.title(f'{region} Download and Upload Speeds')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        speed_image_path = f'{region}_speed_test_speed_{timestamp}.png'
        plt.savefig(speed_image_path)
        plt.close()

        # Plot for Ping
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, pings, label='Ping (ms)', marker='o', color='red')
        plt.xlabel('Timestamp')
        plt.ylabel('Ping (ms)')
        plt.title('Ping')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        ping_image_path = f'{region}_speed_test_ping_{timestamp}.png'
        plt.savefig(ping_image_path)
        plt.close()

        bucket_name = 'Speedtest'

        speed_url, error = upload_to_s3(speed_image_path, bucket_name, speed_image_path)

        if error:
            print(f'[Speedtest][ERROR]: upload_to_s3 failed {error}')
            sys.exit(1)
        else:
            try:
                os.remove(speed_image_path)
            except:
                pass

        ping_url, error = upload_to_s3(ping_image_path, bucket_name, ping_image_path)

        if error:
            print(f'[Speedtest][ERROR]: upload_to_s3 failed {error}')
            sys.exit(1)
        else:
            try:
                os.remove(ping_image_path)
            except:
                pass


        results_url, error = upload_to_s3(results_path, bucket_name, results_path)

        if error:
            print(f'[Speedtest][ERROR]: upload_to_s3 failed {error}')
            sys.exit(1)
        else:
            try:
                os.remove(results_path)
            except:
                pass

        return float(format(avg_download_speed, '.2f')), float(format(avg_upload_speed, '.2f')), speed_url, ping_url, results_url, best_server, None

    except Exception as e:
        return None, None, None, None, None, None, e

''' Handler function that will be used to process jobs. '''
def handler(job):
    # perform test
    avg_download_speed, avg_upload_speed, speed_url, ping_url, results_url, best_server, error = perform_speed_test()

    if error:
        print(f'[Speedtest][ERROR]: perform_speed_test() failed with error: {error}')
        sys.exit(1)

    return {
        'avg_download_speed': avg_download_speed,
        'avg_upload_speed': avg_upload_speed,
        'results_url': results_url,
        'speed_image_url': speed_url,
        'ping_image_url': ping_url,
        'best_server': best_server
    }

if __name__ == '__main__':

    runpod.serverless.start({'handler': handler})
