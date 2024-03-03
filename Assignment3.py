import redis
import json
import requests
import matplotlib.pyplot as plt

class DataProcessor:
    """
    Class for processing JSON data
    """

    def __init__(self, api_url, redis_host, redis_port, redis_password=None):
        """
        Initialize the DataProcessor
        """
        self.api_url = api_url
        self.redis_client = redis.StrictRedis(
            host=redis_host, port=redis_port, password=redis_password
        )

    def fetch_data_from_api(self):
        """
        Fetch JSON data from the API
        """
        response = requests.get(self.api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data from the API.")
            return None

    def insert_into_redis(self, data):
        """
        Insert JSON data into Redis
        """
        json_data = json.dumps(data)
        self.redis_client.set("data", json_data)

    def generate_bar_chart(self):
        """
        Generate a bar chart based on the number of likes for each track
        """
        json_data = self.redis_client.get("data")
        if json_data:
            data = json.loads(json_data)
            track_names = [track['name'] for track in data['tracks']]
            likes = [track['nbL'] for track in data['tracks']]
            plt.bar(track_names, likes)
            plt.xlabel('Track Name')
            plt.ylabel('Number of Likes')
            plt.title('Likes Distribution')
            plt.xticks(rotation=90)
            plt.show()
        else:
            print("No JSON data found in Redis.")

    def aggregate_likes(self):
        """
        Aggregate the total number of likes for all tracks
        """
        json_data = self.redis_client.get("data")
        if json_data:
            data = json.loads(json_data)
            total_likes = sum(track['nbL'] for track in data['tracks'])
            return total_likes
        else:
            print("No JSON data found in Redis.")
            return 0

    def search_track_by_name(self, track_name):
        """
        Search for a track by name
        """
        json_data = self.redis_client.get("data")
        if json_data:
            data = json.loads(json_data)
            matching_tracks = [track for track in data['tracks'] if track['name'].lower() == track_name.lower()]
            return matching_tracks
        else:
            print("No JSON data found in Redis.")
            return []

def main():
    """
    Main function
    """
    # Define constants
    API_URL = "https://openwhyd.org/hot/electro?format=json"
    REDIS_HOST = "http://redis-10779.c326.us-east-1-3.ec2.cloud.redislabs.com"
    REDIS_PORT = 10779
    REDIS_PASSWORD = "cE34Xqnjx60NVXRtIS47bxyUwgwxOEee"

    # Initialize DataProcessor
    processor = DataProcessor(API_URL, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

    # Fetch data from API
    data = processor.fetch_data_from_api()

    # Insert data into Redis
    if data:
        processor.insert_into_redis(data)

    # Generate bar chart
    processor.generate_bar_chart()

    # Aggregate likes
    total_likes = processor.aggregate_likes()
    print(f"Total number of likes for all tracks: {total_likes}")

    # Search for a track by name
    track_name = "Octave Noire - Les Airs Digitaux "
    matching_tracks = processor.search_track_by_name(track_name)
    if matching_tracks:
        print(f"Found tracks with name '{track_name}':")
        for track in matching_tracks:
            print(track)
    else:
        print(f"No tracks found with name '{track_name}'.")

if __name__ == "__main__":
    main()
