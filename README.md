# RunPod Serverless Speedtest Worker

![Banner](resources/Banner.png)

This project allows users to install Speedtest, a bandwidth tool that can inspect a RunPod region's network.

## Docker image

Docker image available at: [Docker Hub](https://hub.docker.com/r/drvpn/runpod_serverless_speedtest_worker)

## Required Environment Variables

To run this application on RunPod serverless, you need to set the following environment variables:

- `BUCKET_ENDPOINT_URL`: The endpoint URL of your S3-compatible storage.
- `BUCKET_ACCESS_KEY_ID`: The access key ID for your S3-compatible storage.
- `BUCKET_SECRET_ACCESS_KEY`: The secret access key for your S3-compatible storage.

These variables are required to store and host the JSON data and the upload and download graphs (PNG)

- `DURATION`: The amount of time in minutes you want the test to run.  The default is `5`.
- `REGION`: The name of the region, ie: `EU-RO-1`.  The default is `NO REGION SET`

## Running on RunPod Serverless

### 1. `Clone the Repository`

```sh
git clone https://github.com/drvpn/runpod_serverless_speedtest_worker.git
cd runpod_serverless_speedtest_worker
```

2. `Build and Push Docker Image`
   - Follow RunPod's documentation to build and push your Docker image to a container registry.

3. `Deploy on RunPod`
   - Go to RunPod's dashboard and create a new serverless endpoint.
   - Use the Docker image you pushed to your container registry.
   - Set the environment variables: `BUCKET_ENDPOINT_URL`, `BUCKET_ACCESS_KEY_ID`, `BUCKET_SECRET_ACCESS_KEY`, `REGION`

4. `Invoke the endpoint`

Speedtest doesn't require any input, but RunPod considers it an error to provide no input, so pass in at least 1 input Here is an example:

```sh
{
  "input": { "run": "yes"}
}
```


Use RunPod's interface or an HTTPS client (i.e. Postman) to send this payload to the deployed function.

# Input
- `provide at least 1 input`: Speedtest doesn't require any input, but RunPod considers it an error to provide no input, use `{ "input": { "run": "yes" } }`

## Example return value
```sh
{
  "delayTime": 5571,
  "executionTime": 318607,
  "id": "your-unique-id-will-be-here",
  "output": {
    "avg_download_speed": 104.35,
    "avg_upload_speed": 38.21,
    "best_server": {
      "cc": "US",
      "country": "United States",
      "d": 6882.352930477993,
      "host": "ookla2.eaglecable.net:8080",
      "id": "31889",
      "lat": "38.9172",
      "latency": 78.37,
      "lon": "-97.2139",
      "name": "Abilene, KS",
      "sponsor": "Vyve Broadband",
      "url": "http://ookla2.eaglecable.net:8080/speedtest/upload.php"
    },
    "ping_image_url": "https://mybucket.nyc3.digitaloceanspaces.com/Speedtest/EU-RO-1_speed_test_ping_20240617_003042.png",
    "results_url": "https://mybucket.nyc3.digitaloceanspaces.com/Speedtest/EU-RO-1_speed_test_results_20240617_003042.json",
    "speed_image_url": "https://mybucket.nyc3.digitaloceanspaces.com/Speedtest/EU-RO-1_speed_test_speed_20240617_003042.png"
  },
  "status": "COMPLETED"
}
```

# Handler Explanation

The `handler.py` script orchestrates the following tasks:

- Performs a speed test for the specified time period(default is 5 minutes)
- Uploads the generated JSON data file, graph images of download, upload, and ping speeds to S3-compatible storage and returns the public URLs.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

